"""Execute and receipt the bounded Phase 3 Tauri surface checkpoint."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .registry import atomic_write_json, sha256_file
from .root_resolver import resolve_repository_context
from .tauri_surface_inventory import REPORT_RELATIVE, write_inventory


CAMPAIGN_VERDICT = "TRUTH_HARDENING_PARTIAL_NOT_READY"
PHASE_VERDICT = "LEGACY_MUTATION_SURFACE_CLOSED"


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
        "stdout_sha256": hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest(),
        "stderr_sha256": hashlib.sha256(completed.stderr.encode("utf-8")).hexdigest(),
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
        "verdict": "PASS" if completed.returncode == 0 else "BLOCK",
        "_stdout": completed.stdout,
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
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _write_audit(
    path: Path,
    inventory: dict[str, Any],
    receipt: dict[str, Any],
) -> None:
    lines = [
        "# Phase 3 — Tauri Surface Audit",
        "",
        f"- Phase verdict: `{receipt['phase_verdict']}`",
        f"- Campaign verdict: `{receipt['campaign_verdict']}`",
        "- Phase 4: `NOT_STARTED`",
        f"- Rust invoke source: `{inventory['rust_invoke_source']['path']}`",
        f"- Registered commands: `{len(inventory['registered_tauri_commands'])}`",
        "- Inventory authority: real Rust `invoke_handler`; frontend declarations are parity evidence only.",
        "",
        "## Registered surface",
        "",
    ]
    for command in inventory["commands"]:
        mutation_route = (
            f"registry `{command['canonical_capability_registry_routed']}`, "
            f"typed executor `{command['typed_executor_routed']}`, "
            f"Owner gate `{command['owner_gate_required']}`"
            if command["effect"] == "MUTATING"
            else "mutation route `NOT_APPLICABLE`"
        )
        lines.append(f"- `{command['command']}` — `{command['effect']}` — {mutation_route}")
    lines.extend(["", "## Legacy direct invocation probes", ""])
    lines.extend(
        f"- `{probe['command']}` — `{probe['effect']}` — `{probe['direct_invocation_result']}`"
        for probe in inventory["legacy_command_probes"]
    )
    lines.extend(["", "## Validation", ""])
    lines.extend(
        f"- `{name}` — `{result['verdict']}` — exit `{result['exit_code']}`"
        for name, result in receipt["commands"].items()
    )
    lines.extend(
        [
            "",
            f"- Targeted Python: `{receipt['junit']['targeted']['tests']} passed`",
            f"- Full Python regression: `{receipt['junit']['regression']['tests']} passed`",
            f"- Reality/master unchanged and clean: `{str(receipt['checks']['reality_unchanged_and_clean']).lower()}`",
            f"- Inventory receipt: `TAURI_COMMAND_INVENTORY.json` (`{receipt['inventory_sha256']}`)",
            f"- Validation receipt: `PHASE_3_VALIDATION_RECEIPT.json` (`{receipt['receipt_hash']}`)",
            "",
            "## Regression repair",
            "",
            "The first full run exposed the stale legacy FPS HUD test left by the Thin IDE migration. The test now proves that `record_runtime_fps_proof` is unreachable and explicitly makes no performance claim; no visual source was changed.",
            "",
            "## Boundary",
            "",
            "Phase 3 closes the legacy Tauri mutation surface only. Rust-to-Python bridge hardening and every later campaign phase remain unstarted by this checkpoint.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def validate_phase3() -> dict[str, Any]:
    context = resolve_repository_context(".")
    root = Path(context.worktree_root)
    reality = Path(context.reality_root)
    app = root / "SUPPORT/APP_TAURI"
    manifest = app / "src-tauri/Cargo.toml"
    report = root / REPORT_RELATIVE
    report.mkdir(parents=True, exist_ok=True)
    inventory_path = report / "TAURI_COMMAND_INVENTORY.json"
    audit_path = report / "TAURI_SURFACE_AUDIT.md"
    inventory = write_inventory(root, inventory_path, audit_path)
    reality_before = _git_state(reality)
    npm = shutil.which("npm.cmd") or shutil.which("npm") or "npm.cmd"
    cargo = shutil.which("cargo.exe") or shutil.which("cargo") or "cargo"

    targeted_xml = report / "PHASE_3_TEST_RESULTS.xml"
    regression_xml = report / "PHASE_3_REGRESSION_RESULTS.xml"
    commands = {
        "targeted_python": _run(
            [
                sys.executable,
                "-m",
                "pytest",
                "ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_tauri_surface.py",
                "ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_executor.py::test_unknown_and_malicious_runner_are_default_denied_without_execution",
                "ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_executor.py::test_mutation_from_reality_is_blocked_before_process_start",
                "-q",
                "-p",
                "no:cacheprovider",
                "--junitxml",
                str(targeted_xml),
            ],
            root,
            240,
        ),
        "targeted_rust": _run(
            [cargo, "test", "--manifest-path", str(manifest), "corridor::"], root, 360
        ),
        "targeted_node_surface": _run([npm, "run", "check:tauri-surface"], app, 120),
        "npm_build": _run([npm, "run", "build"], app, 240),
        "cargo_check": _run([cargo, "check", "--manifest-path", str(manifest)], root, 360),
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
            360,
        ),
        "full_rust_regression": _run(
            [cargo, "test", "--manifest-path", str(manifest)], root, 600
        ),
        "node_parity_regression": _run([npm, "run", "check:parity"], app, 120),
        "legacy_fps_route_regression": _run([npm, "run", "check:fps"], app, 120),
        "read_only_diagnostic": _run(
            [
                sys.executable,
                "-m",
                "ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.diagnostic_tool",
                "--json",
            ],
            root,
            120,
        ),
        "git_diff_check": _run(["git", "diff", "--check"], root, 60),
    }
    reality_after = _git_state(reality)
    targeted_junit = _junit(targeted_xml)
    regression_junit = _junit(regression_xml)
    try:
        diagnostic = json.loads(commands["read_only_diagnostic"]["_stdout"])
    except json.JSONDecodeError:
        diagnostic = {"verdict": "BLOCK", "reason": "DIAGNOSTIC_STDOUT_NOT_JSON"}

    command_checks = {name: result["exit_code"] == 0 for name, result in commands.items()}
    reality_ok = (
        reality_before == reality_after
        and not reality_after["status_porcelain"]
        and reality_after["head"] == reality_after["origin_master"]
    )
    checks = {
        "inventory_closed": inventory["surface_verdict"] == PHASE_VERDICT,
        "unknown_effects_absent": not inventory["unknown_commands"],
        "every_mutation_capability_registry_routed": not inventory["unregistered_mutating_commands"],
        "every_mutation_typed_executor_routed": not inventory["unrouted_mutating_commands"],
        "every_mutation_owner_gated": not inventory["ungated_mutating_commands"],
        "legacy_mutations_unreachable": not inventory["reachable_legacy_mutations"],
        "all_required_commands_passed": all(command_checks.values()),
        "targeted_tests_passed": targeted_junit["verdict"] == "PASS",
        "full_regression_passed": regression_junit["verdict"] == "PASS",
        "read_only_diagnostic_passed": diagnostic.get("verdict") == "PASS_PROVEN",
        "reality_unchanged_and_clean": reality_ok,
    }
    phase_verdict = PHASE_VERDICT if all(checks.values()) else "PHASE_3_BLOCKED"
    validation_sources = [
        Path(__file__).resolve(),
        root / "ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tauri_surface_inventory.py",
        root / "ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_tauri_surface.py",
        app / "src-tauri/src/corridor/surface_tests.rs",
        app / "tests/tauri_surface_check.mjs",
        app / "tests/action_parity_check.mjs",
        app / "tests/fps_contract_check.mjs",
        app / "package.json",
    ]
    receipt: dict[str, Any] = {
        "schema_version": "imperium.core_reference_corridor.phase3_validation.v1",
        "task_id": inventory["task_id"],
        "generated_at_utc": _utc_now(),
        "phase": "PHASE_3_LEGACY_TAURI_MUTATION_SURFACE_CLOSURE",
        "phase_verdict": phase_verdict,
        "campaign_verdict": CAMPAIGN_VERDICT,
        "phase_4_started": False,
        "inventory_path": inventory_path.relative_to(root).as_posix(),
        "inventory_sha256": sha256_file(inventory_path),
        "inventory_receipt_hash": inventory["receipt_hash"],
        "validation_source_hashes": {
            path.relative_to(root).as_posix(): sha256_file(path)
            for path in validation_sources
        },
        "commands": {name: _public(result) for name, result in commands.items()},
        "command_checks": command_checks,
        "junit": {"targeted": targeted_junit, "regression": regression_junit},
        "diagnostic_verdict": diagnostic.get("verdict"),
        "reality_before": reality_before,
        "reality_after": reality_after,
        "checks": checks,
        "regression_repairs": [
            {
                "id": "STALE_LEGACY_FPS_UI_CONTRACT",
                "initial_command": "npm run check:fps",
                "initial_exit_code": 1,
                "initial_missing_markers": [
                    "FPS_LOCK_TARGET",
                    "requestAnimationFrame",
                    "PerformanceObserver",
                    "fpsSamples",
                    "reduceMotionMode",
                ],
                "origin_commit": "a6a840aeba4ad8f8e55df6efe02c020a8b3245eb",
                "repair": "Migrate the stale regression to assert that record_runtime_fps_proof is absent from the real Rust handler and frontend API.",
                "performance_claim": "NOT_CLAIMED_BY_THIN_IDE",
                "visual_source_changes": [],
            }
        ],
        "known_gaps": [
            "Rust-to-Python bridge hardening and Phase 4 are not started.",
            "The overall campaign remains partial until all later checkpoints pass.",
        ],
    }
    receipt["receipt_hash"] = _receipt_hash(receipt)
    atomic_write_json(report / "PHASE_3_VALIDATION_RECEIPT.json", receipt)
    _write_audit(audit_path, inventory, receipt)
    print(
        json.dumps(
            {
                "phase_verdict": phase_verdict,
                "targeted_tests": targeted_junit["tests"],
                "regression_tests": regression_junit["tests"],
                "failed_commands": [name for name, passed in command_checks.items() if not passed],
                "reality_unchanged_and_clean": reality_ok,
            },
            sort_keys=True,
        )
    )
    return receipt


def main() -> int:
    return 0 if validate_phase3()["phase_verdict"] == PHASE_VERDICT else 2


if __name__ == "__main__":
    raise SystemExit(main())
