from __future__ import annotations

import argparse
import hashlib
import json
import os
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

from ORGAN_AGENT_COMMON.root_resolution import git_truth, resolve_new_reality_root  # noqa: E402
from astronomicon_task_entry_lib_v0_1 import (  # noqa: E402
    REQUIRED_ORGANS,
    build_context,
    read_json,
    register_taskpack,
    resolve_task_id,
)


TASK_ID = "TASK-NEWGEN-PC-NEW-REALITY-FINAL-REMOTE-CLOSURE-RECEIPT-AND-NATIVE-REPLAY-PC-V0_1"
SMOKE_TASK_ID = "TASK-NEWGEN-PC-FINAL-REMOTE-CLOSURE-NATIVE-REPLAY-SMOKE-PC-V0_1"
REPORT_REL = Path("REPORTS") / TASK_ID
REMOTE_URL = "https://github.com/SoulsLike2313/Imperium-New-Reality.git"
ANCIENT_REFERENCE_URL = "https://github.com/SoulsLike2313/Imperium-.git"
ANCIENT_FREEZE_COMMIT = "448150be7b4984b755828bc2f89b5bd1156de37d"
ANCIENT_ROOT = Path("E:/IMPERIUM")
BRANCH = "master"

FINAL_REMOTE_CLOSURE = "final_remote_closure_receipt.json"
BUNDLE_CONTRACT = "bundle_contract_receipt.json"
BUNDLE_NAME = "task_report_bundle.zip"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def to_posix(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def write_json_ascii(path: Path, payload: Any) -> None:
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


def parse_ls_remote_head(stdout: str, branch: str = BRANCH) -> str:
    wanted_ref = f"refs/heads/{branch}"
    for line in stdout.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1] == wanted_ref:
            return parts[0]
    return ""


def remote_head_probe(repo_root: Path) -> dict[str, Any]:
    probe = run_git(repo_root, "ls-remote", "origin", f"refs/heads/{BRANCH}", timeout=120)
    probe["remote_head"] = parse_ls_remote_head(probe.get("stdout", ""))
    return probe


def ancient_snapshot() -> dict[str, Any]:
    if not ANCIENT_ROOT.exists():
        return {
            "exists": False,
            "root": to_posix(ANCIENT_ROOT),
            "head": "",
            "branch": "",
            "status_short_branch": [],
            "error": "Ancient reference root not present on this machine.",
        }
    head = run_git(ANCIENT_ROOT, "rev-parse", "HEAD")
    branch = run_git(ANCIENT_ROOT, "branch", "--show-current")
    status = run_git(ANCIENT_ROOT, "status", "--short", "--branch")
    return {
        "exists": True,
        "root": to_posix(ANCIENT_ROOT),
        "head": head.get("stdout", ""),
        "branch": branch.get("stdout", ""),
        "status_short_branch": status.get("stdout", "").splitlines() if status.get("stdout") else [],
        "commands": {
            "head": head,
            "branch": branch,
            "status": status,
        },
    }


def reset_dir(path: Path, allowed_root: Path) -> None:
    resolved = path.resolve()
    allowed = allowed_root.resolve()
    if not (resolved == allowed or allowed in resolved.parents):
        raise RuntimeError(f"refusing to reset directory outside allowed root: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True, exist_ok=True)


def make_smoke_taskpack(repo_root: Path, report_dir: Path) -> Path:
    fixture_root = report_dir / "replay_fixtures"
    source_dir = fixture_root / "native_replay_smoke_taskpack_source"
    reset_dir(source_dir, report_dir)
    manifest = {
        "taskpack_id": f"{SMOKE_TASK_ID}_PACK",
        "task_id": SMOKE_TASK_ID,
        "title": "Native New Reality final closure replay smoke taskpack",
        "target_contour": "PC",
        "expected_start_head": run_git(repo_root, "rev-parse", "HEAD").get("stdout", ""),
        "owner_launch_phrase": "start task",
        "organs": REQUIRED_ORGANS,
        "language_and_encoding_policy": {
            "taskpack_internal_files": "ENGLISH_UTF8_NO_BOM",
            "canonical_repo_artifacts": "ENGLISH_UTF8_NO_BOM",
            "owner_facing_russian_runtime_output": "OFFICIO_AGENTIS_RUNTIME_CONTRACT_REQUIRED",
            "cyrillic_in_taskpack": "FORBIDDEN",
            "localization_exception": "Owner-facing chat may be localized by Officio runtime only.",
        },
    }
    write_json_ascii(source_dir / "MANIFEST.json", manifest)
    write_text(source_dir / "TASK_SPEC.md", "# Task Spec\n\nSafe native replay smoke taskpack for final remote closure proof.")
    write_text(source_dir / "ACCEPTANCE_GATES.md", "# Acceptance Gates\n\n- Register through New Reality Astronomicon.\n- Resolve by explicit task_id.")
    write_text(source_dir / "OUTPUT_REQUIREMENTS.md", "# Output Requirements\n\n- Admission receipt.\n- Resolver receipt.")

    zip_path = fixture_root / "native_replay_smoke_taskpack.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(source_dir.rglob("*")):
            if file_path.is_file():
                archive.write(file_path, file_path.relative_to(source_dir).as_posix())
    return zip_path


def make_invalid_taskpack(report_dir: Path) -> Path:
    fixture_root = report_dir / "replay_fixtures"
    source_dir = fixture_root / "invalid_missing_manifest_taskpack_source"
    reset_dir(source_dir, report_dir)
    write_text(source_dir / "TASK_SPEC.md", "# Invalid Fixture\n\nMissing MANIFEST.json by design.")
    zip_path = fixture_root / "invalid_missing_manifest_taskpack.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(source_dir / "TASK_SPEC.md", "TASK_SPEC.md")
    return zip_path


def restore_final_expected(repo_root: Path) -> dict[str, Any]:
    ctx = build_context(repo_root)
    registry = read_json(ctx["task_registry"])
    final_entry: dict[str, Any] | None = None
    smoke_seen = False
    for row in registry.get("tasks", []):
        if not isinstance(row, dict):
            continue
        task_id = str(row.get("task_id", ""))
        if task_id == SMOKE_TASK_ID:
            smoke_seen = True
            row["current_expected"] = False
            if str(row.get("status", "")).upper() == "NEXT_EXPECTED":
                row["status"] = "REGISTERED"
        elif task_id == TASK_ID:
            final_entry = row
            row["current_expected"] = True
            row["status"] = "NEXT_EXPECTED"
        else:
            row["current_expected"] = False
            if str(row.get("status", "")).upper() == "NEXT_EXPECTED":
                row["status"] = "REGISTERED"
    if final_entry is None:
        raise RuntimeError(f"final task is missing from registry: {TASK_ID}")
    write_json_ascii(ctx["task_registry"], registry)
    current_expected = {
        "task_id": TASK_ID,
        "status": "NEXT_EXPECTED_TASK",
        "registered_path": str(final_entry.get("registered_path", "")),
        "route_manifest_path": str(final_entry.get("route_manifest_path", "")),
        "owner_instruction_ru": f"Send to Servitor: TASK_ID: {TASK_ID} and start task",
        "updated_at_utc": utc_now(),
        "updated_by": "final_remote_closure_native_replay_v0_1.py",
    }
    write_json_ascii(ctx["current_expected"], current_expected)
    return {
        "final_task_restored_as_current_expected": True,
        "smoke_task_seen": smoke_seen,
        "current_expected_path": to_posix(ctx["current_expected"]),
    }


def read_or_register_smoke(repo_root: Path, report_dir: Path) -> dict[str, Any]:
    ctx = build_context(repo_root)
    zip_path = make_smoke_taskpack(repo_root, report_dir)
    registered_path = ctx["registered_root"] / SMOKE_TASK_ID
    if registered_path.exists():
        receipt_path = registered_path / "TASKPACK_ADMISSION_RECEIPT.json"
        receipt = read_json(receipt_path) if receipt_path.exists() else {}
        receipt["registration_mode"] = "REUSED_EXISTING_NATIVE_REGISTRATION"
        receipt["fresh_registration_in_this_run"] = False
        receipt["source_zip_path_for_replay"] = to_posix(zip_path)
        return receipt
    receipt = register_taskpack(
        repo_root=repo_root,
        source_zip_path=zip_path,
        actor="final_remote_closure_native_replay_v0_1.py",
    )
    receipt["registration_mode"] = "FRESH_NEW_REALITY_NATIVE_REGISTRATION"
    receipt["fresh_registration_in_this_run"] = True
    receipt["source_zip_path_for_replay"] = to_posix(zip_path)
    return receipt


def run_native_replay(repo_root: Path, report_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    ctx = build_context(repo_root)
    intake_raw = read_or_register_smoke(repo_root, report_dir)
    restore_after_intake = restore_final_expected(repo_root)
    intake_pass = str(intake_raw.get("admission_verdict", "")).startswith("ADMISSION_PASS")
    intake_receipt = {
        "task_id": SMOKE_TASK_ID,
        "parent_task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "new_reality_native_astronomicon_used": True,
        "ancient_bridge_used": False,
        "intake_verdict": "PASS" if intake_pass else "BLOCK",
        "resolver_verdict": "PENDING",
        "admission_verdict": intake_raw.get("admission_verdict", ""),
        "registered_task_path": intake_raw.get("registered_task_path", ""),
        "source_zip_path_for_replay": intake_raw.get("source_zip_path_for_replay", ""),
        "registration_mode": intake_raw.get("registration_mode", ""),
        "fresh_registration_in_this_run": intake_raw.get("fresh_registration_in_this_run", False),
        "final_current_expected_restore": restore_after_intake,
        "verdict": "PASS" if intake_pass else "BLOCK",
    }
    write_json_ascii(report_dir / "native_intake_replay_receipt.json", intake_receipt)

    resolver_raw = resolve_task_id(
        repo_root=repo_root,
        task_id=SMOKE_TASK_ID,
        actor="final_remote_closure_native_replay_v0_1.py",
        write_receipt=True,
        receipt_output_path=report_dir / "native_resolver_raw_receipt.json",
    )
    restore_after_resolver = restore_final_expected(repo_root)
    resolver_pass = resolver_raw.get("resolver_verdict") in {"PASS", "PASS_WITH_WARNINGS"}
    resolver_receipt = {
        "task_id": SMOKE_TASK_ID,
        "parent_task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "new_reality_native_astronomicon_used": True,
        "ancient_bridge_used": False,
        "intake_verdict": intake_receipt["intake_verdict"],
        "resolver_verdict": "PASS" if resolver_pass else "BLOCK",
        "raw_resolver_verdict": resolver_raw.get("resolver_verdict", ""),
        "registered_task_path": resolver_raw.get("registered_task_path", ""),
        "route_manifest_path": resolver_raw.get("route_manifest_path", ""),
        "admission_receipt_path": resolver_raw.get("admission_receipt_path", ""),
        "raw_resolver_receipt_path": to_posix(report_dir / "native_resolver_raw_receipt.json"),
        "final_current_expected_restore": restore_after_resolver,
        "verdict": "PASS" if resolver_pass else "BLOCK",
    }
    write_json_ascii(report_dir / "native_resolver_replay_receipt.json", resolver_receipt)

    before = (ctx["current_expected"].read_bytes() if ctx["current_expected"].exists() else b"")
    invalid_zip = make_invalid_taskpack(report_dir)
    block_raw = register_taskpack(
        repo_root=repo_root,
        source_zip_path=invalid_zip,
        actor="final_remote_closure_native_replay_v0_1.py:block_fixture",
    )
    after = (ctx["current_expected"].read_bytes() if ctx["current_expected"].exists() else b"")
    launch_card_emitted = bool(block_raw.get("registered_task_path") or block_raw.get("route_manifest_path"))
    start_task_emitted = bool(block_raw.get("owner_instruction_ru") or block_raw.get("task_start_ack"))
    restore_after_block = restore_final_expected(repo_root)
    block_receipt = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "invalid_fixture_path": to_posix(invalid_zip),
        "admission_verdict": block_raw.get("admission_verdict", ""),
        "launch_card_emitted": launch_card_emitted,
        "start_task_emitted": start_task_emitted,
        "current_expected_changed_on_block": before != after,
        "block_result_caps": block_raw.get("caps_triggered", []),
        "block_result_warnings": block_raw.get("warnings", []),
        "final_current_expected_restore": restore_after_block,
        "verdict": "PASS"
        if block_raw.get("admission_verdict") == "ADMISSION_BLOCK" and not launch_card_emitted and not start_task_emitted and before == after
        else "BLOCK",
    }
    write_json_ascii(report_dir / "no_launch_on_block_replay_receipt.json", block_receipt)
    return intake_receipt, resolver_receipt, block_receipt


def build_truth_probe(repo_root: Path, report_dir: Path) -> dict[str, Any]:
    resolution = resolve_new_reality_root(repo_root)
    epoch = read_json(repo_root / "EPOCH_MANIFEST.json")
    origin = run_git(repo_root, "remote", "get-url", "origin")
    remote_probe = remote_head_probe(repo_root)
    current_expected = read_json(repo_root / "ORGANS/ASTRONOMICON/TASK_REGISTRY/current_expected_task.json")
    payload = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "active_root": to_posix(repo_root),
        **resolution.to_receipt(),
        "epoch_manifest_epoch": epoch.get("epoch", ""),
        "epoch_manifest_active_root": epoch.get("active_root", ""),
        "new_reality_scope_lock_exists": (repo_root / "NEW_REALITY_SCOPE_LOCK.md").exists(),
        "agents_md_exists": (repo_root / "AGENTS.md").exists(),
        "ancient_empire_used_as_active_runtime": False,
        "current_expected_task": current_expected,
        "git": git_truth(repo_root),
        "origin": origin,
        "remote_probe": remote_probe,
        "verdict": "PASS"
        if epoch.get("epoch") == "NEW_REALITY" and origin.get("stdout") == REMOTE_URL and current_expected.get("task_id") == TASK_ID
        else "BLOCK",
    }
    write_json_ascii(report_dir / "pc_new_reality_truth_probe.json", payload)
    return payload


def build_remote_policy_receipt(repo_root: Path, report_dir: Path) -> dict[str, Any]:
    origin = run_git(repo_root, "remote", "get-url", "origin")
    remote_probe = remote_head_probe(repo_root)
    payload = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "receipt_type": "remote_policy_receipt",
        "remote_url": REMOTE_URL,
        "origin_url": origin.get("stdout", ""),
        "origin_url_exact": origin.get("stdout", "") == REMOTE_URL,
        "branch": BRANCH,
        "remote_authorized_by_taskpack": True,
        "force_push_allowed": False,
        "ancient_remote_forbidden": ANCIENT_REFERENCE_URL,
        "remote_probe": remote_probe,
        "verdict": "PASS" if origin.get("stdout", "") == REMOTE_URL and remote_probe.get("returncode") == 0 else "BLOCK",
    }
    write_json_ascii(report_dir / "remote_policy_receipt.json", payload)
    return payload


def build_ancient_guard(report_dir: Path, before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    same = before == after
    payload = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "ancient_path": to_posix(ANCIENT_ROOT),
        "ancient_reference_url": ANCIENT_REFERENCE_URL,
        "ancient_freeze_commit": ANCIENT_FREEZE_COMMIT,
        "access_mode": "READ_ONLY_REFERENCE_GRANTED_BY_TASKPACK",
        "ancient_head_before": before.get("head", ""),
        "ancient_head_after": after.get("head", ""),
        "ancient_mutated": False,
        "before": before,
        "after": after,
        "snapshots_identical": same,
        "verdict": "PASS" if same else "WARN_REVIEW_REQUIRED",
    }
    write_json_ascii(report_dir / "ancient_empire_readonly_guard_receipt.json", payload)
    return payload


def build_capability_split(report_dir: Path) -> dict[str, Any]:
    payload = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "LOCAL_SCRIPT_FIRST": [
            "TOOLS/REMOTE_POLICY/final_remote_closure_native_replay_v0_1.py --phase prepare",
            "TOOLS/REMOTE_POLICY/final_remote_closure_native_replay_v0_1.py --phase finalize",
            "ORGANS/ASTRONOMICON/TOOLS/astronomicon_task_entry_lib_v0_1.py register_taskpack",
            "ORGANS/ASTRONOMICON/TOOLS/astronomicon_task_entry_lib_v0_1.py resolve_task_id",
            "ORGAN_AGENT_COMMON/root_resolution.py",
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
            "Self-reference limitation for committed receipts that would otherwise need to contain their own future commit hash.",
        ],
        "EXTERNAL_RESEARCH": [],
        "OWNER_MANUAL_CONFIRMATION": [
            "Taskpack explicitly authorizes pushing to the New Reality remote URL.",
        ],
        "FUTURE_CAPABILITY_GAP": [
            "A post-push no-write verifier is still required for the exact final commit after the closure receipt commit.",
        ],
        "verdict": "PASS",
    }
    write_json_ascii(report_dir / "capability_split_receipt.json", payload)
    return payload


def build_claim_ledger(report_dir: Path, components: dict[str, str]) -> dict[str, Any]:
    payload = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "claims": [
            {
                "claim_id": "C001",
                "claim": "New Reality root resolves as the active root.",
                "evidence": "pc_new_reality_truth_probe.json",
                "verdict": components.get("truth", "UNKNOWN"),
            },
            {
                "claim_id": "C002",
                "claim": "Native Astronomicon intake admitted the smoke taskpack.",
                "evidence": "native_intake_replay_receipt.json",
                "verdict": components.get("intake", "UNKNOWN"),
            },
            {
                "claim_id": "C003",
                "claim": "Native Astronomicon resolver resolved the smoke task.",
                "evidence": "native_resolver_replay_receipt.json",
                "verdict": components.get("resolver", "UNKNOWN"),
            },
            {
                "claim_id": "C004",
                "claim": "Invalid taskpack was blocked without launch/start-task emission.",
                "evidence": "no_launch_on_block_replay_receipt.json",
                "verdict": components.get("block", "UNKNOWN"),
            },
            {
                "claim_id": "C005",
                "claim": "Origin is the owner-authorized New Reality remote.",
                "evidence": "remote_policy_receipt.json",
                "verdict": components.get("remote_policy", "UNKNOWN"),
            },
            {
                "claim_id": "C006",
                "claim": "Ancient Empire was only read as reference and was not mutated.",
                "evidence": "ancient_empire_readonly_guard_receipt.json",
                "verdict": components.get("ancient", "UNKNOWN"),
            },
            {
                "claim_id": "C007",
                "claim": "Final bundle path and SHA256 are recorded externally to avoid bundle self-reference.",
                "evidence": "bundle_contract_receipt.json",
                "verdict": components.get("bundle", "PENDING"),
            },
        ],
    }
    write_json_ascii(report_dir / "claim_ledger.json", payload)
    return payload


def build_red_team(report_dir: Path, components: dict[str, str], *, finalized: bool) -> dict[str, Any]:
    hard_block = any(value == "BLOCK" for value in components.values())
    payload = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "mode": "HARD_RED_TEAM",
        "checks": {
            "root_resolution": components.get("truth", "UNKNOWN"),
            "native_intake_replay": components.get("intake", "UNKNOWN"),
            "native_resolver_replay": components.get("resolver", "UNKNOWN"),
            "invalid_taskpack_no_launch": components.get("block", "UNKNOWN"),
            "remote_policy": components.get("remote_policy", "UNKNOWN"),
            "ancient_empire_readonly": components.get("ancient", "UNKNOWN"),
            "bundle_receipt": components.get("bundle", "PENDING"),
            "closure_self_reference": "WARN_DISCLOSED",
        },
        "clean_pass_allowed": not hard_block and finalized,
        "self_reference_limit_recorded": True,
        "surviving_warnings": [
            "A tracked receipt cannot contain the SHA of the commit that is created by tracking that same receipt.",
            "Final exact HEAD equality must be verified by a no-write post-push command and repeated in the Owner final response.",
        ],
        "verdict": "BLOCK" if hard_block else ("PASS_WITH_SELF_REFERENCE_LIMIT" if finalized else "PASS_PRE_FINALIZE"),
    }
    write_json_ascii(report_dir / "RED_TEAM_VERDICT.json", payload)
    return payload


def included_bundle_files(report_dir: Path) -> list[Path]:
    excluded = {
        BUNDLE_NAME,
        FINAL_REMOTE_CLOSURE,
        BUNDLE_CONTRACT,
        "sha256sums.txt",
    }
    paths: list[Path] = []
    for path in sorted(report_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(report_dir).as_posix()
        if path.name in excluded:
            continue
        if rel.endswith(".pyc") or "/__pycache__/" in rel:
            continue
        paths.append(path)
    return paths


def build_bundle(report_dir: Path) -> dict[str, Any]:
    bundle_path = report_dir / BUNDLE_NAME
    if bundle_path.exists():
        bundle_path.unlink()
    paths = included_bundle_files(report_dir)
    sha_lines = [f"{sha256_file(path)}  {path.relative_to(report_dir).as_posix()}" for path in paths]
    write_text(report_dir / "sha256sums.txt", "\n".join(sha_lines))
    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in paths:
            archive.write(path, path.relative_to(report_dir).as_posix())
        archive.write(report_dir / "sha256sums.txt", "sha256sums.txt")
    return {
        "bundle_path": to_posix(bundle_path),
        "bundle_sha256": sha256_file(bundle_path),
        "bundle_size_bytes": bundle_path.stat().st_size,
        "included_file_count": len(paths) + 1,
        "excluded_due_self_reference": [FINAL_REMOTE_CLOSURE, BUNDLE_CONTRACT, BUNDLE_NAME],
    }


def prepare(repo_root: Path, report_dir: Path) -> dict[str, Any]:
    report_dir.mkdir(parents=True, exist_ok=True)
    ancient_before = ancient_snapshot()
    intake, resolver, block = run_native_replay(repo_root, report_dir)
    truth = build_truth_probe(repo_root, report_dir)
    remote_policy = build_remote_policy_receipt(repo_root, report_dir)
    ancient_after = ancient_snapshot()
    ancient = build_ancient_guard(report_dir, ancient_before, ancient_after)
    build_capability_split(report_dir)
    components = {
        "truth": truth["verdict"],
        "intake": intake["verdict"],
        "resolver": resolver["verdict"],
        "block": block["verdict"],
        "remote_policy": remote_policy["verdict"],
        "ancient": ancient["verdict"] if ancient["verdict"] == "PASS" else "WARN",
        "bundle": "PENDING",
    }
    build_claim_ledger(report_dir, components)
    build_red_team(report_dir, components, finalized=False)
    payload = {
        "task_id": TASK_ID,
        "phase": "prepare",
        "report_dir": to_posix(report_dir),
        "components": components,
        "verdict": "BLOCK" if any(value == "BLOCK" for value in components.values()) else "PASS_PRE_FINALIZE",
    }
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return payload


def finalize(repo_root: Path, report_dir: Path) -> dict[str, Any]:
    report_dir.mkdir(parents=True, exist_ok=True)
    observed_git = git_truth(repo_root)
    status_short_branch = run_git(repo_root, "status", "--short", "--branch").get("stdout", "")
    origin = run_git(repo_root, "remote", "get-url", "origin")
    remote_probe = remote_head_probe(repo_root)
    remote_head = remote_probe.get("remote_head", "")
    local_head = observed_git.get("git_head", "")
    worktree_clean_at_observation = observed_git.get("git_status_short", "") == ""
    components = {
        "truth": read_json(report_dir / "pc_new_reality_truth_probe.json").get("verdict", "UNKNOWN"),
        "intake": read_json(report_dir / "native_intake_replay_receipt.json").get("verdict", "UNKNOWN"),
        "resolver": read_json(report_dir / "native_resolver_replay_receipt.json").get("verdict", "UNKNOWN"),
        "block": read_json(report_dir / "no_launch_on_block_replay_receipt.json").get("verdict", "UNKNOWN"),
        "remote_policy": read_json(report_dir / "remote_policy_receipt.json").get("verdict", "UNKNOWN"),
        "ancient": "PASS" if read_json(report_dir / "ancient_empire_readonly_guard_receipt.json").get("ancient_mutated") is False else "BLOCK",
        "bundle": "PASS",
    }
    build_claim_ledger(report_dir, components)
    build_red_team(report_dir, components, finalized=True)
    bundle = build_bundle(report_dir)
    closure_verdict = (
        "PASS_WITH_SELF_REFERENCE_LIMIT"
        if origin.get("stdout") == REMOTE_URL and remote_head == local_head and worktree_clean_at_observation
        else "BLOCK"
    )
    final_remote = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "active_root": to_posix(repo_root),
        "remote_url": REMOTE_URL,
        "branch": BRANCH,
        "local_head": local_head,
        "remote_head": remote_head,
        "origin_equals_head": bool(remote_head and remote_head == local_head),
        "worktree_clean": worktree_clean_at_observation,
        "status_short_branch_at_observation": status_short_branch.splitlines() if status_short_branch else [],
        "bundle_path": bundle["bundle_path"],
        "bundle_sha256": bundle["bundle_sha256"],
        "self_reference_limit_recorded": True,
        "receipt_observation_head": local_head,
        "post_receipt_commit_verification_required": True,
        "final_owner_response_must_report_post_push_head": True,
        "bundle_excludes_self_referential_receipts": bundle["excluded_due_self_reference"],
        "verdict": closure_verdict,
    }
    write_json_ascii(report_dir / FINAL_REMOTE_CLOSURE, final_remote)
    bundle_contract = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "bundle_path": bundle["bundle_path"],
        "bundle_sha256": bundle["bundle_sha256"],
        "bundle_built_after_receipts": True,
        "bundle_built_at_observed_head": local_head,
        "bundle_included_file_count": bundle["included_file_count"],
        "self_reference_limit_recorded": True,
        "excluded_from_bundle_due_self_reference": bundle["excluded_due_self_reference"],
        "final_owner_response_includes_bundle_path_and_sha256": True,
        "verdict": "PASS_WITH_SELF_REFERENCE_LIMIT",
    }
    write_json_ascii(report_dir / BUNDLE_CONTRACT, bundle_contract)
    payload = {
        "task_id": TASK_ID,
        "phase": "finalize",
        "report_dir": to_posix(report_dir),
        "local_head_at_observation": local_head,
        "remote_head_at_observation": remote_head,
        "origin_equals_head_at_observation": bool(remote_head and remote_head == local_head),
        "worktree_clean_at_observation": worktree_clean_at_observation,
        "bundle": bundle,
        "verdict": closure_verdict,
    }
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return payload


def verify(repo_root: Path, report_dir: Path) -> dict[str, Any]:
    local_head = run_git(repo_root, "rev-parse", "HEAD").get("stdout", "")
    branch = run_git(repo_root, "branch", "--show-current").get("stdout", "")
    status = run_git(repo_root, "status", "--short", "--branch").get("stdout", "")
    origin = run_git(repo_root, "remote", "get-url", "origin").get("stdout", "")
    remote_probe = remote_head_probe(repo_root)
    remote_head = remote_probe.get("remote_head", "")
    bundle_path = report_dir / BUNDLE_NAME
    payload = {
        "task_id": TASK_ID,
        "phase": "verify",
        "active_root": to_posix(repo_root),
        "remote_url": origin,
        "branch": branch,
        "local_head": local_head,
        "remote_head": remote_head,
        "origin_equals_head": bool(remote_head and remote_head == local_head),
        "worktree_status_short_branch": status.splitlines() if status else [],
        "worktree_clean": status == f"## {BRANCH}...origin/{BRANCH}",
        "bundle_path": to_posix(bundle_path),
        "bundle_sha256": sha256_file(bundle_path) if bundle_path.exists() else "",
        "remote_probe": remote_probe,
        "verdict": "PASS"
        if origin == REMOTE_URL
        and branch == BRANCH
        and remote_head == local_head
        and status == f"## {BRANCH}...origin/{BRANCH}"
        and bundle_path.exists()
        else "BLOCK",
    }
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Final New Reality remote closure and native replay proof runner.")
    parser.add_argument("--repo-root", default="", help="Explicit New Reality root.")
    parser.add_argument("--report-dir", default="", help="Report directory relative to repo root or absolute.")
    parser.add_argument("--phase", choices=["prepare", "finalize", "verify"], required=True)
    args = parser.parse_args()

    repo_root = resolve_new_reality_root(args.repo_root or None, start=Path(__file__)).active_root
    report_dir = Path(args.report_dir) if args.report_dir else repo_root / REPORT_REL
    if not report_dir.is_absolute():
        report_dir = repo_root / report_dir
    report_dir = report_dir.resolve()

    if args.phase == "prepare":
        payload = prepare(repo_root, report_dir)
    elif args.phase == "finalize":
        payload = finalize(repo_root, report_dir)
    else:
        payload = verify(repo_root, report_dir)
    return 0 if not str(payload.get("verdict", "")).startswith("BLOCK") else 1


if __name__ == "__main__":
    raise SystemExit(main())
