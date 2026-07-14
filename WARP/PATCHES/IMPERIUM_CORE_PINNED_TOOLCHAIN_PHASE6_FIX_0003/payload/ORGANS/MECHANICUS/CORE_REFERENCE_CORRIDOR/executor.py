"""Typed default-deny process executor for the reference corridor."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import signal
import subprocess
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .pinned_tools import (
    GIT_HASH_ENV, GIT_PATH_ENV, PWSH_HASH_ENV, PWSH_PATH_ENV, REQUIRED_ENV, git_argv
)
from .registry import CapabilityRegistry, RegistryError, canonical_digest, sha256_file


EVIDENCE_SCHEMA = "imperium.core_reference_corridor.evidence_envelope.v0_1"
EXCLUDED_PARTS = {".git", "node_modules", "target", "dist", "__pycache__", ".pytest_cache"}


class ExecutionBlocked(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        git_argv("-C", str(root), *args),
        shell=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=15,
    )


def git_state(root: Path) -> dict[str, Any]:
    head = _run_git(root, "rev-parse", "HEAD")
    branch = _run_git(root, "rev-parse", "--abbrev-ref", "HEAD")
    status = _run_git(root, "status", "--porcelain=v1", "--untracked-files=all")
    diff = _run_git(root, "diff", "--binary", "--no-ext-diff", "HEAD")
    untracked = _run_git(root, "ls-files", "--others", "--exclude-standard", "-z")
    if any(item.returncode != 0 for item in (head, branch, status, diff, untracked)):
        raise ExecutionBlocked("GIT_STATE_UNAVAILABLE", str(root))
    untracked_hashes: dict[str, str] = {}
    for relative in filter(None, untracked.stdout.split("\0")):
        path = root / relative
        if path.is_file() and path.stat().st_size <= 32 * 1024 * 1024:
            untracked_hashes[relative.replace("\\", "/")] = sha256_file(path)
    fingerprint_value = {
        "head": head.stdout.strip(),
        "status": status.stdout.splitlines(),
        "diff_sha256": hashlib.sha256(diff.stdout.encode("utf-8")).hexdigest(),
        "untracked": untracked_hashes,
    }
    return {
        "root": str(root.resolve()),
        "head": head.stdout.strip(),
        "branch": branch.stdout.strip(),
        "porcelain": status.stdout.splitlines(),
        "dirty": bool(status.stdout),
        "diff_sha256": "sha256:" + fingerprint_value["diff_sha256"],
        "working_tree_hash": canonical_digest(fingerprint_value),
    }


def _path_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def _tree_snapshot(roots: Iterable[Path], max_files: int = 30000) -> dict[str, tuple[int, int]]:
    snapshot: dict[str, tuple[int, int]] = {}
    count = 0
    for root in roots:
        resolved = root.resolve()
        if not resolved.exists():
            continue
        if resolved.is_file():
            stat = resolved.stat()
            snapshot[str(resolved)] = (stat.st_size, stat.st_mtime_ns)
            continue
        for path in resolved.rglob("*"):
            relative_parts = path.relative_to(resolved).parts
            if any(part in EXCLUDED_PARTS for part in relative_parts):
                continue
            if path.is_file():
                stat = path.stat()
                snapshot[str(path.resolve())] = (stat.st_size, stat.st_mtime_ns)
                count += 1
                if count > max_files:
                    raise ExecutionBlocked("SNAPSHOT_FILE_LIMIT", f"more than {max_files} guarded files")
    return snapshot


def _snapshot_diff(before: dict[str, tuple[int, int]], after: dict[str, tuple[int, int]]) -> dict[str, list[str]]:
    before_keys, after_keys = set(before), set(after)
    return {
        "added": sorted(after_keys - before_keys),
        "removed": sorted(before_keys - after_keys),
        "modified": sorted(path for path in before_keys & after_keys if before[path] != after[path]),
    }


def _minimal_environment(worktree_root: Path) -> tuple[dict[str, str], dict[str, Any]]:
    allow = [
        "SystemRoot", "WINDIR", "PATH", "PATHEXT", "COMSPEC", "TEMP", "TMP",
        GIT_PATH_ENV, GIT_HASH_ENV, PWSH_PATH_ENV, PWSH_HASH_ENV, REQUIRED_ENV,
    ]
    env = {key: os.environ[key] for key in allow if key in os.environ}
    env.update(
        {
            "PYTHONUTF8": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "NO_COLOR": "1",
            "IMPERIUM_ACTIVE_WORKTREE": str(worktree_root),
        }
    )
    profile = {"profile_id": "CORE_MINIMAL_HOST_V0_1", "inherited_keys": sorted(key for key in allow if key in os.environ), "set_keys": sorted(set(env) - set(allow))}
    return env, profile


def _terminate_tree(process: subprocess.Popen[Any]) -> dict[str, Any]:
    if process.poll() is not None:
        return {"requested": False, "method": "process_already_exited", "tree_terminated": True}
    if os.name == "nt":
        result = subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            shell=False,
            capture_output=True,
            check=False,
            timeout=10,
        )
        process.wait(timeout=5)
        return {"requested": True, "method": "taskkill_pid_tree_force", "returncode": result.returncode, "tree_terminated": process.poll() is not None}
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait(timeout=5)
    return {"requested": True, "method": "killpg_sigkill", "tree_terminated": process.poll() is not None}


def _hash_stream(path: Path) -> str:
    return sha256_file(path)


def _read_bounded(path: Path, limit: int = 1024 * 1024) -> tuple[str, bool]:
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    truncated = len(data) > limit
    return data[:limit].decode("utf-8", errors="replace"), truncated


def _host_fingerprint() -> str:
    material = "|".join([platform.system(), platform.release(), platform.machine(), platform.node()])
    return "sha256:" + hashlib.sha256(material.encode("utf-8")).hexdigest()


def _envelope_digest(envelope: dict[str, Any]) -> str:
    clone = dict(envelope)
    clone.pop("envelope_digest", None)
    payload = json.dumps(clone, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_params(capability: dict[str, Any], params: dict[str, Any]) -> list[str]:
    schema = capability.get("parameter_schema", {"type": "object", "additionalProperties": False})
    properties = schema.get("properties", {})
    if schema.get("additionalProperties") is False:
        unknown = sorted(set(params) - set(properties))
        if unknown:
            raise ExecutionBlocked("PARAMETER_NOT_ALLOWED", ",".join(unknown))
    missing = sorted(set(schema.get("required", [])) - set(params))
    if missing:
        raise ExecutionBlocked("PARAMETER_REQUIRED", ",".join(missing))
    argv: list[str] = []
    bindings = capability.get("parameter_bindings", {})
    for key in sorted(params):
        value, rule = params[key], properties.get(key, {})
        expected = rule.get("type")
        if expected == "string" and not isinstance(value, str):
            raise ExecutionBlocked("PARAMETER_TYPE", key)
        if expected == "integer" and (not isinstance(value, int) or isinstance(value, bool)):
            raise ExecutionBlocked("PARAMETER_TYPE", key)
        if "enum" in rule and value not in rule["enum"]:
            raise ExecutionBlocked("PARAMETER_ENUM", key)
        flag = bindings.get(key)
        if not flag:
            raise ExecutionBlocked("PARAMETER_BINDING_MISSING", key)
        argv.extend([str(flag), str(value)])
    return argv


def execute_capability(
    *,
    registry: CapabilityRegistry,
    capability_id: str,
    operation: str,
    params: dict[str, Any],
    cwd: Path | str,
    task_state: dict[str, Any],
    reality_root: Path | str,
    worktree_root: Path | str,
    guard_roots: list[Path | str] | None = None,
    validator_ids: list[str] | None = None,
    organ_verdict_refs: list[str] | None = None,
    parent_evidence_ids: list[str] | None = None,
) -> dict[str, Any]:
    capability = registry.resolve(capability_id, operation)
    cwd_path, reality, worktree = Path(cwd).resolve(), Path(reality_root).resolve(), Path(worktree_root).resolve()
    base_head = task_state.get("base_head")
    if not base_head or git_state(reality)["head"] != base_head:
        raise ExecutionBlocked("STALE_BASE_HEAD", f"expected {base_head}")
    allowed_reads = [Path(path).resolve() for path in capability["allowed_read_roots"]]
    allowed_writes = [Path(path).resolve() for path in capability["allowed_write_roots"]]
    if not any(_path_within(cwd_path, root) for root in allowed_reads):
        raise ExecutionBlocked("CWD_OUTSIDE_READ_SCOPE", str(cwd_path))
    mutating = capability["actual_effect_class"] != "READ_ONLY"
    active_warp = Path(task_state.get("warp", {}).get("path", worktree)).resolve()
    if mutating and (not _path_within(cwd_path, active_warp) or active_warp == reality):
        raise ExecutionBlocked("MUTATION_OUTSIDE_ACTIVE_WARP", str(cwd_path))

    executable = Path(capability["executable_path"]).resolve()
    if sha256_file(executable) != capability["executable_sha256"]:
        raise ExecutionBlocked("EXECUTABLE_IDENTITY_MISMATCH", capability_id)
    exact_argv = [str(executable), *[str(item) for item in capability.get("fixed_argv", [])], *_validate_params(capability, params)]
    env, env_profile = _minimal_environment(worktree)
    roots = [Path(item).resolve() for item in (guard_roots or [reality, worktree])]
    pre_git = {"reality": git_state(reality), "worktree": git_state(worktree)}
    pre_fs = _tree_snapshot(roots)
    start_timestamp = utc_now()
    started = time.monotonic()
    timed_out = False
    termination = {"requested": False, "method": "normal_exit", "tree_terminated": True}

    with tempfile.TemporaryDirectory(prefix="imperium-core-exec-") as temp_dir:
        stdout_path, stderr_path = Path(temp_dir) / "stdout.bin", Path(temp_dir) / "stderr.bin"
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
        with stdout_path.open("wb") as stdout_stream, stderr_path.open("wb") as stderr_stream:
            process = subprocess.Popen(
                exact_argv,
                cwd=str(cwd_path),
                env=env,
                shell=False,
                stdin=subprocess.DEVNULL,
                stdout=stdout_stream,
                stderr=stderr_stream,
                creationflags=creationflags,
                start_new_session=os.name != "nt",
            )
            try:
                process.wait(timeout=float(capability["timeout_seconds"]))
            except subprocess.TimeoutExpired:
                timed_out = True
                termination = _terminate_tree(process)
        stdout_hash, stderr_hash = _hash_stream(stdout_path), _hash_stream(stderr_path)
        stdout, stdout_truncated = _read_bounded(stdout_path)
        stderr, stderr_truncated = _read_bounded(stderr_path)
        exit_code = process.returncode

    post_fs = _tree_snapshot(roots)
    post_git = {"reality": git_state(reality), "worktree": git_state(worktree)}
    fs_diff = _snapshot_diff(pre_fs, post_fs)
    changed_paths = fs_diff["added"] + fs_diff["removed"] + fs_diff["modified"]
    reasons: list[str] = []
    if timed_out:
        reasons.append("TIMEOUT")
    if exit_code != 0:
        reasons.append("PROCESS_EXIT_NONZERO")
    if pre_git["reality"] != post_git["reality"]:
        reasons.append("REALITY_WRITE_ATTEMPT")
    if capability["actual_effect_class"] == "READ_ONLY" and (pre_git["worktree"] != post_git["worktree"] or changed_paths):
        reasons.append("READ_ONLY_SIDE_EFFECT")
    unauthorized = [path for path in changed_paths if not any(_path_within(Path(path), root) for root in allowed_writes)]
    if mutating and unauthorized:
        reasons.append("UNAUTHORIZED_WRITE_PATH")
    parsed_result: Any = None
    if stdout.strip():
        try:
            parsed_result = json.loads(stdout)
        except json.JSONDecodeError:
            parsed_result = None
    if isinstance(parsed_result, dict) and str(parsed_result.get("verdict", "")).startswith("BLOCK"):
        reasons.append("CAPABILITY_REPORTED_BLOCK")

    end_timestamp = utc_now()
    event_id = "event-" + uuid.uuid4().hex
    evidence_id = "evidence-" + uuid.uuid4().hex
    envelope: dict[str, Any] = {
        "schema_version": EVIDENCE_SCHEMA,
        "evidence_id": evidence_id,
        "task_id": task_state.get("task_id"),
        "warp_id": task_state.get("warp", {}).get("warp_id"),
        "event_id": event_id,
        "base_head": base_head,
        "result_head_or_tree_hash": post_git["worktree"]["working_tree_hash"].removeprefix("sha256:"),
        "branch": post_git["worktree"]["branch"],
        "timestamp_utc": end_timestamp,
        "start_timestamp_utc": start_timestamp,
        "end_timestamp_utc": end_timestamp,
        "duration_ms": round((time.monotonic() - started) * 1000, 3),
        "host_fingerprint": _host_fingerprint(),
        "toolchain": {"python": platform.python_version(), "platform": platform.system()},
        "capability_id": capability_id,
        "operation": operation,
        "registry_digest": registry.data.get("registry_digest"),
        "exact_argv": exact_argv,
        "executable_path": str(executable),
        "executable_sha256": capability["executable_sha256"],
        "cwd": str(cwd_path),
        "environment_profile": env_profile,
        "input_hashes": {"adapter": capability.get("adapter_sha256", ""), "registry": str(registry.data.get("registry_digest", "")).removeprefix("sha256:")},
        "output_hashes": {"stdout": stdout_hash, "stderr": stderr_hash},
        "stdout_hash": stdout_hash,
        "stderr_hash": stderr_hash,
        "stdout_truncated": stdout_truncated,
        "stderr_truncated": stderr_truncated,
        "exit_code": exit_code,
        "timeout": capability["timeout_seconds"],
        "timeout_triggered": timed_out,
        "pre_git_state": pre_git,
        "post_git_state": post_git,
        "filesystem_diff": {**fs_diff, "unauthorized": unauthorized},
        "allowed_reads": [str(path) for path in allowed_reads],
        "allowed_writes": [str(path) for path in allowed_writes],
        "process_termination_result": termination,
        "validator_ids": validator_ids or [],
        "acceptance_results": [{"check": "typed_execution", "verdict": "PASS" if not reasons else "BLOCK", "reasons": reasons}],
        "organ_verdict_refs": organ_verdict_refs or [],
        "owner_decision_ref": task_state.get("owner_decisions", [])[-1].get("decision_id") if task_state.get("owner_decisions") else None,
        "parent_evidence_ids": parent_evidence_ids or [],
        "verdict": "PASS_PROVEN" if not reasons else "BLOCK",
        "block_reasons": reasons,
        "result": parsed_result,
        "stderr_preview": stderr[:4000],
    }
    envelope["envelope_digest"] = _envelope_digest(envelope)
    return envelope
