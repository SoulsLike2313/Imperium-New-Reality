#!/usr/bin/env python3
"""Build sample requests for Transfer Action Runner foundation."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ACTION-RUNNER-VM3-V0_1"
BASE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE"
RUNNER_REL = f"{BASE_REL}/TOOLS/transfer_action_runner_v0_1.py"
SAMPLES_DIR_REL = f"{BASE_REL}/DATA/samples"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def relpath(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


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


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[4]
    default_report_dir = default_repo_root / f"{BASE_REL}/REPORTS/{TASK_ID_DEFAULT}"
    default_output = default_report_dir / "transfer_action_samples_build_report.json"

    parser = argparse.ArgumentParser(description="Build sample requests for transfer action runner.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output", type=Path, default=default_output)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    report_dir = args.report_dir.resolve()
    output_path = args.output.resolve()

    samples_dir = repo_root / SAMPLES_DIR_REL
    samples_dir.mkdir(parents=True, exist_ok=True)

    valid_request = {
        "schema_id": "TRANSFER_ACTION_REQUEST_V0_1",
        "request_id": "SAMPLE-VALID-DRY-RUN",
        "task_id": str(args.task_id),
        "action_type": "SEND_TASKPACK_ZIP",
        "source_contour": "PC",
        "target_contour": "VM3",
        "artifact_type": "taskpack_zip",
        "artifact_name": "TASKPACK_TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ACTION-RUNNER-VM3-V0_1.zip",
        "source_path": "INBOX/VM3_TASKPACKS/TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ACTION-RUNNER-VM3-V0_1/TASKPACK_TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ACTION-RUNNER-VM3-V0_1.zip",
        "target_path": "/home/vboxuser3/IMPERIUM_WORK/Imperium-/INBOX/VM3_TASKPACKS/TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ACTION-RUNNER-VM3-V0_1/TASKPACK_RECEIVE_SLOT.zip",
        "mode": "DRY_RUN",
        "owner_approval_required": True,
        "owner_approved": False,
        "rollback_plan": "IMPERIUM_NEW_GENERATION/TRUTH/ACTION_ROLLBACK/ACTION_ROLLBACK_POLICY_V0_1.json",
        "allowed_command_profile": "DRY_RUN_ONLY",
        "created_at_utc": utc_now(),
        "status": "REQUESTED",
        "claim_boundary": "FOUNDATION_ONLY"
    }

    execute_not_approved_request = {
        **valid_request,
        "request_id": "SAMPLE-EXECUTE-NOT-APPROVED",
        "mode": "EXECUTE",
        "owner_approved": False,
        "allowed_command_profile": "PROFILE_NOT_READY"
    }

    unsafe_path_request = {
        **valid_request,
        "request_id": "SAMPLE-UNSAFE-PATH",
        "source_path": "/tmp/unsafe_source.zip",
        "target_path": "/tmp/unsafe_target.zip"
    }

    valid_path = samples_dir / "sample_valid_dry_run_request.json"
    execute_path = samples_dir / "sample_execute_not_approved_request.json"
    unsafe_path = samples_dir / "sample_unsafe_path_request.json"

    write_json(valid_path, valid_request)
    write_json(execute_path, execute_not_approved_request)
    write_json(unsafe_path, unsafe_path_request)

    runner = repo_root / RUNNER_REL
    validate_run = run_cmd(
        [
            "python3",
            str(runner),
            "--repo-root",
            str(repo_root),
            "--task-id",
            str(args.task_id),
            "--action-id",
            "VALIDATE_TRANSFER_REQUEST",
            "--request-file",
            str(valid_path),
            "--report-dir",
            str(report_dir),
            "--output-report",
            str(report_dir / "build_sample_validate_action_report.json"),
        ],
        repo_root,
    )

    dry_run = run_cmd(
        [
            "python3",
            str(runner),
            "--repo-root",
            str(repo_root),
            "--task-id",
            str(args.task_id),
            "--action-id",
            "DRY_RUN_TRANSFER",
            "--request-file",
            str(valid_path),
            "--report-dir",
            str(report_dir),
            "--output-report",
            str(report_dir / "build_sample_dry_run_action_report.json"),
        ],
        repo_root,
    )

    steps = [validate_run, dry_run]
    failures = [step for step in steps if int(step.get("returncode", 1)) != 0]
    statuses = [str(step.get("parsed", {}).get("transfer_action_runner_status", "")) for step in steps]

    verdict = "PASS"
    if failures:
        verdict = "BLOCK"
    elif any(status == "BLOCK" for status in statuses):
        verdict = "WARN"

    report = {
        "schema_id": "TRANSFER_ACTION_SAMPLES_BUILD_REPORT_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "samples": {
            "valid_request": relpath(valid_path, repo_root),
            "execute_not_approved": relpath(execute_path, repo_root),
            "unsafe_path": relpath(unsafe_path, repo_root)
        },
        "runner_steps": steps,
        "claim_boundary": "FOUNDATION_ONLY",
        "known_limitations": [
            "Sample build verifies bounded dry-run/validation flow only.",
            "No production remote orchestration claim is made."
        ]
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"transfer_action_samples_build_verdict={verdict}")
    print(f"transfer_action_samples_build_report={relpath(output_path, repo_root)}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
