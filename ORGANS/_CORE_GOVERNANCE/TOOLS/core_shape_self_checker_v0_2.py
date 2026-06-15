#!/usr/bin/env python3
"""Imperium core shape self-checker V0.2."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260605-PC-CORE-SHAPE-DRIFT-CLEANUP-MIGRATION-QUEUE-QUARANTINE-GATE-V0_1"
REGISTRY = Path("ORGANS/_CORE_GOVERNANCE/REQUIRED_9_ORGANS_V0_1.json")
REQUIRED_FILES = [
    "ORGANS/_CORE_GOVERNANCE/CORE_SHAPE_CONTRACT_V0_1.md",
    "ORGANS/_CORE_GOVERNANCE/REQUIRED_9_ORGANS_V0_1.json",
    "ORGANS/_CORE_GOVERNANCE/ORGAN_LIFE_ZONE_CONTRACT_V0_1.md",
    "ORGANS/_CORE_GOVERNANCE/SUPPORT_ZONE_CONTRACT_V0_1.md",
    "ORGANS/_CORE_GOVERNANCE/QUARANTINE_USE_BAN_CONTRACT_V0_1.md",
    "ORGANS/_CORE_GOVERNANCE/CORE_SELF_VALIDATION_CONTRACT_V0_1.md",
    "ORGANS/_CORE_GOVERNANCE/TOOLS/core_shape_self_checker_v0_1.py",
    "ORGANS/_CORE_GOVERNANCE/TOOLS/core_shape_self_checker_v0_2.py",
    "ORGANS/_CORE_GOVERNANCE/TOOLS/core_file_classifier_dry_run_v0_2.py",
    "ORGANS/_CORE_GOVERNANCE/TOOLS/core_migration_queue_builder_v0_1.py",
    "ORGANS/_CORE_GOVERNANCE/TOOLS/quarantine_active_use_checker_v0_1.py",
    "ORGANS/_CORE_GOVERNANCE/TOOLS/core_shape_master_check_v0_1.py",
    "ORGANS/CUSTODES/ORGAN_CARD.json",
    "ORGANS/CUSTODES/ORGAN_CONTRACT.md",
    "ORGANS/CUSTODES/READ_FIRST.md",
    "ORGANS/ADMINISTRATUM/MIGRATION_QUEUE/CORE_MIGRATION_QUEUE_CONTRACT_V0_1.md",
    "ORGANS/INQUISITION/QUARANTINE_POLICY/quarantine_active_use_violation_matrix.json",
    "SUPPORT/QUESTIONABLE_OR_QUARANTINE/QUARANTINE_INDEX.json",
]
REQUIRED_SUPPORT_ZONES = [
    "SUPPORT/COMMON_IMPERIUM_SUPPORT",
    "SUPPORT/QUESTIONABLE_OR_QUARANTINE",
]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core_file_classifier_dry_run_v0_2 import build_report as build_classifier_report  # noqa: E402
from quarantine_active_use_checker_v0_1 import build_report as build_quarantine_report  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def load_required_organs(repo_root: Path) -> list[dict[str, Any]]:
    path = repo_root / REGISTRY
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("required_organs", [])


def path_check(repo_root: Path, rel: str, expect_dir: bool | None = None) -> dict[str, Any]:
    path = repo_root / rel
    exists = path.exists()
    is_dir = path.is_dir()
    ok = exists if expect_dir is None else exists and is_dir == expect_dir
    return {"path": rel, "exists": exists, "is_dir": is_dir, "status": "PASS" if ok else "BLOCK"}


def build_report(repo_root: Path, task_id: str) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    warnings: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    organs = load_required_organs(repo_root)
    organ_checks = []
    if len(organs) != 9:
        blockers.append({"id": "REQUIRED_ORGAN_COUNT_NOT_9", "count": len(organs)})
    for entry in organs:
        organ_id = entry.get("organ_id", "UNKNOWN")
        root_path = entry.get("root_path", "")
        life_zone_path = entry.get("life_zone_path", root_path)
        root_exists = bool(root_path) and (repo_root / root_path).is_dir()
        life_zone_exists = bool(life_zone_path) and (repo_root / life_zone_path).is_dir()
        metadata_paths = [
            f"{life_zone_path}/ORGAN_CARD.json",
            f"{life_zone_path}/ORGAN_CONTRACT.md",
            f"{life_zone_path}/READ_FIRST.md",
            f"{life_zone_path}/TASK_PARTICIPATION",
            f"{life_zone_path}/IDENTITY",
        ]
        metadata_present = any((repo_root / rel).exists() for rel in metadata_paths)
        if not root_exists or not life_zone_exists:
            blockers.append({"id": "MISSING_REQUIRED_ORGAN_HOME", "organ_id": organ_id, "root_path": root_path, "life_zone_path": life_zone_path})
        elif not metadata_present:
            warnings.append({"id": "ORGAN_METADATA_GAP", "organ_id": organ_id, "meaning": "Life zone exists but minimum metadata still needs enrichment."})
        organ_checks.append(
            {
                "organ_id": organ_id,
                "root_path": root_path,
                "root_exists": root_exists,
                "life_zone_path": life_zone_path,
                "life_zone_exists": life_zone_exists,
                "metadata_present": metadata_present,
                "status": "PASS" if root_exists and life_zone_exists and metadata_present else ("PASS_WITH_WARNINGS" if root_exists and life_zone_exists else "BLOCK"),
            }
        )

    file_checks = [path_check(repo_root, rel) for rel in REQUIRED_FILES]
    for item in file_checks:
        if item["status"] == "BLOCK":
            blockers.append({"id": "MISSING_REQUIRED_CORE_FILE", "path": item["path"]})

    support_checks = [path_check(repo_root, rel, expect_dir=True) for rel in REQUIRED_SUPPORT_ZONES]
    for item in support_checks:
        if item["status"] == "BLOCK":
            blockers.append({"id": "MISSING_REQUIRED_SUPPORT_ZONE", "path": item["path"]})

    classifier = build_classifier_report(repo_root, task_id, max_entries=5000)
    quarantine = build_quarantine_report(repo_root, task_id)
    drift_counts = classifier.get("drift_type_counts", {})
    classification_counts = classifier.get("classification_counts", {})
    if classification_counts.get("UNKNOWN_OWNER", 0):
        warnings.append({"id": "UNKNOWN_OWNER_CLASSIFICATIONS_PRESENT", "count": classification_counts["UNKNOWN_OWNER"]})
    for drift_id in ["REGISTRY_DRIFT", "TASK_INBOX_RESIDUE", "POST_WORK_RESIDUE", "FUTURE_SCOPE"]:
        if drift_counts.get(drift_id, 0):
            warnings.append({"id": f"{drift_id}_PRESENT", "count": drift_counts[drift_id]})
    if quarantine["verdict"] == "BLOCK":
        blockers.extend(quarantine.get("blockers", []))

    if blockers:
        verdict = "BLOCK"
    elif warnings or classifier["verdict"] == "PASS_WITH_WARNINGS":
        verdict = "PASS_WITH_WARNINGS"
    else:
        verdict = "PASS"
    return {
        "schema_version": "imperium.core_self_validation_report.v0_2",
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "repo_root": str(repo_root).replace("\\", "/"),
        "verdict": verdict,
        "required_organ_count": len(organs),
        "organ_checks": organ_checks,
        "required_file_checks": file_checks,
        "support_zone_checks": support_checks,
        "classifier_verdict": classifier["verdict"],
        "classification_counts": classification_counts,
        "drift_type_counts": drift_counts,
        "quarantine_active_use_verdict": quarantine["verdict"],
        "quarantine_active_use_violation_count": quarantine["active_use_violation_count"],
        "distinguished_drift_classes": [
            "ACTIVE_ORGAN",
            "COMMON_SUPPORT",
            "ACCEPTED_LEGACY",
            "UNKNOWN_OWNER",
            "QUARANTINE_ZONE",
            "REGISTRY_DRIFT",
            "TASK_INBOX_RESIDUE",
            "POST_WORK_RESIDUE",
            "FUTURE_SCOPE",
            "ACTIVE_USE_REFERENCE",
        ],
        "warnings": warnings,
        "blockers": blockers,
        "next_action": "Commit classified registry/taskpack residue and keep quarantine active-use checker in the post-work gate.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Imperium core shape V0.2.")
    parser.add_argument("--repo-root", "--root", dest="repo_root", default=".")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--output", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(Path(args.repo_root), args.task_id)
    if args.output:
        write_json(Path(args.output), report)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["verdict"] in {"PASS", "PASS_WITH_WARNINGS"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
