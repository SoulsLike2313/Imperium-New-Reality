"""Run and receipt the bounded Phase 4 Rust-to-Python bridge checkpoint."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .registry import atomic_write_json, sha256_file
from .root_resolver import resolve_repository_context


TASK_ID = "IMPERIUM_CORE_TRUTH_HARDENING_0002"
BRIDGE_TASK_ID = "IMPERIUM-CORE-REFERENCE-CORRIDOR-0001"
WARP_ID = "WARP-CORE-REFERENCE-0001"
BASE_HEAD = "281c3a7c8463de7fb64473929fe0ed975f99f595"
PHASE_PASS = "RUST_PYTHON_BRIDGE_HARDENING_PASS"
PHASE_PARTIAL = "RUST_PYTHON_BRIDGE_PARTIAL_NOT_READY"
CAMPAIGN_VERDICT = "TRUTH_HARDENING_PARTIAL_NOT_READY"
REPORT_RELATIVE = Path(
    "ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002"
)
RUST_RELATIVE = Path("SUPPORT/APP_TAURI/src-tauri/src/corridor")

REQUIRED_TESTS = (
    "phase4_01_admitted_absolute_python_works",
    "phase4_02_bare_python_is_rejected",
    "phase4_03_path_hijack_is_rejected",
    "phase4_04_executable_hash_mismatch_is_rejected",
    "phase4_05_cwd_escape_is_rejected_before_spawn",
    "phase4_06_shell_metacharacters_remain_inert_argv",
    "phase4_07_secret_like_environment_variables_are_excluded",
    "phase4_08_stdout_and_stderr_are_captured_separately",
    "phase4_09_timeout_kills_parent_child_and_grandchild",
    "phase4_10_bridge_receipt_has_task_warp_and_base_bindings",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _run(argv: list[str], cwd: Path, timeout: int) -> dict[str, Any]:
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
        "cwd": str(cwd),
        "started_at_utc": started,
        "ended_at_utc": _utc_now(),
        "timeout_seconds": timeout,
        "exit_code": completed.returncode,
        "stdout_sha256": hashlib.sha256(completed.stdout.encode()).hexdigest(),
        "stderr_sha256": hashlib.sha256(completed.stderr.encode()).hexdigest(),
        "stdout_tail": completed.stdout[-6000:],
        "stderr_tail": completed.stderr[-6000:],
        "verdict": "PASS" if completed.returncode == 0 else "BLOCK",
        "_stdout": completed.stdout,
        "_stderr": completed.stderr,
    }


def _public(result: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in result.items() if not key.startswith("_")}


def _git_value(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        shell=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=True,
    )
    return completed.stdout.strip()


def _git_state(root: Path) -> dict[str, Any]:
    return {
        "root": str(root),
        "head": _git_value(root, "rev-parse", "HEAD"),
        "origin_master": _git_value(root, "rev-parse", "origin/master"),
        "branch": _git_value(root, "branch", "--show-current"),
        "status_porcelain": _git_value(root, "status", "--porcelain=v1").splitlines(),
    }


def _git_status_lines(root: Path) -> list[str]:
    completed = subprocess.run(
        ["git", "-C", str(root), "status", "--short"],
        shell=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=True,
    )
    return completed.stdout.splitlines()


def _junit(path: Path) -> dict[str, Any]:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    result = {
        "path": path.name,
        "sha256": sha256_file(path),
        "tests": sum(int(suite.attrib.get("tests", 0)) for suite in suites),
        "failures": sum(int(suite.attrib.get("failures", 0)) for suite in suites),
        "errors": sum(int(suite.attrib.get("errors", 0)) for suite in suites),
        "skipped": sum(int(suite.attrib.get("skipped", 0)) for suite in suites),
    }
    result["verdict"] = (
        "PASS"
        if result["tests"] > 0 and result["failures"] == result["errors"] == 0
        else "BLOCK"
    )
    return result


def _receipt_hash(value: dict[str, Any]) -> str:
    clone = dict(value)
    clone.pop("receipt_hash", None)
    payload = json.dumps(clone, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def _source_checks(root: Path) -> tuple[dict[str, bool], dict[str, str]]:
    source_paths = sorted((root / RUST_RELATIVE).glob("*.rs"))
    sources = {
        path.name: path.read_text(encoding="utf-8")
        for path in source_paths
    }
    bridge = sources["bridge.rs"]
    boundary = sources["process_boundary.rs"]
    job = sources["windows_job.rs"]
    receipt = sources["bridge_receipt.rs"]
    tests = sources["bridge_tests.rs"]
    registry_path = root / (
        "ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001/"
        "CAPABILITY_REGISTRY.json"
    )
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    python_identities = {
        (item["executable_path"], item["executable_sha256"])
        for item in registry["capabilities"]
        if item.get("type") == "PYTHON_MODULE"
    }
    identity_ok = False
    if len(python_identities) == 1:
        executable, expected_hash = next(iter(python_identities))
        path = Path(executable)
        identity_ok = (
            path.is_absolute()
            and path.name.lower() == "python.exe"
            and path.is_file()
            and sha256_file(path).lower() == expected_hash.lower()
        )
    required_test_sources = all(f"fn {name}()" in tests for name in REQUIRED_TESTS)
    lines_ok = all(len(source.splitlines()) <= 500 for source in sources.values())
    checks = {
        "no_bare_python_command": not bool(
            re.search(r"Command::new\s*\(\s*[\"']python(?:\.exe)?[\"']", bridge + boundary)
        ),
        "registry_admits_one_absolute_hashed_python": identity_ok,
        "sha256_checked_at_admission_and_before_spawn": (
            "BRIDGE_EXECUTABLE_HASH_MISMATCH" in boundary
            and "BRIDGE_EXECUTABLE_HASH_CHANGED_BEFORE_SPAWN" in boundary
        ),
        "exact_argv_without_shell": (
            "Command::new(&admission.executable_path)" in boundary
            and ".args(args)" in boundary
            and "shell: false" in receipt
        ),
        "cwd_is_exact_canonical_root": "if cwd != allowed_cwd" in boundary,
        "environment_is_cleared_and_path_not_admitted": (
            ".env_clear()" in boundary
            and 'const INHERITED_ENV_KEYS: [&str; 4] = ["SystemRoot", "WINDIR", "TEMP", "TMP"]'
            in boundary
            and "path_inherited: false" in receipt
        ),
        "timeout_is_bounded": "BRIDGE_TIMEOUT_NOT_ADMITTED" in boundary,
        "windows_job_kills_full_tree": (
            "JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE" in job
            and "AssignProcessToJobObject" in job
            and "TerminateJobObject" in job
        ),
        "receipt_binds_task_warp_base": all(
            token in receipt for token in ["task_id", "warp_id", "base_head", "receipt_hash"]
        ),
        "required_test_sources_present": required_test_sources,
        "production_modules_within_500_lines": lines_ok,
    }
    hashes = {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in [
            *source_paths,
            root / "SUPPORT/APP_TAURI/src-tauri/Cargo.toml",
            root / "SUPPORT/APP_TAURI/src-tauri/Cargo.lock",
            Path(__file__).resolve(),
            registry_path,
        ]
    }
    return checks, hashes


def _write_markdown(path: Path, checkpoint: dict[str, Any]) -> None:
    lines = [
        "# Phase 4 — Rust → Python Bridge Hardening",
        "",
        f"- Phase verdict: `{checkpoint['phase_verdict']}`",
        f"- Campaign verdict: `{checkpoint['campaign_verdict']}`",
        "- Phase 5: `NOT_STARTED`",
        f"- Process-tree termination proven: `{str(checkpoint['process_tree_termination_proven']).lower()}`",
        "- UI changes: `NONE`",
        "- Land: `NOT_PERFORMED`",
        "",
        "## Production boundary",
        "",
        "Absolute registry-pinned `python.exe` and SHA-256 are revalidated before exact-argv, shell-free execution. CWD is the canonical WARP root, the inherited environment is cleared, timeout cleanup uses a Windows Job Object, and every completed process boundary writes an atomic bound receipt.",
        "",
        "## Required targeted tests",
        "",
    ]
    lines.extend(
        f"- `{name}` — `{result['verdict']}`"
        for name, result in checkpoint["required_tests"].items()
    )
    lines.extend(["", "## Validation", ""])
    lines.extend(
        f"- `{name}` — `{result['verdict']}` — exit `{result['exit_code']}`"
        for name, result in checkpoint["commands"].items()
    )
    lines.extend(
        [
            "",
            f"- Python regression: `{checkpoint['python_regression']['tests']} passed`",
            f"- Reality/master unchanged and clean: `{str(checkpoint['checks']['reality_unchanged_and_clean']).lower()}`",
            f"- Checkpoint receipt hash: `{checkpoint['receipt_hash']}`",
            "",
            "## Boundary",
            "",
            "This checkpoint completes Phase 4 only. Phase 5 and every later campaign phase remain unstarted.",
        ]
    )
    if checkpoint["blockers"]:
        lines.extend(["", "## Blockers", ""])
        lines.extend(f"- `{blocker}`" for blocker in checkpoint["blockers"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def validate_phase4() -> dict[str, Any]:
    context = resolve_repository_context(".")
    root = Path(context.worktree_root)
    reality = Path(context.reality_root)
    app = root / "SUPPORT/APP_TAURI"
    manifest = app / "src-tauri/Cargo.toml"
    report = root / REPORT_RELATIVE
    report.mkdir(parents=True, exist_ok=True)
    regression_xml = report / "PHASE_4_REGRESSION_RESULTS.xml"
    cargo = shutil.which("cargo.exe") or shutil.which("cargo") or "cargo"
    npm = shutil.which("npm.cmd") or shutil.which("npm") or "npm.cmd"
    reality_before = _git_state(reality)
    commands = {
        "targeted_rust": _run(
            [
                cargo,
                "test",
                "--manifest-path",
                str(manifest),
                "corridor::bridge_tests",
                "--",
                "--test-threads=1",
            ],
            root,
            600,
        ),
        "full_rust_tests": _run(
            [cargo, "test", "--manifest-path", str(manifest)], root, 600
        ),
        "cargo_check": _run(
            [cargo, "check", "--manifest-path", str(manifest)], root, 600
        ),
        "npm_build": _run([npm, "run", "build"], app, 300),
        "full_python_regression": _run(
            [
                sys.executable,
                "-m",
                "pytest",
                "ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests",
                "-q",
                "-p",
                "no:cacheprovider",
                "--junitxml",
                str(regression_xml),
            ],
            root,
            600,
        ),
        "git_diff_check": _run(["git", "diff", "--check"], root, 60),
    }
    reality_after = _git_state(reality)
    source_checks, source_hashes = _source_checks(root)
    targeted_output = commands["targeted_rust"]["_stdout"]
    required_tests = {
        name: {
            "verdict": (
                "PASS"
                if commands["targeted_rust"]["exit_code"] == 0
                and f"test corridor::bridge_tests::{name} ... ok" in targeted_output
                else "BLOCK"
            )
        }
        for name in REQUIRED_TESTS
    }
    regression = _junit(regression_xml)
    command_checks = {
        name: result["exit_code"] == 0 for name, result in commands.items()
    }
    status_lines = _git_status_lines(root)
    changed = [line[3:] for line in status_lines if len(line) >= 4]
    reality_ok = (
        reality_before == reality_after
        and not reality_after["status_porcelain"]
        and reality_after["head"] == reality_after["origin_master"] == BASE_HEAD
    )
    process_tree_proven = (
        required_tests["phase4_09_timeout_kills_parent_child_and_grandchild"]["verdict"]
        == "PASS"
    )
    checks = {
        **source_checks,
        "all_required_targeted_tests_passed": all(
            item["verdict"] == "PASS" for item in required_tests.values()
        ),
        "all_validation_commands_passed": all(command_checks.values()),
        "full_python_regression_passed": regression["verdict"] == "PASS",
        "process_tree_termination_proven": process_tree_proven,
        "reality_unchanged_and_clean": reality_ok,
        "no_ui_source_changes": not any(
            path.startswith("SUPPORT/APP_TAURI/src/") for path in changed
        ),
    }
    blockers = [name for name, passed in checks.items() if not passed]
    phase_verdict = PHASE_PASS if not blockers else PHASE_PARTIAL
    checkpoint: dict[str, Any] = {
        "schema_version": "imperium.core_reference_corridor.phase4_checkpoint.v1",
        "task_id": TASK_ID,
        "generated_at_utc": _utc_now(),
        "phase": "PHASE_4_RUST_TO_PYTHON_BRIDGE_HARDENING",
        "phase_verdict": phase_verdict,
        "campaign_verdict": CAMPAIGN_VERDICT,
        "phase_5_started": False,
        "bridge_binding": {
            "task_id": BRIDGE_TASK_ID,
            "warp_id": WARP_ID,
            "base_head": BASE_HEAD,
        },
        "process_tree_termination_proven": process_tree_proven,
        "required_tests": required_tests,
        "commands": {name: _public(result) for name, result in commands.items()},
        "command_checks": command_checks,
        "python_regression": regression,
        "source_hashes": source_hashes,
        "reality_before": reality_before,
        "reality_after": reality_after,
        "changed_paths": changed,
        "checks": checks,
        "blockers": blockers,
        "ui_changes": [],
        "land_performed": False,
    }
    checkpoint["receipt_hash"] = _receipt_hash(checkpoint)
    json_path = report / "PHASE_4_CHECKPOINT.json"
    md_path = report / "PHASE_4_CHECKPOINT.md"
    atomic_write_json(json_path, checkpoint)
    _write_markdown(md_path, checkpoint)
    print(
        json.dumps(
            {
                "phase_verdict": phase_verdict,
                "blockers": blockers,
                "python_regression_tests": regression["tests"],
                "process_tree_termination_proven": process_tree_proven,
                "reality_unchanged_and_clean": reality_ok,
            },
            sort_keys=True,
        )
    )
    return checkpoint


def main() -> int:
    return 0 if validate_phase4()["phase_verdict"] == PHASE_PASS else 2


if __name__ == "__main__":
    raise SystemExit(main())
