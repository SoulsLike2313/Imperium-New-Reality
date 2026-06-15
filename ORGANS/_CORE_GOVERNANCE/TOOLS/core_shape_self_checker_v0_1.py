#!/usr/bin/env python3
"""Imperium core shape self-checker V0.1.

This checker is intentionally offline and read-only except for an optional JSON
output file selected by the caller.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260605-PC-IMPERIUM-CORE-SHAPE-ORGAN-LIFE-METRICS-QUARANTINE-V0_1"
REGISTRY = Path("ORGANS/_CORE_GOVERNANCE/REQUIRED_9_ORGANS_V0_1.json")
REQUIRED_CORE_FILES = [
    "ORGANS/_CORE_GOVERNANCE/CORE_SHAPE_CONTRACT_V0_1.md",
    "ORGANS/_CORE_GOVERNANCE/REQUIRED_9_ORGANS_V0_1.json",
    "ORGANS/_CORE_GOVERNANCE/ORGAN_LIFE_ZONE_CONTRACT_V0_1.md",
    "ORGANS/_CORE_GOVERNANCE/SUPPORT_ZONE_CONTRACT_V0_1.md",
    "ORGANS/_CORE_GOVERNANCE/QUARANTINE_USE_BAN_CONTRACT_V0_1.md",
    "ORGANS/_CORE_GOVERNANCE/CORE_SELF_VALIDATION_CONTRACT_V0_1.md",
]
REQUIRED_SUPPORT = [
    "SUPPORT/COMMON_IMPERIUM_SUPPORT",
    "SUPPORT/QUESTIONABLE_OR_QUARANTINE",
]
TARGET_TOP_LEVEL = {"ORGANS", "SUPPORT", "REPORTS"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def path_status(repo_root: Path, rel_path: str) -> dict[str, Any]:
    path = repo_root / rel_path
    return {"path": rel_path, "exists": path.exists(), "is_dir": path.is_dir()}


def build_report(repo_root: Path, task_id: str) -> dict[str, Any]:
    warnings: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    alerts: list[dict[str, Any]] = []

    registry_path = repo_root / REGISTRY
    if not registry_path.exists():
        blockers.append({"id": "MISSING_REQUIRED_ORGAN_REGISTRY", "path": str(REGISTRY)})
        organs: list[dict[str, Any]] = []
    else:
        registry = read_json(registry_path)
        organs = registry.get("required_organs", [])
        organ_ids = [entry.get("organ_id") for entry in organs]
        if len(organ_ids) != 9 or len(set(organ_ids)) != 9:
            blockers.append({
                "id": "REQUIRED_ORGAN_COUNT_NOT_EXACTLY_9",
                "count": len(organ_ids),
                "unique_count": len(set(organ_ids)),
            })

    required_organs = []
    for entry in organs:
        organ_id = entry.get("organ_id", "UNKNOWN")
        root_path = entry.get("root_path", "")
        life_zone_path = entry.get("life_zone_path", root_path)
        root_exists = bool(root_path) and (repo_root / root_path).is_dir()
        life_exists = bool(life_zone_path) and (repo_root / life_zone_path).is_dir()
        status = "PASS" if root_exists and life_exists else "BLOCK"
        if status == "BLOCK":
            blockers.append({"id": "MISSING_REQUIRED_ORGAN_LIFE_ZONE", "organ_id": organ_id, "root_path": root_path, "life_zone_path": life_zone_path})
        required_organs.append({
            "organ_id": organ_id,
            "root_path": root_path,
            "root_exists": root_exists,
            "life_zone_path": life_zone_path,
            "life_zone_exists": life_exists,
            "status": status,
        })

    support_zones = {rel: path_status(repo_root, rel) for rel in REQUIRED_SUPPORT}
    for rel, status in support_zones.items():
        if not status["exists"] or not status["is_dir"]:
            blockers.append({"id": "MISSING_SUPPORT_ZONE", "path": rel})

    quarantine_zone = path_status(repo_root, "SUPPORT/QUESTIONABLE_OR_QUARANTINE")

    core_files = [path_status(repo_root, rel) for rel in REQUIRED_CORE_FILES]
    for status in core_files:
        if not status["exists"]:
            blockers.append({"id": "MISSING_CORE_GOVERNANCE_FILE", "path": status["path"]})

    unexpected_top_level = []
    if repo_root.exists():
        for child in sorted(repo_root.iterdir(), key=lambda p: p.name.upper()):
            if child.name.startswith("."):
                continue
            if child.name not in TARGET_TOP_LEVEL:
                item = {
                    "path": child.name,
                    "kind": "directory" if child.is_dir() else "file",
                    "classification": "LEGACY_OR_UNMAPPED_TOP_LEVEL",
                    "required_action": "classify in dry-run before any migration",
                }
                unexpected_top_level.append(item)
        if unexpected_top_level:
            warnings.append({
                "id": "LEGACY_OR_UNMAPPED_TOP_LEVEL_PRESENT",
                "count": len(unexpected_top_level),
                "meaning": "Not a V0.1 blocker; migration is dry-run only in this task.",
            })

    questionable_names = {"QUARANTINE", "SPECULUM", "ANCIENT_EMPIRE_REFERENCE.md", "IMPERIUM_NEW_GENERATION"}
    questionable_candidates = []
    for name in sorted(questionable_names):
        candidate = repo_root / name if name != "SPECULUM" else repo_root / "ORGANS" / name
        if candidate.exists():
            questionable_candidates.append({
                "path": str(candidate.relative_to(repo_root)).replace("\\", "/"),
                "reason": "Name requires explicit classification before active core use.",
            })
    if questionable_candidates:
        alerts.append({
            "id": "QUESTIONABLE_OR_LEGACY_CANDIDATES_PRESENT",
            "severity": "WARN",
            "candidates": questionable_candidates,
        })

    organ_life_minimum_checks = []
    for entry in required_organs:
        organ_id = entry["organ_id"]
        root = repo_root / entry["root_path"]
        expected_identity = root / "IDENTITY" / "organ_identity_v0_1.md"
        expected_task_participation = root / "TASK_PARTICIPATION"
        check = {
            "organ_id": organ_id,
            "life_zone_exists": entry["life_zone_exists"],
            "identity_file_exists": expected_identity.exists(),
            "task_participation_exists": expected_task_participation.exists(),
            "status": "PASS_WITH_WARNINGS",
        }
        if not entry["life_zone_exists"]:
            check["status"] = "BLOCK"
        elif expected_identity.exists() or expected_task_participation.exists():
            check["status"] = "PASS"
        else:
            warnings.append({
                "id": "ORGAN_LIFE_MINIMUM_METADATA_GAP",
                "organ_id": organ_id,
                "meaning": "Life zone exists but identity/task participation metadata is incomplete.",
            })
        organ_life_minimum_checks.append(check)

    if blockers:
        verdict = "BLOCK"
        next_action = "Repair blockers before claiming core shape pass."
    elif warnings or alerts:
        verdict = "PASS_WITH_WARNINGS"
        next_action = "Use dry-run classifier and organ life validator before any migration."
    else:
        verdict = "PASS"
        next_action = "Keep V0.1 checkers in closure bundle."

    return {
        "schema_version": "imperium.core_self_validation_report.v0_1",
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "verdict": verdict,
        "required_organs": required_organs,
        "support_zones": support_zones,
        "quarantine_zone": quarantine_zone,
        "core_governance_files": core_files,
        "unexpected_top_level": unexpected_top_level,
        "unclassified_or_questionable_candidates": questionable_candidates,
        "organ_life_minimum_checks": organ_life_minimum_checks,
        "alerts": alerts,
        "warnings": warnings,
        "blockers": blockers,
        "next_action": next_action,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--output")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    report = build_report(repo_root, args.task_id)
    encoded = json.dumps(report, indent=2, ensure_ascii=True) + "\n"
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if report["verdict"] in {"PASS", "PASS_WITH_WARNINGS"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
