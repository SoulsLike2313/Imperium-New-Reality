#!/usr/bin/env python3
"""Build the dry-run core migration queue from the V0.2 classifier."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260605-PC-CORE-SHAPE-DRIFT-CLEANUP-MIGRATION-QUEUE-QUARANTINE-GATE-V0_1"
DEFAULT_QUEUE_OUT = "ORGANS/ADMINISTRATUM/MIGRATION_QUEUE/core_migration_queue_v0_1.json"
DEFAULT_SUMMARY_OUT = "ORGANS/ADMINISTRATUM/MIGRATION_QUEUE/core_migration_queue_summary.md"
DEFAULT_REPORT_OUT = f"REPORTS/{TASK_ID_DEFAULT}/CORE_MIGRATION_QUEUE_REPORT.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core_file_classifier_dry_run_v0_2 import build_report as build_classifier_report  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def queue_entry_from_classifier(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": entry["path"],
        "classification": entry["classification"],
        "owner_organ": entry["owner_organ"],
        "recommended_action": entry["recommended_action"],
        "active_use_allowed": entry["active_use_allowed"],
        "reason": entry["reason"],
        "risk": entry["risk"],
        "drift_type": entry.get("drift_type", ""),
        "confidence": entry.get("confidence", ""),
        "evidence": entry.get("evidence", []),
        "git_status": entry.get("git_status", ""),
    }


def build_queue(repo_root: Path, task_id: str) -> tuple[dict[str, Any], dict[str, Any], str]:
    classifier = build_classifier_report(repo_root, task_id, max_entries=5000)
    entries = [queue_entry_from_classifier(entry) for entry in classifier["entries"]]
    counts: dict[str, int] = {}
    action_counts: dict[str, int] = {}
    for entry in entries:
        counts[entry["classification"]] = counts.get(entry["classification"], 0) + 1
        action_counts[entry["recommended_action"]] = action_counts.get(entry["recommended_action"], 0) + 1

    blockers: list[dict[str, Any]] = []
    warnings = list(classifier.get("warnings", []))
    if counts.get("UNKNOWN_OWNER", 0):
        warnings.append({"id": "MIGRATION_QUEUE_HAS_UNKNOWN_OWNER", "count": counts["UNKNOWN_OWNER"]})
    if any(entry["recommended_action"] in {"MOVE_TO_ORGAN", "MOVE_TO_SUPPORT", "MOVE_TO_QUARANTINE"} for entry in entries):
        warnings.append({"id": "PHYSICAL_MOVE_RECOMMENDATIONS_ARE_DRY_RUN_ONLY", "meaning": "No move was performed by this task."})

    queue = {
        "schema_version": "imperium.core_migration_queue.v0_1",
        "task_id": task_id,
        "created_at_utc": utc_now(),
        "mode": "DRY_RUN_ONLY",
        "move_or_delete_performed": False,
        "entry_count": len(entries),
        "classification_counts": counts,
        "recommended_action_counts": action_counts,
        "allowed_classifications": ["ORGAN_HOME", "COMMON_SUPPORT", "QUARANTINE_CANDIDATE", "LEGACY_ACCEPTED", "UNKNOWN_OWNER", "FUTURE_SCOPE"],
        "allowed_recommended_actions": ["KEEP", "MOVE_TO_ORGAN", "MOVE_TO_SUPPORT", "MOVE_TO_QUARANTINE", "INVESTIGATE", "FUTURE_SCOPE_HOLD"],
        "entries": entries,
        "warnings": warnings,
        "blockers": blockers,
        "verdict": "PASS_WITH_WARNINGS" if warnings else "PASS",
    }
    report = {
        "schema_version": "imperium.core_migration_queue_report.v0_1",
        "task_id": task_id,
        "created_at_utc": utc_now(),
        "verdict": queue["verdict"],
        "queue_path": DEFAULT_QUEUE_OUT,
        "summary_path": DEFAULT_SUMMARY_OUT,
        "classifier_schema_version": classifier["schema_version"],
        "classifier_verdict": classifier["verdict"],
        "queue_entry_count": len(entries),
        "classification_counts": counts,
        "recommended_action_counts": action_counts,
        "warnings": warnings,
        "blockers": blockers,
        "no_physical_migration_receipt": {
            "move_or_delete_performed": False,
            "import_rewrite_performed": False,
            "scope": "DRY_RUN_QUEUE_ONLY",
        },
    }
    summary_lines = [
        "# Core Migration Queue Summary V0.1",
        "",
        f"Task: {task_id}",
        f"Created: {queue['created_at_utc']}",
        f"Verdict: {queue['verdict']}",
        "",
        "No physical moves, deletes, or import rewrites were performed.",
        "",
        "## Classification Counts",
        "",
    ]
    for key in sorted(counts):
        summary_lines.append(f"- {key}: {counts[key]}")
    summary_lines.extend(["", "## Recommended Action Counts", ""])
    for key in sorted(action_counts):
        summary_lines.append(f"- {key}: {action_counts[key]}")
    summary_lines.extend(["", "## Highest Risk Entries", ""])
    high_risk = [entry for entry in entries if entry["risk"] == "HIGH"][:20]
    if not high_risk:
        summary_lines.append("- None.")
    for entry in high_risk:
        summary_lines.append(f"- {entry['path']}: {entry['classification']} / {entry['recommended_action']}")
    summary = "\n".join(summary_lines) + "\n"
    return queue, report, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build core migration queue V0.1.")
    parser.add_argument("--repo-root", "--root", dest="repo_root", default=".")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--queue-out", default=DEFAULT_QUEUE_OUT)
    parser.add_argument("--report-out", default=DEFAULT_REPORT_OUT)
    parser.add_argument("--summary-out", default=DEFAULT_SUMMARY_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    queue, report, summary = build_queue(Path(args.repo_root), args.task_id)
    write_json(Path(args.queue_out), queue)
    write_json(Path(args.report_out), report)
    write_text(Path(args.summary_out), summary)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["verdict"] in {"PASS", "PASS_WITH_WARNINGS"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
