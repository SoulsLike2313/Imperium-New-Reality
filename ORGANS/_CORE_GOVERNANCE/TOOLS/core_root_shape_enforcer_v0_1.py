#!/usr/bin/env python3
"""Run the physical root migration executor and active root checker."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


TASK_ID_DEFAULT = "TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1"
REPORT_DIR_DEFAULT = f"REPORTS/{TASK_ID_DEFAULT}"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def run_command(repo_root: Path, command: list[str]) -> dict:
    proc = subprocess.run(command, cwd=repo_root, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    return {
        "command": command,
        "exit_code": proc.returncode,
        "stdout_tail": proc.stdout[-3000:],
        "stderr_tail": proc.stderr[-3000:],
        "status": "PASS" if proc.returncode == 0 else "BLOCK",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enforce root shape with migration and checker tools.")
    parser.add_argument("--root", "--repo-root", dest="repo_root", default=".")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", default=REPORT_DIR_DEFAULT)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--out", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    report_dir = Path(args.report_dir)
    executor_command = [
        "python",
        "ORGANS/_CORE_GOVERNANCE/TOOLS/core_migration_executor_v0_1.py",
        "--root",
        ".",
        "--task-id",
        args.task_id,
        "--report-out",
        str(report_dir / "CORE_PHYSICAL_MIGRATION_REPORT.json"),
        "--receipt-out",
        str(report_dir / "CORE_MIGRATION_EXECUTION_RECEIPT.json"),
    ]
    if args.apply:
        executor_command.append("--apply")
    checker_command = [
        "python",
        "ORGANS/_CORE_GOVERNANCE/TOOLS/core_active_root_allowlist_checker_v0_1.py",
        "--root",
        ".",
        "--task-id",
        args.task_id,
        "--out",
        str(report_dir / "CORE_ACTIVE_ROOT_ALLOWLIST_CHECK_REPORT.json"),
    ]
    rows = [run_command(repo_root, executor_command), run_command(repo_root, checker_command)]
    blockers = [row for row in rows if row["exit_code"] != 0]
    report = {
        "schema_version": "imperium.core_root_shape_enforcer_report.v0_1",
        "task_id": args.task_id,
        "created_at_utc": utc_now(),
        "mode": "APPLY" if args.apply else "DRY_RUN",
        "commands": rows,
        "verdict": "BLOCK" if blockers else "PASS",
        "blockers": blockers,
    }
    out = Path(args.out) if args.out else report_dir / "CORE_ROOT_SHAPE_ENFORCER_REPORT.json"
    write_json(out, report)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if not blockers else 2


if __name__ == "__main__":
    raise SystemExit(main())
