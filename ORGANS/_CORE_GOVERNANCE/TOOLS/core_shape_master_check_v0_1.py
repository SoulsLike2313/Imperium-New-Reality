#!/usr/bin/env python3
"""Run the core shape checker suite and aggregate command receipts."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260605-PC-CORE-SHAPE-DRIFT-CLEANUP-MIGRATION-QUEUE-QUARANTINE-GATE-V0_1"
REPORT_DIR_DEFAULT = f"REPORTS/{TASK_ID_DEFAULT}"
TOOLS_DIR = Path("ORGANS/_CORE_GOVERNANCE/TOOLS")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def command_row(repo_root: Path, command: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        command,
        cwd=repo_root,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    return {
        "command": command,
        "exit_code": proc.returncode,
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-4000:],
        "status": "PASS" if proc.returncode == 0 else "BLOCK",
    }


def build_commands(task_id: str, report_dir: str) -> list[list[str]]:
    return [
        [
            "python",
            str(TOOLS_DIR / "core_shape_self_checker_v0_1.py"),
            "--repo-root",
            ".",
            "--task-id",
            task_id,
            "--output",
            str(Path(report_dir) / "CORE_SELF_VALIDATION_REPORT_V0_1_COMPAT.json"),
        ],
        [
            "python",
            str(TOOLS_DIR / "core_file_classifier_dry_run_v0_2.py"),
            "--repo-root",
            ".",
            "--task-id",
            task_id,
            "--output",
            str(Path(report_dir) / "CORE_FILE_CLASSIFIER_DRY_RUN_REPORT.json"),
        ],
        [
            "python",
            str(TOOLS_DIR / "core_migration_queue_builder_v0_1.py"),
            "--repo-root",
            ".",
            "--task-id",
            task_id,
            "--queue-out",
            "ORGANS/ADMINISTRATUM/MIGRATION_QUEUE/core_migration_queue_v0_1.json",
            "--summary-out",
            "ORGANS/ADMINISTRATUM/MIGRATION_QUEUE/core_migration_queue_summary.md",
            "--report-out",
            str(Path(report_dir) / "CORE_MIGRATION_QUEUE_REPORT.json"),
        ],
        [
            "python",
            str(TOOLS_DIR / "quarantine_active_use_checker_v0_1.py"),
            "--repo-root",
            ".",
            "--task-id",
            task_id,
            "--output",
            str(Path(report_dir) / "QUARANTINE_ACTIVE_USE_CHECK_REPORT.json"),
        ],
        [
            "python",
            str(TOOLS_DIR / "organ_life_validator_v0_1.py"),
            "--repo-root",
            ".",
            "--task-id",
            task_id,
            "--output",
            str(Path(report_dir) / "ORGAN_LIFE_VALIDATION_REPORT.json"),
        ],
        [
            "python",
            str(TOOLS_DIR / "core_shape_self_checker_v0_2.py"),
            "--repo-root",
            ".",
            "--task-id",
            task_id,
            "--output",
            str(Path(report_dir) / "CORE_SELF_VALIDATION_REPORT.json"),
        ],
    ]


def build_report(repo_root: Path, task_id: str, report_dir: str) -> dict[str, Any]:
    rows = [command_row(repo_root, command) for command in build_commands(task_id, report_dir)]
    blockers = [
        {
            "id": "SUBCHECK_FAILED",
            "command": row["command"],
            "exit_code": row["exit_code"],
            "stderr_tail": row["stderr_tail"],
        }
        for row in rows
        if row["exit_code"] != 0
    ]
    return {
        "schema_version": "imperium.core_shape_master_check_report.v0_1",
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "repo_root": str(repo_root.resolve()).replace("\\", "/"),
        "report_dir": report_dir,
        "verdict": "BLOCK" if blockers else "PASS",
        "command_count": len(rows),
        "commands": rows,
        "blockers": blockers,
        "warnings": [],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run core shape master check V0.1.")
    parser.add_argument("--repo-root", "--root", dest="repo_root", default=".")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", default=REPORT_DIR_DEFAULT)
    parser.add_argument("--output", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(Path(args.repo_root), args.task_id, args.report_dir)
    out = Path(args.output) if args.output else Path(args.report_dir) / "CORE_SHAPE_MASTER_CHECK_REPORT.json"
    write_json(out, report)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["verdict"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
