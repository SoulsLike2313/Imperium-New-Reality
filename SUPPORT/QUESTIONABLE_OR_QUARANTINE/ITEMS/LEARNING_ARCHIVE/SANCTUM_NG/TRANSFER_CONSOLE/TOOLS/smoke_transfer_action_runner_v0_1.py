#!/usr/bin/env python3
"""Smoke-check bounded PC->VM3 route proof flow."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-PC-TO-VM3-VM3-V0_1"
BASE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE"
RUNNER_REL = f"{BASE_REL}/TOOLS/transfer_action_runner_v0_1.py"
VALIDATOR_REL = f"{BASE_REL}/TOOLS/validate_transfer_action_runner_v0_1.py"
VIEW_STATE_REL = f"{BASE_REL}/DATA/TRANSFER_CONSOLE_VIEW_STATE.generated.json"
EVIDENCE_NAME = "PC_TO_VM3_DELIVERY_EVIDENCE.json"

ROUTE_ACTION = "SEND_TASKPACK_ZIP"
ROUTE_SOURCE = "PC"
ROUTE_TARGET = "VM3"
ROUTE_VERDICT = "PASS_FOR_ONE_CONFIRMED_BOUNDED_PC_TO_VM3_TRANSFER_ROUTE_ONLY"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_kv(stdout: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in stdout.splitlines():
        line = line.strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
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
    default_report_dir = default_repo_root / f"{BASE_REL}/REPORTS/{TASK_ID_DEFAULT}"
    default_output = default_report_dir / "transfer_route_proof_smoke_report.json"
    default_evidence = (
        default_repo_root
        / "INBOX"
        / "VM3_TASKPACKS"
        / TASK_ID_DEFAULT
        / EVIDENCE_NAME
    )

    parser = argparse.ArgumentParser(description="Smoke test bounded PC->VM3 route proof flow.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output", type=Path, default=default_output)
    parser.add_argument("--evidence-file", type=Path, default=default_evidence)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    report_dir = args.report_dir.resolve()
    output_path = args.output.resolve()
    evidence_path = args.evidence_file.resolve()

    steps: list[dict[str, Any]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    report_dir.mkdir(parents=True, exist_ok=True)

    confirm_run = run_cmd(
        [
            "python3",
            str(repo_root / RUNNER_REL),
            "--repo-root",
            str(repo_root),
            "--task-id",
            str(args.task_id),
            "--action-id",
            ROUTE_ACTION,
            "--mode",
            "DRY_RUN",
            "--route-proof-mode",
            "--delivery-evidence-file",
            str(evidence_path),
            "--report-dir",
            str(report_dir),
            "--output-report",
            str(report_dir / "smoke_confirm_action_report.json"),
        ],
        repo_root,
    )
    confirm_status = str(confirm_run.get("parsed", {}).get("transfer_action_runner_status", ""))
    add_step(
        steps,
        warnings,
        blockers,
        "confirm_pc_to_vm3_route",
        confirm_run["returncode"] == 0 and confirm_status == "PASS",
        confirm_run,
        "confirm_pc_to_vm3_route_failed",
    )

    execute_run = run_cmd(
        [
            "python3",
            str(repo_root / RUNNER_REL),
            "--repo-root",
            str(repo_root),
            "--task-id",
            str(args.task_id),
            "--action-id",
            ROUTE_ACTION,
            "--mode",
            "EXECUTE",
            "--route-proof-mode",
            "--delivery-evidence-file",
            str(evidence_path),
            "--report-dir",
            str(report_dir),
        ],
        repo_root,
    )
    execute_status = str(execute_run.get("parsed", {}).get("transfer_action_runner_status", ""))
    add_step(
        steps,
        warnings,
        blockers,
        "execute_mode_rejected",
        execute_run["returncode"] != 0 and execute_status == "BLOCK",
        execute_run,
        "execute_mode_not_rejected",
    )

    bad_route_run = run_cmd(
        [
            "python3",
            str(repo_root / RUNNER_REL),
            "--repo-root",
            str(repo_root),
            "--task-id",
            str(args.task_id),
            "--action-id",
            ROUTE_ACTION,
            "--source-contour",
            "VM2",
            "--target-contour",
            ROUTE_TARGET,
            "--route-proof-mode",
            "--delivery-evidence-file",
            str(evidence_path),
            "--report-dir",
            str(report_dir),
        ],
        repo_root,
    )
    bad_route_status = str(bad_route_run.get("parsed", {}).get("transfer_action_runner_status", ""))
    add_step(
        steps,
        warnings,
        blockers,
        "vm2_route_rejected",
        bad_route_run["returncode"] != 0 and bad_route_status == "BLOCK",
        bad_route_run,
        "vm2_route_not_rejected",
    )

    validator_run = run_cmd(
        [
            "python3",
            str(repo_root / VALIDATOR_REL),
            "--repo-root",
            str(repo_root),
            "--task-id",
            str(args.task_id),
            "--report-dir",
            str(report_dir),
            "--output",
            str(report_dir / "transfer_route_proof_validator_report.json"),
            "--evidence-file",
            str(evidence_path),
        ],
        repo_root,
    )
    validator_status = str(validator_run.get("parsed", {}).get("transfer_route_proof_validator_verdict", ""))
    add_step(
        steps,
        warnings,
        blockers,
        "validator_pass",
        validator_run["returncode"] == 0 and validator_status == "PASS",
        validator_run,
        "validator_not_pass",
    )

    view_payload = load_json(repo_root / VIEW_STATE_REL)
    last_action = (
        view_payload.get("action_runner_state", {}).get("last_action", {})
        if isinstance(view_payload, dict)
        else {}
    )
    view_ok = (
        isinstance(last_action, dict)
        and str(last_action.get("route_proof_status", "")) == "CONFIRMED"
        and str(last_action.get("route_proof_verdict", "")) == ROUTE_VERDICT
        and str(last_action.get("route", "")) == f"{ROUTE_SOURCE}->{ROUTE_TARGET}"
    )
    add_step(
        steps,
        warnings,
        blockers,
        "view_state_route_proof_visible",
        view_ok,
        {
            "last_action": last_action,
            "view_state_path": VIEW_STATE_REL,
        },
        "view_state_route_proof_not_visible",
    )

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
        "allowed_final_verdict": ROUTE_VERDICT,
        "steps": steps,
        "warnings": warnings,
        "blockers": blockers,
        "claim_boundary": "FOUNDATION_ONLY",
        "not_proven": [
            "VM2 transfer route proof",
            "VM3 to PC report fetch proof",
            "production remote orchestration",
            "arbitrary shell execution",
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"transfer_route_proof_smoke_verdict={verdict}")
    print(f"transfer_route_proof_smoke_report={output_path.relative_to(repo_root).as_posix()}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
