#!/usr/bin/env python3
"""Validate Schola aggressive learning matrix V0.1."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


TASK_ID_DEFAULT = "TASK-20260605-PC-IMPERIUM-CORE-SHAPE-ORGAN-LIFE-METRICS-QUARANTINE-V0_1"
MATRIX = Path("ORGANS/SCHOLA_IMPERIALIS/LEARNING/known_alert_to_preventive_rule_matrix.json")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--output")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    warnings = []
    blockers = []
    matrix_path = repo_root / MATRIX
    rows = []
    if matrix_path.exists():
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
        rows = matrix.get("rows", [])
        for idx, row in enumerate(rows):
            for key in ["alert_id", "preventive_rule", "future_checker_hook"]:
                if not row.get(key):
                    blockers.append({"id": "MISSING_LEARNING_FIELD", "row": idx, "field": key})
    else:
        blockers.append({"id": "MISSING_LEARNING_MATRIX", "path": str(MATRIX)})
    if not rows:
        blockers.append({"id": "NO_LEARNING_ROWS"})
    verdict = "BLOCK" if blockers else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    report = {
        "schema_version": "imperium.schola_learning_capture_report.v0_1",
        "task_id": args.task_id,
        "timestamp_utc": utc_now(),
        "verdict": verdict,
        "checked_evidence": [str(MATRIX)],
        "learning_row_count": len(rows),
        "warnings": warnings,
        "blockers": blockers,
        "next_action": "Promote future_checker_hook rows into executable validators in V0.2.",
    }
    encoded = json.dumps(report, indent=2, ensure_ascii=True) + "\n"
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if verdict in {"PASS", "PASS_WITH_WARNINGS"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
