#!/usr/bin/env python3
"""Smoke-check scoped transfer route-proof recovery flow."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-RECOVERY-VM2-V0_1"
BASE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE"
REPORT_DIR_REL = f"{BASE_REL}/REPORTS/{TASK_ID_DEFAULT}"
SUMMARY_REL = f"{REPORT_DIR_REL}/route_proof_recovery_summary.json"
OUTPUT_REL = f"{REPORT_DIR_REL}/transfer_route_proof_smoke_report.json"
BUILDER_REL = f"{BASE_REL}/TOOLS/build_transfer_route_proof_recovery_v0_1.py"
VALIDATOR_REL = f"{BASE_REL}/TOOLS/validate_transfer_route_proof_recovery_v0_1.py"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_kv(stdout: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in stdout.splitlines():
        row = line.strip()
        if "=" not in row:
            continue
        key, value = row.split("=", 1)
        out[key.strip()] = value.strip()
    return out


def run_cmd(cmd: list[str], repo_root: Path) -> dict[str, Any]:
    proc = subprocess.run(
        cmd,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "parsed": parse_kv(proc.stdout.strip()),
    }


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def add_step(
    steps: list[dict[str, Any]],
    warnings: list[str],
    blockers: list[str],
    step: str,
    ok: bool,
    details: Any,
    fail_id: str,
    warn: bool = False,
) -> None:
    if ok:
        steps.append({"step": step, "status": "PASS", "details": details})
        return
    status = "WARN" if warn else "BLOCK"
    steps.append({"step": step, "status": status, "details": details})
    if warn:
        warnings.append(fail_id)
    else:
        blockers.append(fail_id)


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[4]
    parser = argparse.ArgumentParser(description="Smoke test transfer route-proof recovery flow.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--summary", type=Path, default=default_repo_root / SUMMARY_REL)
    parser.add_argument("--output", type=Path, default=default_repo_root / OUTPUT_REL)
    parser.add_argument("--report-dir", type=Path, default=default_repo_root / REPORT_DIR_REL)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    output_path = args.output.resolve()
    summary_path = args.summary.resolve()
    report_dir = args.report_dir.resolve()
    report_dir.mkdir(parents=True, exist_ok=True)

    steps: list[dict[str, Any]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    build_run = run_cmd(
        [
            "python3",
            str(repo_root / BUILDER_REL),
            "--repo-root",
            str(repo_root),
            "--task-id",
            str(args.task_id),
            "--report-dir",
            str(report_dir),
            "--output-summary",
            str(summary_path),
        ],
        repo_root,
    )
    builder_verdict = str(build_run.get("parsed", {}).get("transfer_route_recovery_builder_verdict", ""))
    add_step(
        steps,
        warnings,
        blockers,
        "builder_completed",
        build_run["returncode"] == 0 and builder_verdict in {"PASS", "WARN"},
        build_run,
        "builder_failed",
    )

    validator_run = run_cmd(
        [
            "python3",
            str(repo_root / VALIDATOR_REL),
            "--repo-root",
            str(repo_root),
            "--task-id",
            str(args.task_id),
            "--summary",
            str(summary_path),
            "--output",
            str(report_dir / "transfer_route_proof_validator_report.json"),
        ],
        repo_root,
    )
    validator_verdict = str(validator_run.get("parsed", {}).get("transfer_route_proof_validator_verdict", ""))
    add_step(
        steps,
        warnings,
        blockers,
        "validator_completed",
        validator_run["returncode"] == 0 and validator_verdict in {"PASS", "WARN"},
        validator_run,
        "validator_failed",
    )

    summary = load_json(summary_path)
    add_step(
        steps,
        warnings,
        blockers,
        "summary_present_after_build",
        summary is not None,
        {"summary_path": summary_path.as_posix()},
        "summary_missing_after_build",
    )

    if summary is not None:
        routes = summary.get("routes", [])
        route_map: dict[str, str] = {}
        if isinstance(routes, list):
            for item in routes:
                if isinstance(item, dict):
                    route_map[str(item.get("route", ""))] = str(item.get("status", ""))

        pc_vm2 = route_map.get("PC_TO_VM2", "UNKNOWN")
        pc_vm3 = route_map.get("PC_TO_VM3", "UNKNOWN")
        vm2_vm3 = route_map.get("VM2_TO_VM3", "UNKNOWN")

        add_step(
            steps,
            warnings,
            blockers,
            "pc_to_vm2_is_proved",
            pc_vm2 == "PROVED",
            {"PC_TO_VM2": pc_vm2},
            "pc_to_vm2_not_proved",
        )
        add_step(
            steps,
            warnings,
            blockers,
            "pc_to_vm3_status_honest",
            pc_vm3 in {"PROVED", "RECOVERED_PROVED", "WARN_PARTIAL"},
            {"PC_TO_VM3": pc_vm3},
            "pc_to_vm3_status_invalid",
            warn=True,
        )
        add_step(
            steps,
            warnings,
            blockers,
            "vm2_to_vm3_status_honest",
            vm2_vm3 in {"PROVED", "BLOCKED_ROUTE_UNAVAILABLE"},
            {"VM2_TO_VM3": vm2_vm3},
            "vm2_to_vm3_status_invalid",
            warn=True,
        )

        # If VM2->VM3 is blocked-unavailable or PC->VM3 is warn-partial, smoke should not fake full PASS.
        expected_warn = vm2_vm3 == "BLOCKED_ROUTE_UNAVAILABLE" or pc_vm3 == "WARN_PARTIAL"
        add_step(
            steps,
            warnings,
            blockers,
            "no_fake_full_pass_when_partial",
            not expected_warn or validator_verdict == "WARN",
            {
                "expected_warn": expected_warn,
                "validator_verdict": validator_verdict,
            },
            "partial_state_not_reflected_as_warn",
            warn=expected_warn,
        )
        if expected_warn:
            warnings.append("partial_route_state_requires_warn_verdict")

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report = {
        "schema_id": "TRANSFER_ROUTE_PROOF_SMOKE_REPORT_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "allowed_final_verdict": "PASS/WARN_FOR_SCOPED_ROUTE_PROOF_ONLY",
        "steps": steps,
        "warnings": warnings,
        "blockers": blockers,
        "runner_runs": {
            "builder": build_run,
            "validator": validator_run,
        },
        "claim_boundary": "FOUNDATION_ONLY",
        "not_proven": [
            "production orchestration",
            "global live transfer across all contours",
            "arbitrary remote shell execution",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"transfer_route_proof_smoke_verdict={verdict}")
    print(f"transfer_route_proof_smoke_report={output_path.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
