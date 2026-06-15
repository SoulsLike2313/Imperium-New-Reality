#!/usr/bin/env python3
"""Validate New Reality remote/tree/bundle closure evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


for candidate in Path(__file__).resolve().parents:
    if all((candidate / marker).is_file() for marker in ("EPOCH_MANIFEST.json", "NEW_REALITY_SCOPE_LOCK.md", "AGENTS.md")):
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
        tools_path = candidate / "ORGANS" / "ASTRONOMICON" / "TOOLS"
        if str(tools_path) not in sys.path:
            sys.path.insert(0, str(tools_path))
        break

from ORGAN_AGENT_COMMON.root_resolution import resolve_new_reality_root  # noqa: E402
from astronomicon_task_entry_lib_v0_1 import build_context, read_json, resolve_task_id  # noqa: E402


TASK_ID = "TASK-NEWGEN-PC-NEW-REALITY-REMOTE-TREE-BUNDLE-CLOSURE-VALIDATOR-PC-V0_1"
REPORT_REL = Path("REPORTS") / TASK_ID
REMOTE_URL = "https://github.com/SoulsLike2313/Imperium-New-Reality.git"
BRANCH = "master"
ANCIENT_ROOT = Path("E:/IMPERIUM")
ANCIENT_REFERENCE_URL = "https://github.com/SoulsLike2313/Imperium-"
ANCIENT_FREEZE_COMMIT = "448150be7b4984b755828bc2f89b5bd1156de37d"
BUNDLE_NAME = "task_report_bundle.zip"
SHA256SUMS_NAME = "sha256sums.txt"

REMOTE_TREE_RECEIPT = "remote_tree_bundle_closure_receipt.json"
NATIVE_REPLAY_RECEIPT = "native_registry_replay_receipt.json"
INVALID_RECHECK_RECEIPT = "invalid_taskpack_no_launch_recheck_receipt.json"
ANCIENT_GUARD_RECEIPT = "ancient_readonly_guard_receipt.json"
BUNDLE_CONTRACT_RECEIPT = "bundle_contract_receipt.json"
FINAL_REMOTE_CLOSURE_RECEIPT = "final_remote_closure_receipt.json"
VALIDATOR_STDOUT = "validator_run_stdout.txt"
RED_TEAM = "RED_TEAM_VERDICT.json"
CLAIM_LEDGER = "CLAIM_LEDGER.json"
CAPABILITY_SPLIT = "CAPABILITY_SPLIT_RECEIPT.json"
SELF_REFERENCE_NOTE = "SELF_REFERENCE_LIMIT.txt"

SELF_REFERENTIAL_REPORTS = {
    BUNDLE_NAME,
    SHA256SUMS_NAME,
    REMOTE_TREE_RECEIPT,
    BUNDLE_CONTRACT_RECEIPT,
    FINAL_REMOTE_CLOSURE_RECEIPT,
}

TEXT_SUFFIXES = {".json", ".md", ".txt", ".py"}
CYRILLIC_RE = re.compile(r"[\u0400-\u04ff]")
REPLACEMENT_RE = re.compile(r"\ufffd")
MOJIBAKE_PATTERNS = (
    re.compile(r"\u00c3[\u0080-\u00bf]"),
    re.compile(r"\u00c2[\u0080-\u00bf]"),
    re.compile(r"\u00e2\u0080[\u0098-\u009f]"),
    re.compile(r"[\u00d0\u00d1][\u0080-\u00bf]"),
)
GIT_HEAD_RE = re.compile(r"^[0-9a-f]{40}$")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def to_posix(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def run_command(command: list[str], cwd: Path, *, timeout: int = 120) -> dict[str, Any]:
    env = os.environ.copy()
    env.setdefault("GIT_TERMINAL_PROMPT", "0")
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "status": "PASS" if completed.returncode == 0 else "FAIL",
    }


def run_git(repo_root: Path, *args: str, timeout: int = 120) -> dict[str, Any]:
    return run_command(["git", *args], repo_root, timeout=timeout)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_under(root: Path, candidate: Path) -> bool:
    root_resolved = root.resolve()
    candidate_resolved = candidate.resolve()
    return candidate_resolved == root_resolved or root_resolved in candidate_resolved.parents


def reset_dir(path: Path, allowed_root: Path) -> None:
    resolved = path.resolve()
    if not is_under(allowed_root, resolved):
        raise RuntimeError(f"refusing to reset path outside allowed root: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True, exist_ok=True)


def parse_ls_remote_head(stdout: str, branch: str = BRANCH) -> str:
    wanted_ref = f"refs/heads/{branch}"
    for line in stdout.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1] == wanted_ref:
            return parts[0]
    return ""


def read_bytes_or_empty(path: Path) -> bytes:
    return path.read_bytes() if path.exists() else b""


def git_observation(repo_root: Path) -> dict[str, Any]:
    root_resolution = resolve_new_reality_root(repo_root)
    remote = run_git(repo_root, "remote", "get-url", "origin")
    branch = run_git(repo_root, "branch", "--show-current")
    local_head = run_git(repo_root, "rev-parse", "HEAD")
    local_head_type = run_git(repo_root, "cat-file", "-t", "HEAD")
    origin_master = run_git(repo_root, "rev-parse", "--verify", f"origin/{BRANCH}")
    status_short = run_git(repo_root, "status", "--short")
    status_short_branch = run_git(repo_root, "status", "--short", "--branch")
    ls_remote = run_git(repo_root, "ls-remote", "origin", f"refs/heads/{BRANCH}", timeout=120)

    local_head_value = local_head.get("stdout", "")
    origin_master_value = origin_master.get("stdout", "")
    ls_remote_value = parse_ls_remote_head(ls_remote.get("stdout", ""))
    return {
        "timestamp_utc": utc_now(),
        "active_root": to_posix(root_resolution.active_root),
        "root_resolution": root_resolution.to_receipt(),
        "remote_url": remote.get("stdout", ""),
        "remote_url_exact": remote.get("stdout", "") == REMOTE_URL,
        "branch": branch.get("stdout", ""),
        "branch_exact": branch.get("stdout", "") == BRANCH,
        "local_head": local_head_value,
        "local_head_is_commit": bool(GIT_HEAD_RE.fullmatch(local_head_value))
        and local_head_type.get("stdout", "") == "commit",
        "origin_master": origin_master_value,
        "origin_master_resolves": bool(GIT_HEAD_RE.fullmatch(origin_master_value)),
        "ls_remote_master": ls_remote_value,
        "ls_remote_resolves": bool(GIT_HEAD_RE.fullmatch(ls_remote_value)),
        "head_equals_origin_master": bool(local_head_value and local_head_value == origin_master_value),
        "ls_remote_equals_local_head": bool(local_head_value and local_head_value == ls_remote_value),
        "ls_remote_equals_origin_master": bool(origin_master_value and origin_master_value == ls_remote_value),
        "status_short": status_short.get("stdout", ""),
        "status_short_branch": status_short_branch.get("stdout", ""),
        "status_short_branch_lines": status_short_branch.get("stdout", "").splitlines()
        if status_short_branch.get("stdout")
        else [],
        "worktree_clean": status_short.get("stdout", "") == "",
        "commands": {
            "remote": remote,
            "branch": branch,
            "local_head": local_head,
            "local_head_type": local_head_type,
            "origin_master": origin_master,
            "status_short": status_short,
            "status_short_branch": status_short_branch,
            "ls_remote": ls_remote,
        },
    }


def ancient_snapshot() -> dict[str, Any]:
    if not ANCIENT_ROOT.exists():
        return {
            "exists": False,
            "root": to_posix(ANCIENT_ROOT),
            "head": "",
            "branch": "",
            "status_short_branch": [],
            "remote_url": "",
            "note": "Ancient Empire root is not present on this machine.",
        }
    head = run_git(ANCIENT_ROOT, "rev-parse", "HEAD")
    branch = run_git(ANCIENT_ROOT, "branch", "--show-current")
    status = run_git(ANCIENT_ROOT, "status", "--short", "--branch")
    remote = run_git(ANCIENT_ROOT, "remote", "get-url", "origin")
    return {
        "exists": True,
        "root": to_posix(ANCIENT_ROOT),
        "head": head.get("stdout", ""),
        "branch": branch.get("stdout", ""),
        "status_short_branch": status.get("stdout", "").splitlines() if status.get("stdout") else [],
        "remote_url": remote.get("stdout", ""),
        "commands": {
            "head": head,
            "branch": branch,
            "status": status,
            "remote": remote,
        },
    }


def build_ancient_guard(report_dir: Path, before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    unchanged = (
        before.get("exists") == after.get("exists")
        and before.get("head") == after.get("head")
        and before.get("branch") == after.get("branch")
        and before.get("status_short_branch") == after.get("status_short_branch")
        and before.get("remote_url") == after.get("remote_url")
    )
    receipt = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "receipt_type": "ancient_readonly_guard_receipt",
        "ancient_root": to_posix(ANCIENT_ROOT),
        "ancient_reference_url": ANCIENT_REFERENCE_URL,
        "ancient_freeze_commit": ANCIENT_FREEZE_COMMIT,
        "access_mode": "READ_ONLY_PROBE_AUTHORIZED_BY_TASKPACK",
        "write_operations_performed": False,
        "ancient_empire_mutated": not unchanged,
        "before": before,
        "after": after,
        "verdict": "PASS" if unchanged else "BLOCK",
    }
    write_json(report_dir / ANCIENT_GUARD_RECEIPT, receipt)
    return receipt


def build_native_registry_replay(repo_root: Path, report_dir: Path) -> dict[str, Any]:
    ctx = build_context(repo_root)
    raw_resolver_path = report_dir / "native_registry_resolver_raw_receipt.json"
    resolver = resolve_task_id(
        repo_root=repo_root,
        task_id=TASK_ID,
        actor="validate_remote_tree_bundle_closure_v0_1.py:native_registry_replay",
        write_receipt=True,
        receipt_output_path=raw_resolver_path,
    )
    admission_path = Path(str(resolver.get("admission_receipt_path", "")))
    admission: dict[str, Any] = {}
    if admission_path.exists():
        admission = read_json(admission_path)
    registered_path = Path(str(resolver.get("registered_task_path", ""))) if resolver.get("registered_task_path") else Path()
    native_path_ok = bool(registered_path) and is_under(ctx["registered_root"], registered_path)
    resolver_pass = resolver.get("resolver_verdict") in {"PASS", "PASS_WITH_WARNINGS"}
    admission_pass = str(admission.get("admission_verdict", "")).startswith("ADMISSION_PASS")
    receipt = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "receipt_type": "native_registry_replay_receipt",
        "new_reality_native_astronomicon_used": True,
        "ancient_bridge_used": False,
        "replay_mode": "RESOLVE_EXISTING_REGISTERED_TASK",
        "task_registry_path": to_posix(ctx["task_registry"]),
        "current_expected_path": to_posix(ctx["current_expected"]),
        "registered_task_path": resolver.get("registered_task_path", ""),
        "route_manifest_path": resolver.get("route_manifest_path", ""),
        "admission_receipt_path": resolver.get("admission_receipt_path", ""),
        "raw_resolver_receipt_path": to_posix(raw_resolver_path),
        "admission_verdict": admission.get("admission_verdict", ""),
        "resolver_verdict": resolver.get("resolver_verdict", ""),
        "native_registered_path_under_new_reality": native_path_ok,
        "caps_triggered": resolver.get("caps_triggered", []),
        "warnings": resolver.get("warnings", []),
        "verdict": "PASS" if resolver_pass and admission_pass and native_path_ok else "BLOCK",
    }
    write_json(report_dir / NATIVE_REPLAY_RECEIPT, receipt)
    return receipt


def make_invalid_taskpack(report_dir: Path) -> Path:
    fixture_root = report_dir / "fixtures" / "invalid_taskpack_no_manifest"
    source_dir = fixture_root / "source"
    reset_dir(source_dir, report_dir)
    write_text(source_dir / "TASK_SPEC.md", "# Invalid Fixture\n\nThis fixture intentionally omits MANIFEST.json.")
    zip_path = fixture_root / "invalid_taskpack_no_manifest.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(source_dir / "TASK_SPEC.md", "TASK_SPEC.md")
    return zip_path


def parse_json_stdout(stdout: str) -> dict[str, Any]:
    try:
        payload = json.loads(stdout)
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def build_invalid_recheck(repo_root: Path, report_dir: Path) -> dict[str, Any]:
    ctx = build_context(repo_root)
    invalid_zip = make_invalid_taskpack(report_dir)
    before_current = read_bytes_or_empty(ctx["current_expected"])
    before_registry = read_bytes_or_empty(ctx["task_registry"])
    intake_script = repo_root / "ORGANS" / "ASTRONOMICON" / "TOOLS" / "astronomicon_taskpack_intake_v0_1.py"
    result = run_command(
        [
            sys.executable,
            str(intake_script),
            "--zip-path",
            str(invalid_zip),
            "--repo-root",
            str(repo_root),
            "--actor",
            "validate_remote_tree_bundle_closure_v0_1.py:invalid_recheck",
        ],
        repo_root,
        timeout=120,
    )
    after_current = read_bytes_or_empty(ctx["current_expected"])
    after_registry = read_bytes_or_empty(ctx["task_registry"])
    payload = parse_json_stdout(result.get("stdout", ""))
    stdout_lower = result.get("stdout", "").lower()
    launch_phrase = "launch card" in stdout_lower
    start_phrase = "start task" in stdout_lower
    launch_card_emitted = bool(
        payload.get("registered_task_path")
        or payload.get("route_manifest_path")
        or payload.get("task_start_ack")
        or launch_phrase
    )
    start_task_emitted = bool(payload.get("owner_instruction_ru") or start_phrase)
    current_expected_changed = before_current != after_current
    registry_changed = before_registry != after_registry
    blocked = payload.get("admission_verdict") == "ADMISSION_BLOCK"
    receipt = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "receipt_type": "invalid_taskpack_no_launch_recheck_receipt",
        "invalid_fixture_path": to_posix(invalid_zip),
        "expected_verdict": "ADMISSION_BLOCK_NO_LAUNCH",
        "command": result.get("command", []),
        "returncode": result.get("returncode"),
        "stdout_path": "validator_run_stdout.txt",
        "admission_verdict": payload.get("admission_verdict", ""),
        "launch_card_emitted": launch_card_emitted,
        "start_task_emitted": start_task_emitted,
        "stdout_contains_launch_card_phrase": launch_phrase,
        "stdout_contains_start_task_phrase": start_phrase,
        "current_expected_changed_on_block": current_expected_changed,
        "task_registry_changed_on_block": registry_changed,
        "caps_triggered": payload.get("caps_triggered", []),
        "warnings": payload.get("warnings", []),
        "raw_intake_result": result,
        "verdict": "PASS"
        if blocked and not launch_card_emitted and not start_task_emitted and not current_expected_changed and not registry_changed
        else "BLOCK",
    }
    write_json(report_dir / INVALID_RECHECK_RECEIPT, receipt)
    return receipt


def component_verdict(value: dict[str, Any]) -> str:
    return str(value.get("verdict", "UNKNOWN"))


def build_capability_split(report_dir: Path) -> dict[str, Any]:
    payload = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "LOCAL_SCRIPT_FIRST": [
            "TOOLS/NEW_REALITY_VALIDATORS/validate_remote_tree_bundle_closure_v0_1.py --phase prepare",
            "TOOLS/NEW_REALITY_VALIDATORS/validate_remote_tree_bundle_closure_v0_1.py --phase finalize",
            "TOOLS/NEW_REALITY_VALIDATORS/validate_remote_tree_bundle_closure_v0_1.py --phase verify",
            "ORGANS/ASTRONOMICON/TOOLS/astronomicon_task_id_resolver_v0_1.py",
            "ORGANS/ASTRONOMICON/TOOLS/astronomicon_taskpack_intake_v0_1.py",
        ],
        "LOCAL_MANUAL_COMMAND": [
            "git status --short --branch",
            "git add",
            "git commit",
            "git push origin master",
            "git ls-remote origin refs/heads/master",
        ],
        "CANDIDATE_SCRIPT_FIRST": [],
        "AGENT_REASONING_ONLY": [
            "A committed receipt cannot contain the hash of the future commit that will contain that receipt.",
        ],
        "EXTERNAL_RESEARCH": [],
        "OWNER_MANUAL_CONFIRMATION": [
            "Taskpack authorizes the New Reality remote URL and master branch for this closure task.",
        ],
        "FUTURE_CAPABILITY_GAP": [
            "Browser-level GitHub UI visibility is optional and not claimed by this validator.",
        ],
        "verdict": "PASS",
    }
    write_json(report_dir / CAPABILITY_SPLIT, payload)
    return payload


def build_claim_ledger(report_dir: Path, components: dict[str, str]) -> dict[str, Any]:
    claims = [
        ("C001", "Active root is New Reality.", REMOTE_TREE_RECEIPT, components.get("remote_tree", "PENDING")),
        ("C002", "Origin remote URL is the authorized New Reality remote.", REMOTE_TREE_RECEIPT, components.get("remote_tree", "PENDING")),
        ("C003", "Native Astronomicon registry replay resolves this task without Ancient bridge.", NATIVE_REPLAY_RECEIPT, components.get("native", "PENDING")),
        ("C004", "Invalid taskpack blocks without launch card or start-task emission.", INVALID_RECHECK_RECEIPT, components.get("invalid", "PENDING")),
        ("C005", "Ancient Empire was not mutated by this task.", ANCIENT_GUARD_RECEIPT, components.get("ancient", "PENDING")),
        ("C006", "Report bundle exists and its SHA256 is recorded in sha256sums.txt.", BUNDLE_CONTRACT_RECEIPT, components.get("bundle", "PENDING")),
        ("C007", "Machine artifacts are UTF-8, no-BOM, and do not contain Cyrillic machine text.", RED_TEAM, components.get("encoding", "PENDING")),
        ("C008", "Final git equality proof is by git commands, not browser assumption.", FINAL_REMOTE_CLOSURE_RECEIPT, components.get("remote_tree", "PENDING")),
    ]
    payload = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "claims": [
            {
                "claim_id": claim_id,
                "claim": claim,
                "evidence": evidence,
                "verdict": verdict,
            }
            for claim_id, claim, evidence, verdict in claims
        ],
        "verdict": "BLOCK" if any(value == "BLOCK" for value in components.values()) else "PASS_WITH_SELF_REFERENCE_LIMIT",
    }
    write_json(report_dir / CLAIM_LEDGER, payload)
    return payload


def decode_text_file(path: Path) -> tuple[str | None, str | None]:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        return None, "UTF-8 BOM detected."
    try:
        return raw.decode("utf-8"), None
    except UnicodeDecodeError as exc:
        return None, f"UTF-8 decode error: {exc}"


def check_text_for_language(path_label: str, text: str) -> list[str]:
    issues: list[str] = []
    if CYRILLIC_RE.search(text):
        issues.append(f"Cyrillic text detected in machine artifact: {path_label}")
    if REPLACEMENT_RE.search(text):
        issues.append(f"Replacement character detected in machine artifact: {path_label}")
    for pattern in MOJIBAKE_PATTERNS:
        if pattern.search(text):
            issues.append(f"Mojibake signature detected in machine artifact: {path_label}")
            break
    return issues


def validate_encoding_for_paths(paths: list[Path], repo_root: Path) -> dict[str, Any]:
    issues: list[str] = []
    checked: list[str] = []
    for path in sorted(paths):
        if not path.exists() or not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text, error = decode_text_file(path)
        label = to_posix(path.relative_to(repo_root)) if is_under(repo_root, path) else to_posix(path)
        checked.append(label)
        if error:
            issues.append(f"{label}: {error}")
            continue
        assert text is not None
        issues.extend(check_text_for_language(label, text))
    return {
        "checked_file_count": len(checked),
        "checked_files": checked,
        "issues": issues,
        "verdict": "PASS" if not issues else "BLOCK",
    }


def validate_bundle_encoding(bundle_path: Path) -> dict[str, Any]:
    issues: list[str] = []
    checked: list[str] = []
    if not bundle_path.exists():
        return {"checked_file_count": 0, "checked_files": [], "issues": ["Bundle missing."], "verdict": "BLOCK"}
    with zipfile.ZipFile(bundle_path, "r") as archive:
        for name in sorted(archive.namelist()):
            if Path(name).suffix.lower() not in TEXT_SUFFIXES:
                continue
            raw = archive.read(name)
            checked.append(name)
            if raw.startswith(b"\xef\xbb\xbf"):
                issues.append(f"{name}: UTF-8 BOM detected.")
                continue
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                issues.append(f"{name}: UTF-8 decode error: {exc}")
                continue
            issues.extend(check_text_for_language(name, text))
    return {
        "checked_file_count": len(checked),
        "checked_files": checked,
        "issues": issues,
        "verdict": "PASS" if not issues else "BLOCK",
    }


def build_red_team(report_dir: Path, components: dict[str, str], encoding: dict[str, Any]) -> dict[str, Any]:
    hard_block = any(value == "BLOCK" for value in components.values()) or encoding.get("verdict") == "BLOCK"
    payload = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "mode": "HARD_RED_TEAM",
        "checks": {
            "remote_tree_bundle_closure": components.get("remote_tree", "PENDING"),
            "native_registry_replay": components.get("native", "PENDING"),
            "invalid_taskpack_no_launch": components.get("invalid", "PENDING"),
            "ancient_readonly_guard": components.get("ancient", "PENDING"),
            "bundle_contract": components.get("bundle", "PENDING"),
            "machine_artifact_encoding": encoding.get("verdict", "UNKNOWN"),
            "browser_github_visibility": "NOT_CLAIMED",
            "git_self_reference_limit": "WARN_DISCLOSED",
        },
        "encoding_issues": encoding.get("issues", []),
        "surviving_warnings": [
            "Final committed receipt has an accepted git self-reference limit.",
            "Browser-level GitHub UI visibility was not checked and is not claimed.",
        ],
        "verdict": "BLOCK" if hard_block else "PASS_WITH_SELF_REFERENCE_LIMIT",
    }
    write_json(report_dir / RED_TEAM, payload)
    return payload


def write_self_reference_note(report_dir: Path) -> Path:
    path = report_dir / SELF_REFERENCE_NOTE
    write_text(
        path,
        "\n".join(
            [
                "# Self Reference Limit",
                "",
                "This bundle intentionally records the accepted git self-reference limit.",
                "A committed receipt cannot know the commit hash of the future commit that will contain that same receipt.",
                "Final remote equality must be verified by a no-write post-push validator run.",
            ]
        ),
    )
    return path


def bundle_source_paths(repo_root: Path, report_dir: Path) -> list[Path]:
    paths: list[Path] = []
    for path in sorted(report_dir.rglob("*")):
        if not path.is_file():
            continue
        rel_name = path.relative_to(report_dir).as_posix()
        if path.name in SELF_REFERENTIAL_REPORTS:
            continue
        if "/__pycache__/" in rel_name or rel_name.endswith(".pyc"):
            continue
        paths.append(path)
    repo_artifacts = [
        repo_root / "TOOLS" / "NEW_REALITY_VALIDATORS" / "validate_remote_tree_bundle_closure_v0_1.py",
        repo_root / "SCHEMAS" / "remote_tree_bundle_closure_receipt.schema.json",
        repo_root / "DOCS" / "NEW_REALITY_REMOTE_TREE_BUNDLE_CLOSURE_VALIDATOR_V0_1.md",
    ]
    paths.extend(path for path in repo_artifacts if path.exists())
    return sorted(dict.fromkeys(paths))


def archive_name(repo_root: Path, report_dir: Path, path: Path) -> str:
    if is_under(report_dir, path):
        return path.relative_to(report_dir).as_posix()
    return path.relative_to(repo_root).as_posix()


def build_bundle(repo_root: Path, report_dir: Path) -> dict[str, Any]:
    write_self_reference_note(report_dir)
    bundle_path = report_dir / BUNDLE_NAME
    if bundle_path.exists():
        bundle_path.unlink()
    paths = bundle_source_paths(repo_root, report_dir)
    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in paths:
            archive.write(path, archive_name(repo_root, report_dir, path))
    with zipfile.ZipFile(bundle_path, "r") as archive:
        names = sorted(archive.namelist())
    bundle_hash = sha256_file(bundle_path)
    contains_final = FINAL_REMOTE_CLOSURE_RECEIPT in names
    records_limit = SELF_REFERENCE_NOTE in names
    return {
        "bundle_path": to_posix(bundle_path),
        "bundle_sha256": bundle_hash,
        "bundle_size_bytes": bundle_path.stat().st_size,
        "included_file_count": len(names),
        "included_files": names,
        "bundle_contains_final_closure_receipt": contains_final,
        "bundle_records_self_reference_limit": records_limit,
        "excluded_from_bundle_due_self_reference": sorted(SELF_REFERENTIAL_REPORTS),
    }


def write_sha256sums(repo_root: Path, report_dir: Path) -> dict[str, Any]:
    paths = sorted(path for path in report_dir.rglob("*") if path.is_file() and path.name != SHA256SUMS_NAME)
    lines = []
    for path in paths:
        rel = path.relative_to(report_dir).as_posix()
        lines.append(f"{sha256_file(path)}  {rel}")
    write_text(report_dir / SHA256SUMS_NAME, "\n".join(lines))
    bundle_hash = sha256_file(report_dir / BUNDLE_NAME) if (report_dir / BUNDLE_NAME).exists() else ""
    bundle_recorded = any(line.endswith(f"  {BUNDLE_NAME}") and line.startswith(bundle_hash) for line in lines)
    return {
        "sha256sums_path": to_posix(report_dir / SHA256SUMS_NAME),
        "line_count": len(lines),
        "bundle_sha256": bundle_hash,
        "bundle_hash_recorded": bundle_recorded,
        "verdict": "PASS" if bundle_hash and bundle_recorded else "BLOCK",
    }


def read_sha256sums(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not path.exists():
        return result
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        result[parts[1].strip()] = parts[0].strip()
    return result


def build_bundle_contract(report_dir: Path, bundle: dict[str, Any], sha_report: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "receipt_type": "bundle_contract_receipt",
        "bundle_path": bundle.get("bundle_path", ""),
        "bundle_sha256": bundle.get("bundle_sha256", ""),
        "sha256sums_path": sha_report.get("sha256sums_path", ""),
        "sha256sums_records_bundle_sha256": sha_report.get("bundle_hash_recorded", False),
        "bundle_contains_final_closure_receipt": bundle.get("bundle_contains_final_closure_receipt", False),
        "bundle_records_self_reference_limit": bundle.get("bundle_records_self_reference_limit", False),
        "included_file_count": bundle.get("included_file_count", 0),
        "included_files": bundle.get("included_files", []),
        "excluded_from_bundle_due_self_reference": bundle.get("excluded_from_bundle_due_self_reference", []),
        "verdict": "PASS_WITH_SELF_REFERENCE_LIMIT"
        if sha_report.get("verdict") == "PASS"
        and (
            bundle.get("bundle_contains_final_closure_receipt")
            or bundle.get("bundle_records_self_reference_limit")
        )
        else "BLOCK",
    }
    write_json(report_dir / BUNDLE_CONTRACT_RECEIPT, payload)
    return payload


def build_remote_tree_receipt(
    report_dir: Path,
    observation: dict[str, Any],
    bundle: dict[str, Any],
    sha_report: dict[str, Any],
    components: dict[str, str],
    encoding: dict[str, Any],
    *,
    allow_dirty_worktree: bool = False,
) -> dict[str, Any]:
    all_core = [
        observation.get("active_root") == "E:/IMPERIUM_NEW_GENERATION_NEW_REALITY",
        observation.get("remote_url_exact"),
        observation.get("branch_exact"),
        observation.get("local_head_is_commit"),
        observation.get("origin_master_resolves"),
        observation.get("head_equals_origin_master"),
        observation.get("ls_remote_equals_local_head"),
        observation.get("ls_remote_equals_origin_master"),
        observation.get("worktree_clean") or allow_dirty_worktree,
        Path(str(bundle.get("bundle_path", ""))).exists(),
        sha_report.get("bundle_hash_recorded"),
        bundle.get("bundle_contains_final_closure_receipt") or bundle.get("bundle_records_self_reference_limit"),
        components.get("ancient") == "PASS",
        components.get("invalid") == "PASS",
        encoding.get("verdict") == "PASS",
    ]
    warnings = [
        "Final committed receipt has accepted git self-reference limit.",
        "Browser-level GitHub UI visibility was not checked and is not claimed.",
    ]
    payload = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "receipt_type": "remote_tree_bundle_closure_receipt",
        "active_root": observation.get("active_root", ""),
        "remote_url": observation.get("remote_url", ""),
        "remote_url_expected": REMOTE_URL,
        "branch": observation.get("branch", ""),
        "local_head": observation.get("local_head", ""),
        "local_head_is_commit": observation.get("local_head_is_commit", False),
        "origin_master": observation.get("origin_master", ""),
        "origin_master_resolves": observation.get("origin_master_resolves", False),
        "ls_remote_master": observation.get("ls_remote_master", ""),
        "head_equals_origin_master": observation.get("head_equals_origin_master", False),
        "ls_remote_equals_local_head": observation.get("ls_remote_equals_local_head", False),
        "ls_remote_equals_origin_master": observation.get("ls_remote_equals_origin_master", False),
        "worktree_clean": observation.get("worktree_clean", False),
        "worktree_clean_gate_deferred_to_finalize": allow_dirty_worktree
        and not observation.get("worktree_clean", False),
        "status_short_branch_at_observation": observation.get("status_short_branch_lines", []),
        "report_bundle_path": bundle.get("bundle_path", ""),
        "report_bundle_sha256": bundle.get("bundle_sha256", ""),
        "sha256sums_path": sha_report.get("sha256sums_path", ""),
        "bundle_sha256_matches_sha256sums": sha_report.get("bundle_hash_recorded", False),
        "bundle_contains_final_closure_receipt": bundle.get("bundle_contains_final_closure_receipt", False),
        "bundle_records_self_reference_limit": bundle.get("bundle_records_self_reference_limit", False),
        "ancient_empire_mutated": components.get("ancient") != "PASS",
        "invalid_taskpack_blocked_no_launch": components.get("invalid") == "PASS",
        "machine_artifacts_encoding_verdict": encoding.get("verdict", ""),
        "self_reference_limit": "ACCEPTED_FINAL_RECEIPT_COMMIT_HASH_REQUIRES_POST_PUSH_NO_WRITE_VERIFY",
        "remote_visibility_proof": "git ls-remote origin refs/heads/master",
        "browser_github_ui_visibility": "NOT_CHECKED_NOT_CLAIMED",
        "warnings": warnings,
        "verdict": "PASS_WITH_SELF_REFERENCE_LIMIT" if all(all_core) else "BLOCK",
    }
    write_json(report_dir / REMOTE_TREE_RECEIPT, payload)
    return payload


def build_final_remote_closure(
    report_dir: Path,
    observation: dict[str, Any],
    remote_tree: dict[str, Any],
    bundle_contract: dict[str, Any],
) -> dict[str, Any]:
    payload = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "receipt_type": "final_remote_closure_receipt",
        "active_root": observation.get("active_root", ""),
        "remote_url": observation.get("remote_url", ""),
        "branch": observation.get("branch", ""),
        "local_head_at_observation": observation.get("local_head", ""),
        "origin_master_at_observation": observation.get("origin_master", ""),
        "ls_remote_master_at_observation": observation.get("ls_remote_master", ""),
        "head_equals_origin_master_at_observation": observation.get("head_equals_origin_master", False),
        "head_equals_ls_remote_at_observation": observation.get("ls_remote_equals_local_head", False),
        "worktree_clean_at_observation": observation.get("worktree_clean", False),
        "status_short_branch_at_observation": observation.get("status_short_branch_lines", []),
        "report_bundle_path": remote_tree.get("report_bundle_path", ""),
        "report_bundle_sha256": remote_tree.get("report_bundle_sha256", ""),
        "sha256sums_path": remote_tree.get("sha256sums_path", ""),
        "bundle_contract_receipt": BUNDLE_CONTRACT_RECEIPT,
        "remote_tree_bundle_closure_receipt": REMOTE_TREE_RECEIPT,
        "self_reference_limit_recorded": True,
        "post_push_no_write_verify_required": True,
        "post_push_verify_command": [
            sys.executable,
            "TOOLS/NEW_REALITY_VALIDATORS/validate_remote_tree_bundle_closure_v0_1.py",
            "--phase",
            "verify",
        ],
        "verdict": "PASS_WITH_SELF_REFERENCE_LIMIT"
        if remote_tree.get("verdict") == "PASS_WITH_SELF_REFERENCE_LIMIT"
        and bundle_contract.get("verdict") == "PASS_WITH_SELF_REFERENCE_LIMIT"
        else "BLOCK",
    }
    write_json(report_dir / FINAL_REMOTE_CLOSURE_RECEIPT, payload)
    return payload


def required_report_paths(report_dir: Path) -> list[Path]:
    return [
        report_dir / REMOTE_TREE_RECEIPT,
        report_dir / NATIVE_REPLAY_RECEIPT,
        report_dir / INVALID_RECHECK_RECEIPT,
        report_dir / ANCIENT_GUARD_RECEIPT,
        report_dir / BUNDLE_CONTRACT_RECEIPT,
        report_dir / FINAL_REMOTE_CLOSURE_RECEIPT,
        report_dir / VALIDATOR_STDOUT,
        report_dir / RED_TEAM,
        report_dir / CLAIM_LEDGER,
        report_dir / CAPABILITY_SPLIT,
        report_dir / SHA256SUMS_NAME,
        report_dir / BUNDLE_NAME,
    ]


def run_phase(repo_root: Path, report_dir: Path, phase: str) -> dict[str, Any]:
    report_dir.mkdir(parents=True, exist_ok=True)
    observation = git_observation(repo_root)
    ancient_before = ancient_snapshot()
    native = build_native_registry_replay(repo_root, report_dir)
    invalid = build_invalid_recheck(repo_root, report_dir)
    ancient_after = ancient_snapshot()
    ancient = build_ancient_guard(report_dir, ancient_before, ancient_after)
    capability = build_capability_split(report_dir)

    pre_bundle_components = {
        "native": component_verdict(native),
        "invalid": component_verdict(invalid),
        "ancient": component_verdict(ancient),
        "bundle": "PENDING",
        "encoding": "PENDING",
        "remote_tree": "PENDING",
    }
    build_claim_ledger(report_dir, pre_bundle_components)
    initial_encoding = validate_encoding_for_paths(
        [
            report_dir / NATIVE_REPLAY_RECEIPT,
            report_dir / INVALID_RECHECK_RECEIPT,
            report_dir / ANCIENT_GUARD_RECEIPT,
            report_dir / CLAIM_LEDGER,
            report_dir / CAPABILITY_SPLIT,
            repo_root / "TOOLS" / "NEW_REALITY_VALIDATORS" / "validate_remote_tree_bundle_closure_v0_1.py",
            repo_root / "SCHEMAS" / "remote_tree_bundle_closure_receipt.schema.json",
            repo_root / "DOCS" / "NEW_REALITY_REMOTE_TREE_BUNDLE_CLOSURE_VALIDATOR_V0_1.md",
        ],
        repo_root,
    )
    build_red_team(report_dir, pre_bundle_components, initial_encoding)
    bundle = build_bundle(repo_root, report_dir)
    bundle_encoding = validate_bundle_encoding(Path(str(bundle["bundle_path"])))
    encoding_paths = [
        path
        for path in report_dir.rglob("*")
        if path.is_file() and path.name not in {BUNDLE_NAME, SHA256SUMS_NAME}
    ]
    encoding_paths.extend(
        [
            repo_root / "TOOLS" / "NEW_REALITY_VALIDATORS" / "validate_remote_tree_bundle_closure_v0_1.py",
            repo_root / "SCHEMAS" / "remote_tree_bundle_closure_receipt.schema.json",
            repo_root / "DOCS" / "NEW_REALITY_REMOTE_TREE_BUNDLE_CLOSURE_VALIDATOR_V0_1.md",
        ]
    )
    file_encoding = validate_encoding_for_paths(encoding_paths, repo_root)
    encoding = {
        "file_encoding": file_encoding,
        "bundle_encoding": bundle_encoding,
        "issues": file_encoding.get("issues", []) + bundle_encoding.get("issues", []),
        "verdict": "PASS" if file_encoding.get("verdict") == "PASS" and bundle_encoding.get("verdict") == "PASS" else "BLOCK",
    }

    components = {
        "native": component_verdict(native),
        "invalid": component_verdict(invalid),
        "ancient": component_verdict(ancient),
        "bundle": "PENDING",
        "encoding": encoding["verdict"],
        "remote_tree": "PENDING",
    }
    red_team = build_red_team(report_dir, components, encoding)
    build_claim_ledger(report_dir, components)
    bundle = build_bundle(repo_root, report_dir)
    sha_report = write_sha256sums(repo_root, report_dir)
    bundle_contract = build_bundle_contract(report_dir, bundle, sha_report)
    components["bundle"] = "PASS" if bundle_contract.get("verdict") == "PASS_WITH_SELF_REFERENCE_LIMIT" else "BLOCK"
    remote_tree = build_remote_tree_receipt(
        report_dir,
        observation,
        bundle,
        sha_report,
        components,
        encoding,
        allow_dirty_worktree=phase == "prepare",
    )
    components["remote_tree"] = "PASS" if remote_tree.get("verdict") == "PASS_WITH_SELF_REFERENCE_LIMIT" else "BLOCK"
    final = build_final_remote_closure(report_dir, observation, remote_tree, bundle_contract)
    red_team = build_red_team(report_dir, components, encoding)
    claim_ledger = build_claim_ledger(report_dir, components)
    sha_report = write_sha256sums(repo_root, report_dir)

    missing = [
        to_posix(path)
        for path in required_report_paths(report_dir)
        if path.name != VALIDATOR_STDOUT and not path.exists()
    ]
    hard_block = (
        bool(missing)
        or final.get("verdict") == "BLOCK"
        or red_team.get("verdict") == "BLOCK"
        or claim_ledger.get("verdict") == "BLOCK"
        or capability.get("verdict") == "BLOCK"
    )
    result = {
        "task_id": TASK_ID,
        "phase": phase,
        "timestamp_utc": utc_now(),
        "active_root": to_posix(repo_root),
        "report_dir": to_posix(report_dir),
        "observation_head": observation.get("local_head", ""),
        "observation_worktree_clean": observation.get("worktree_clean", False),
        "observation_head_equals_origin_master": observation.get("head_equals_origin_master", False),
        "observation_head_equals_ls_remote": observation.get("ls_remote_equals_local_head", False),
        "bundle_path": bundle.get("bundle_path", ""),
        "bundle_sha256": bundle.get("bundle_sha256", ""),
        "sha256sums_path": sha_report.get("sha256sums_path", ""),
        "components": components,
        "missing_required_outputs": missing,
        "self_reference_limit": "ACCEPTED",
        "verdict": "BLOCK" if hard_block else "PASS_WITH_SELF_REFERENCE_LIMIT",
    }
    write_text(report_dir / VALIDATOR_STDOUT, json.dumps(result, ensure_ascii=True, indent=2))
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return result


def verify_existing(repo_root: Path, report_dir: Path) -> dict[str, Any]:
    observation = git_observation(repo_root)
    bundle_path = report_dir / BUNDLE_NAME
    sha_path = report_dir / SHA256SUMS_NAME
    sha_map = read_sha256sums(sha_path)
    bundle_sha = sha256_file(bundle_path) if bundle_path.exists() else ""
    bundle_recorded = sha_map.get(BUNDLE_NAME, "") == bundle_sha
    bundle_contains_final = False
    bundle_records_limit = False
    bundle_names: list[str] = []
    if bundle_path.exists():
        with zipfile.ZipFile(bundle_path, "r") as archive:
            bundle_names = sorted(archive.namelist())
        bundle_contains_final = FINAL_REMOTE_CLOSURE_RECEIPT in bundle_names
        bundle_records_limit = SELF_REFERENCE_NOTE in bundle_names

    required_repo = [
        repo_root / "TOOLS" / "NEW_REALITY_VALIDATORS" / "validate_remote_tree_bundle_closure_v0_1.py",
        repo_root / "SCHEMAS" / "remote_tree_bundle_closure_receipt.schema.json",
        repo_root / "DOCS" / "NEW_REALITY_REMOTE_TREE_BUNDLE_CLOSURE_VALIDATOR_V0_1.md",
    ]
    missing = [to_posix(path) for path in required_report_paths(report_dir) + required_repo if not path.exists()]
    encoding_paths = [
        path
        for path in report_dir.rglob("*")
        if path.is_file() and path.name not in {BUNDLE_NAME, SHA256SUMS_NAME}
    ]
    encoding_paths.extend(required_repo)
    encoding = validate_encoding_for_paths(encoding_paths, repo_root)
    bundle_encoding = validate_bundle_encoding(bundle_path)
    final_checks = {
        "active_root_is_new_reality": observation.get("active_root") == "E:/IMPERIUM_NEW_GENERATION_NEW_REALITY",
        "remote_url_exact": observation.get("remote_url_exact"),
        "branch_exact": observation.get("branch_exact"),
        "local_head_is_commit": observation.get("local_head_is_commit"),
        "origin_master_resolves": observation.get("origin_master_resolves"),
        "head_equals_origin_master": observation.get("head_equals_origin_master"),
        "ls_remote_equals_local_head": observation.get("ls_remote_equals_local_head"),
        "ls_remote_equals_origin_master": observation.get("ls_remote_equals_origin_master"),
        "worktree_clean": observation.get("worktree_clean"),
        "bundle_exists": bundle_path.exists(),
        "bundle_sha256_matches_sha256sums": bundle_recorded,
        "bundle_contains_final_or_records_limit": bundle_contains_final or bundle_records_limit,
        "required_outputs_present": not missing,
        "machine_artifact_encoding": encoding.get("verdict") == "PASS" and bundle_encoding.get("verdict") == "PASS",
    }
    payload = {
        "task_id": TASK_ID,
        "phase": "verify",
        "timestamp_utc": utc_now(),
        "active_root": to_posix(repo_root),
        "remote_url": observation.get("remote_url", ""),
        "branch": observation.get("branch", ""),
        "local_head": observation.get("local_head", ""),
        "origin_master": observation.get("origin_master", ""),
        "ls_remote_master": observation.get("ls_remote_master", ""),
        "head_equals_origin_master": observation.get("head_equals_origin_master", False),
        "head_equals_ls_remote": observation.get("ls_remote_equals_local_head", False),
        "worktree_clean": observation.get("worktree_clean", False),
        "status_short_branch": observation.get("status_short_branch_lines", []),
        "report_bundle_path": to_posix(bundle_path),
        "report_bundle_sha256": bundle_sha,
        "sha256sums_path": to_posix(sha_path),
        "bundle_sha256_matches_sha256sums": bundle_recorded,
        "bundle_contains_final_closure_receipt": bundle_contains_final,
        "bundle_records_self_reference_limit": bundle_records_limit,
        "missing_required_outputs": missing,
        "encoding_issues": encoding.get("issues", []) + bundle_encoding.get("issues", []),
        "checks": final_checks,
        "verdict": "PASS_WITH_SELF_REFERENCE_LIMIT" if all(final_checks.values()) else "BLOCK",
    }
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return payload


def resolve_report_dir(repo_root: Path, value: str) -> Path:
    if not value:
        return repo_root / REPORT_REL
    path = Path(value)
    if not path.is_absolute():
        path = repo_root / path
    resolved = path.resolve()
    if not is_under(repo_root, resolved):
        raise RuntimeError(f"report directory escapes New Reality root: {resolved}")
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description="New Reality remote/tree/bundle closure validator v0.1.")
    parser.add_argument("--repo-root", default="", help="Explicit New Reality root. Defaults to auto-discovery.")
    parser.add_argument("--report-dir", default="", help="Report directory, relative to repo root or absolute.")
    parser.add_argument("--phase", choices=["prepare", "finalize", "verify"], required=True)
    args = parser.parse_args()

    repo_root = resolve_new_reality_root(args.repo_root or None, start=Path(__file__)).active_root
    report_dir = resolve_report_dir(repo_root, args.report_dir)
    if args.phase == "verify":
        result = verify_existing(repo_root, report_dir)
    else:
        result = run_phase(repo_root, report_dir, args.phase)
    return 0 if str(result.get("verdict", "")).startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
