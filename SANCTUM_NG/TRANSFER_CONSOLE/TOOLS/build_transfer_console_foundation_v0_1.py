#!/usr/bin/env python3
"""Build foundation Transfer Console artifacts and emit build report."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-TRANSFER-CONSOLE-VM3-V0_1"
BASE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_command(cmd: list[str], cwd: Path) -> dict[str, Any]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
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
    }


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def count_json_files(path: Path) -> int:
    if not path.exists():
        return 0
    return len(list(path.glob("*.json")))


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[4]
    default_report_dir = default_repo_root / f"{BASE_REL}/REPORTS/{TASK_ID_DEFAULT}"
    parser = argparse.ArgumentParser(description="Build transfer console foundation state.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output", type=Path, default=default_report_dir / "transfer_console_build_report.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    report_dir = args.report_dir.resolve()
    output = args.output.resolve()

    report_dir.mkdir(parents=True, exist_ok=True)
    runner = repo_root / f"{BASE_REL}/TOOLS/transfer_console_action_runner_v0_1.py"
    build_action_report = report_dir / "build_foundation_action_report.json"

    cmd = [
        "python3",
        str(runner),
        "--repo-root",
        str(repo_root),
        "--task-id",
        str(args.task_id),
        "--action-id",
        "BUILD_FOUNDATION",
        "--requester",
        "TRANSFER_CONSOLE_BUILDER",
        "--report-dir",
        str(report_dir),
        "--output-report",
        str(build_action_report),
    ]

    run = run_command(cmd, repo_root)
    build_payload = load_json(build_action_report) or {}

    view_state_path = repo_root / f"{BASE_REL}/DATA/TRANSFER_CONSOLE_VIEW_STATE.generated.json"
    request_dir = repo_root / f"{BASE_REL}/DATA/requests"
    result_dir = repo_root / f"{BASE_REL}/DATA/results"
    probe_dir = repo_root / f"{BASE_REL}/DATA/contours/probes"

    generated_records = {
        "request_records": count_json_files(request_dir),
        "result_records": count_json_files(result_dir),
        "probe_receipts": count_json_files(probe_dir),
    }

    build_status = str(build_payload.get("status", "WARN"))
    verdict = "PASS" if run["returncode"] == 0 and build_status == "PASS" else "WARN"
    if run["returncode"] != 0:
        verdict = "BLOCK"

    report = {
        "schema_id": "TRANSFER_CONSOLE_BUILD_REPORT_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "builder_command": cmd,
        "runner_result": run,
        "build_action_report": (
            build_action_report.relative_to(repo_root).as_posix() if build_action_report.exists() else "MISSING"
        ),
        "view_state_path": view_state_path.relative_to(repo_root).as_posix() if view_state_path.exists() else "MISSING",
        "generated_records": generated_records,
        "verdict": verdict,
        "claim_boundary": "FOUNDATION_ONLY",
        "notes": [
            "Foundation build seeds contour probes and dry-run transfer records.",
            "No live SEND/FETCH claim is produced by this builder.",
        ],
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"transfer_console_build_verdict={verdict}")
    print(f"transfer_console_build_report={output.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
