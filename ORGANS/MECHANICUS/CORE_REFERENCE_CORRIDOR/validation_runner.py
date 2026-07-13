"""Current-proof validator and 20-scenario adversarial receipt writer."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .evidence import EvidenceFinalizedError, EvidenceStore
from .executor import git_state
from .negative_proof_runner import run_negative_suite
from .registry import atomic_write_json, sha256_file
from .root_resolver import resolve_repository_context
from .service import BASE_HEAD, REPORT_RELATIVE, TASKPACK_RELATIVE, TASK_ID, WARP_ID


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _run(argv: list[str], cwd: Path, timeout: int = 180) -> dict[str, Any]:
    started = _utc_now()
    completed = subprocess.run(
        argv,
        cwd=str(cwd),
        shell=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    return {
        "argv": argv,
        "started_at_utc": started,
        "ended_at_utc": _utc_now(),
        "exit_code": completed.returncode,
        "timeout": timeout,
        "stdout_sha256": hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest(),
        "stderr_sha256": hashlib.sha256(completed.stderr.encode("utf-8")).hexdigest(),
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
        "verdict": "PASS" if completed.returncode == 0 else "BLOCK",
    }


def _junit(report: Path) -> tuple[dict[str, Any], set[str]]:
    path = report / "BACKEND_TEST_RESULTS.xml"
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    tests = sum(int(item.attrib.get("tests", 0)) for item in suites)
    failures = sum(int(item.attrib.get("failures", 0)) for item in suites)
    errors = sum(int(item.attrib.get("errors", 0)) for item in suites)
    skipped = sum(int(item.attrib.get("skipped", 0)) for item in suites)
    names = {item.attrib.get("name", "") for item in root.iter("testcase")}
    return (
        {
            "path": path.relative_to(report).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "tests": tests,
            "failures": failures,
            "errors": errors,
            "skipped": skipped,
            "verdict": "PASS" if tests > 0 and failures == errors == 0 else "BLOCK",
        },
        names,
    )


def _source_security(worktree: Path) -> dict[str, Any]:
    rust = (worktree / "SUPPORT/APP_TAURI/src-tauri/src/main.rs").read_text(encoding="utf-8")
    sources = "\n".join(path.read_text(encoding="utf-8") for path in (worktree / "SUPPORT/APP_TAURI/src-tauri/src").rglob("*.rs"))
    forbidden = [pattern for pattern in ["run_registered_patch_pack", "find_runner", 'Command::new("pwsh")', "RUN_*.ps1"] if pattern in sources]
    handler = re.search(r"invoke_handler\(tauri::generate_handler!\[([\s\S]*?)\]\)", rust)
    commands = [item.strip().split("::")[-1] for item in handler.group(1).split(",") if item.strip()] if handler else []
    corridor_commands = sorted(command for command in commands if command.startswith("corridor_ui_"))
    expected = ["corridor_ui_action", "corridor_ui_snapshot"]
    return {
        "forbidden_matches": forbidden,
        "commands": commands,
        "corridor_commands": corridor_commands,
        "legacy_commands_retained_read_only_by_scope": sorted(set(commands) - set(corridor_commands)),
        "verdict": "PASS" if not forbidden and corridor_commands == expected else "BLOCK",
    }


def _json_parse_check(roots: list[Path]) -> dict[str, Any]:
    checked = 0
    failures: list[str] = []
    for root in roots:
        for path in root.rglob("*.json"):
            if any(part in {"target", "node_modules", "dist"} for part in path.parts):
                continue
            try:
                json.loads(path.read_text(encoding="utf-8"))
                checked += 1
            except Exception as exc:
                failures.append(f"{path}: {exc}")
    return {"checked": checked, "failures": failures, "verdict": "PASS" if not failures else "BLOCK"}


def _line_check(worktree: Path) -> dict[str, Any]:
    roots = [worktree / "ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR", worktree / "SUPPORT/APP_TAURI/src/corridor", worktree / "SUPPORT/APP_TAURI/src-tauri/src/corridor"]
    too_large = []
    checked = 0
    for root in roots:
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".js", ".rs"}:
                lines = len(path.read_text(encoding="utf-8").splitlines())
                checked += 1
                if lines > 500:
                    too_large.append({"path": path.relative_to(worktree).as_posix(), "lines": lines})
    return {"checked": checked, "files_over_500": too_large, "verdict": "PASS" if not too_large else "BLOCK"}


def _required_outputs(report: Path) -> dict[str, Any]:
    names = [
        "OWNER_RESULT.md", "ARCHITECTURE_DELTA.md", "AUDIT_FINDINGS_CLOSURE_MATRIX.md", "MIGRATION_MAP.md",
        "KNOWN_GAPS.md", "OWNER_REVIEW_GUIDE.md", "LAND_PLAN.md", "ROLLBACK_PLAN.md", "TASK_MANIFEST.json",
        "TASK_STATE.json", "CAPABILITY_REGISTRY.json", "STATE_TRANSITION_LOG.jsonl", "ORGAN_PARTICIPATION_LEDGER.json",
        "EVIDENCE_INDEX.json", "CHECKPOINT_INDEX.json", "FILES_CHANGED.json", "FILES_TO_LAND.json",
        "DRIFT_GUARD_RECEIPT.json", "DRIFT_GUARD_RECEIPT.md", "WARP_CREATE_RECEIPT.json", "WARP_CREATE_RECEIPT.md",
        "SAFE_EXECUTION_RECEIPT.json", "SAFE_EXECUTION_RECEIPT.md",
    ]
    missing = [name for name in names if not (report / name).is_file()]
    return {"required_count": len(names), "missing": missing, "self_reference_pending": ["VALIDATION_MATRIX.json", "HASH_MANIFEST.json", "VALIDATION_RECEIPT.json", "OWNER_REVIEW_READY_RECEIPT.json"], "verdict": "PASS" if not missing else "BLOCK"}


def _write_envelope(store: EvidenceStore, envelope: dict[str, Any]) -> None:
    try:
        store.write(envelope, finalize=True)
    except EvidenceFinalizedError:
        store.verify(envelope["evidence_id"])


def _executed_envelope(
    *,
    evidence_id: str,
    command: dict[str, Any],
    result: dict[str, Any],
    context: Any,
    pre_git: dict[str, Any],
    post_git: dict[str, Any],
    acceptance: list[dict[str, Any]],
    parent_evidence_id: str,
) -> dict[str, Any]:
    executable = Path(command["argv"][0]).resolve()
    result_bytes = json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    blocked = command["exit_code"] != 0 or str(result.get("verdict", "")).startswith("BLOCK") or any(
        str(item.get("verdict", "")).startswith("BLOCK") for item in acceptance
    )
    tree_hash = str(post_git["worktree"]["working_tree_hash"]).removeprefix("sha256:")
    return {
        "schema_version": "imperium.core_reference_corridor.evidence_envelope.v0_1",
        "evidence_id": evidence_id,
        "task_id": TASK_ID,
        "warp_id": "WARP-CORE-REFERENCE-0001",
        "event_id": "EVENT-" + evidence_id,
        "base_head": BASE_HEAD,
        "result_head_or_tree_hash": tree_hash,
        "branch": context.branch,
        "timestamp_utc": command["ended_at_utc"],
        "host_fingerprint": "sha256:" + hashlib.sha256((platform.node() + platform.machine()).encode("utf-8")).hexdigest(),
        "toolchain": {"platform": platform.system(), "python": platform.python_version()},
        "exact_argv": command["argv"],
        "executable_path": str(executable),
        "executable_sha256": sha256_file(executable),
        "cwd": str(context.worktree_root),
        "environment_profile": {"profile_id": "CORE_VALIDATION_CHILD_V0_1", "set_keys": ["PYTHONDONTWRITEBYTECODE"]},
        "input_hashes": {"owner_prompt": "3fa7249d956c8a79c04a8b5f323ec82bec8de1ebabf7aa3cace18d96e7ef6fd8"},
        "output_hashes": {"result": hashlib.sha256(result_bytes).hexdigest()},
        "stdout_hash": command["stdout_sha256"],
        "stderr_hash": command["stderr_sha256"],
        "exit_code": command["exit_code"],
        "timeout": command["timeout"],
        "pre_git_state": pre_git,
        "post_git_state": post_git,
        "filesystem_diff": {"captured_by_parent_typed_executor": parent_evidence_id},
        "validator_ids": [evidence_id + "_VALIDATOR"],
        "acceptance_results": acceptance,
        "organ_verdict_refs": [f"{REPORT_RELATIVE.as_posix()}/ORGAN_PARTICIPATION_LEDGER.json"],
        "owner_decision_ref": "OWNER-LAUNCH-IMPERIUM-CORE-REFERENCE-0001",
        "parent_evidence_ids": [parent_evidence_id],
        "verdict": "BLOCK" if blocked else "PASS_PROVEN",
        "result": result,
    }


def _validation_attempt(report: Path) -> int:
    attempts = [0] if (report / "VALIDATION_RECEIPT.json").is_file() else []
    for path in report.glob("VALIDATION_RETRY_*_RECEIPT.json"):
        match = re.fullmatch(r"VALIDATION_RETRY_(\d+)_RECEIPT\.json", path.name)
        if match:
            attempts.append(int(match.group(1)))
    return max(attempts, default=-1) + 1


def validate_and_write() -> dict[str, Any]:
    context = resolve_repository_context(".")
    worktree, reality = Path(context.worktree_root), Path(context.reality_root)
    report = worktree / REPORT_RELATIVE
    pre_git = {"reality": git_state(reality), "worktree": git_state(worktree)}
    reality_before = _live_git(reality)
    pytest_result = _run(
        [
            sys.executable,
            "-m",
            "pytest",
            "ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests",
            "-q",
            "-p",
            "no:cacheprovider",
            "--junitxml",
            str(report / "BACKEND_TEST_RESULTS.xml"),
        ],
        worktree,
        240,
    )
    junit, _test_names = _junit(report)
    app = worktree / "SUPPORT/APP_TAURI"
    npm = shutil.which("npm.cmd") or shutil.which("npm") or "npm.cmd"
    node = shutil.which("node.exe") or shutil.which("node") or "node.exe"
    node_build = _run([npm, "run", "build"], app)
    node_parity = _run([node, "tests/action_parity_check.mjs"], app)
    cargo_check = _run(["cargo", "check", "--manifest-path", "src-tauri/Cargo.toml"], app)
    cargo_tests = _run(["cargo", "test", "--manifest-path", "src-tauri/Cargo.toml", "corridor::bridge::tests"], app)
    diff_check = _run(["git", "diff", "--check"], worktree)
    taskpack_check = _run(
        [sys.executable, "ORGANS/ASTRONOMICON/TOOLS/servitor_intake.py", "check", str(worktree / TASKPACK_RELATIVE / "EXTRACTED"), "--servitor", "CODEX", "--reality-root", str(worktree)],
        worktree,
    )
    post_git = {"reality": git_state(reality), "worktree": git_state(worktree)}
    reality_after = _live_git(reality)
    negative = run_negative_suite(
        report=report,
        worktree=worktree,
        reality=reality,
        task_id=TASK_ID,
        warp_id=WARP_ID,
        base_head=BASE_HEAD,
    )
    try:
        parity_result = json.loads(node_parity["stdout_tail"])
    except json.JSONDecodeError:
        parity_result = {"verdict": "BLOCK", "raw_tail": node_parity["stdout_tail"]}
    security = _source_security(worktree)
    json_check = _json_parse_check([worktree / "ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR", worktree / TASKPACK_RELATIVE, report])
    line_check = _line_check(worktree)
    required = _required_outputs(report)
    attempt = _validation_attempt(report)
    suffix = "" if attempt == 0 else f"_ATTEMPT_{attempt:02d}"
    negative_evidence_id = "NEGATIVE_PROOF_RECEIPT" + suffix
    ui_evidence_id = "UI_BACKEND_PARITY_RECEIPT" + suffix
    validation_evidence_id = "VALIDATION_RECEIPT" if attempt == 0 else f"VALIDATION_RETRY_{attempt:02d}_RECEIPT"
    checks = {
        "pytest_execution": pytest_result,
        "backend_tests": junit,
        "negative_scenarios": {"count": negative["scenario_count"], "verdict": "PASS" if negative["phase_acceptance"] == "NEGATIVE_PROOF_HARDENING_PASS" else "BLOCK"},
        "vite_build": node_build,
        "ui_backend_parity": {**node_parity, "parsed": parity_result},
        "cargo_check": cargo_check,
        "cargo_bridge_tests": cargo_tests,
        "direct_runner_unreachable": security,
        "git_diff_check": diff_check,
        "taskpack_digest_check": taskpack_check,
        "json_parse": json_check,
        "no_monolith": line_check,
        "required_outputs": required,
        "reality_unchanged": {"before": reality_before, "after": reality_after, "verdict": "PASS" if reality_before == reality_after else "BLOCK"},
    }
    failed = [name for name, check in checks.items() if check.get("verdict") not in {"PASS", "PASS_PROVEN"}]
    matrix = {
        "schema_version": "imperium.core_reference_corridor.validation_matrix.v0_1",
        "task_id": TASK_ID,
        "base_head": BASE_HEAD,
        "generated_at_utc": _utc_now(),
        "checks": checks,
        "failed_checks": failed,
        "current_receipts": {
            "validation": validation_evidence_id + ".json",
            "negative_proof": negative_evidence_id + ".json",
            "ui_backend_parity": ui_evidence_id + ".json",
        },
        "self_reference_exclusions": required["self_reference_pending"],
        "verdict": "PASS_PROVEN" if not failed else "BLOCK",
    }
    atomic_write_json(report / "VALIDATION_MATRIX.json", matrix)
    store = EvidenceStore(report)
    _write_envelope(
        store,
        _executed_envelope(
            evidence_id=negative_evidence_id,
            command=pytest_result,
            result=negative,
            context=context,
            pre_git=pre_git,
            post_git=post_git,
            acceptance=[{"check": "20_scenarios", "verdict": "PASS" if negative["phase_acceptance"] == "NEGATIVE_PROOF_HARDENING_PASS" else "BLOCK"}],
            parent_evidence_id=validation_evidence_id,
        ),
    )
    ui_result = {
        "semantic_parity": parity_result,
        "supporting_matrix": "VALIDATION_MATRIX.json",
        "verdict": "PASS_PROVEN"
        if node_parity["verdict"] == "PASS" and parity_result.get("verdict") == "PASS_CORRIDOR_UI_BACKEND_SEMANTIC_PARITY"
        else "BLOCK",
    }
    _write_envelope(
        store,
        _executed_envelope(
            evidence_id=ui_evidence_id,
            command=node_parity,
            result=ui_result,
            context=context,
            pre_git=pre_git,
            post_git=post_git,
            acceptance=[{"check": "semantic_parity", "verdict": "PASS" if ui_result["verdict"] == "PASS_PROVEN" else "BLOCK"}],
            parent_evidence_id=validation_evidence_id,
        ),
    )
    result = {"verdict": matrix["verdict"], "failed_checks": failed, "scenario_count": negative["scenario_count"], "report": str(report / "VALIDATION_MATRIX.json")}
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return result


def _live_git(root: Path) -> dict[str, Any]:
    head = _run(["git", "-C", str(root), "rev-parse", "HEAD"], root, 30)
    status = _run(["git", "-C", str(root), "status", "--porcelain=v1"], root, 30)
    origin = _run(["git", "-C", str(root), "rev-parse", "origin/master"], root, 30)
    return {"head": head["stdout_tail"].strip(), "origin_master": origin["stdout_tail"].strip(), "porcelain": status["stdout_tail"].splitlines(), "verdict": "PASS" if head["exit_code"] == status["exit_code"] == origin["exit_code"] == 0 else "BLOCK"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", required=True)
    parser.parse_args(argv)
    return 0 if validate_and_write()["verdict"] == "PASS_PROVEN" else 2


if __name__ == "__main__":
    raise SystemExit(main())
