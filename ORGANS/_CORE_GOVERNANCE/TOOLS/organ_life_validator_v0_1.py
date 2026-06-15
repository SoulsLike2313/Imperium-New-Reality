#!/usr/bin/env python3
"""Validate Imperium organ life-zone mappings V0.1."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260605-PC-IMPERIUM-CORE-SHAPE-ORGAN-LIFE-METRICS-QUARANTINE-V0_1"
REGISTRY = Path("ORGANS/_CORE_GOVERNANCE/REQUIRED_9_ORGANS_V0_1.json")
REQUIRED_SCHEMAS = [
    "organ_card.schema.json",
    "organ_life_receipt.schema.json",
    "support_classification.schema.json",
    "quarantine_item.schema.json",
    "core_file_ownership_entry.schema.json",
    "core_self_validation_report.schema.json",
    "organ_metric.schema.json",
    "organ_matrix.schema.json",
]
REQUIRED_TEMPLATES = [
    "ORGAN_CARD_TEMPLATE.json",
    "ORGAN_LIFE_RECEIPT_TEMPLATE.json",
    "SUPPORT_CLASSIFICATION_TEMPLATE.json",
    "QUARANTINE_ITEM_TEMPLATE.json",
    "CORE_ALERT_TEMPLATE.json",
]
TASK_REQUIRED_ORGAN_ZONES = {
    "ADMINISTRATUM": ["ORGANS/ADMINISTRATUM/ADDRESS_BOOK"],
    "STRATEGIUM": ["ORGANS/STRATEGIUM/METRICS"],
    "SCHOLA_IMPERIALIS": ["ORGANS/SCHOLA_IMPERIALIS/LEARNING"],
    "INQUISITION": ["ORGANS/INQUISITION/QUARANTINE_POLICY"],
    "CUSTODES": ["ORGANS/CUSTODES/ORGAN_LIFE_AUDIT"],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_report(repo_root: Path, task_id: str) -> dict[str, Any]:
    warnings: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    registry_path = repo_root / REGISTRY
    if not registry_path.exists():
        return {
            "schema_version": "imperium.organ_life_validation_report.v0_1",
            "task_id": task_id,
            "timestamp_utc": utc_now(),
            "verdict": "BLOCK",
            "organ_checks": [],
            "schema_checks": [],
            "template_checks": [],
            "warnings": [],
            "blockers": [{"id": "MISSING_REQUIRED_ORGAN_REGISTRY", "path": str(REGISTRY)}],
            "next_action": "Create required 9-organ registry.",
        }
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    organs = registry.get("required_organs", [])
    if len(organs) != 9:
        blockers.append({"id": "REQUIRED_ORGAN_COUNT_NOT_9", "count": len(organs)})

    organ_checks = []
    for entry in organs:
        organ_id = entry.get("organ_id", "UNKNOWN")
        root_path = entry.get("root_path", "")
        life_zone_path = entry.get("life_zone_path", root_path)
        root_exists = bool(root_path) and (repo_root / root_path).is_dir()
        life_zone_exists = bool(life_zone_path) and (repo_root / life_zone_path).is_dir()
        required_zone_checks = []
        for rel in TASK_REQUIRED_ORGAN_ZONES.get(organ_id, []):
            exists = (repo_root / rel).is_dir()
            required_zone_checks.append({"path": rel, "exists": exists})
            if not exists:
                blockers.append({"id": "MISSING_TASK_REQUIRED_ORGAN_ZONE", "organ_id": organ_id, "path": rel})
        metadata_candidates = [
            f"{life_zone_path}/IDENTITY/organ_identity_v0_1.md",
            f"{life_zone_path}/TASK_PARTICIPATION",
            f"{life_zone_path}/ORGAN_LIFE_AUDIT",
            f"{life_zone_path}/ADDRESS_BOOK",
            f"{life_zone_path}/METRICS",
            f"{life_zone_path}/LEARNING",
            f"{life_zone_path}/QUARANTINE_POLICY",
        ]
        metadata_present = any((repo_root / rel).exists() for rel in metadata_candidates)
        if not metadata_present:
            warnings.append({"id": "ORGAN_METADATA_MINIMUM_GAP", "organ_id": organ_id})
        if not root_exists or not life_zone_exists:
            blockers.append({"id": "MISSING_ORGAN_LIFE_ZONE", "organ_id": organ_id, "root_path": root_path, "life_zone_path": life_zone_path})
        organ_checks.append({
            "organ_id": organ_id,
            "root_path": root_path,
            "root_exists": root_exists,
            "life_zone_path": life_zone_path,
            "life_zone_exists": life_zone_exists,
            "metadata_present": metadata_present,
            "task_required_zone_checks": required_zone_checks,
            "status": "BLOCK" if not root_exists or not life_zone_exists else ("PASS" if metadata_present else "PASS_WITH_WARNINGS"),
        })

    schema_checks = []
    for name in REQUIRED_SCHEMAS:
        rel = f"ORGANS/_CORE_GOVERNANCE/SCHEMAS/{name}"
        exists = (repo_root / rel).is_file()
        schema_checks.append({"path": rel, "exists": exists})
        if not exists:
            blockers.append({"id": "MISSING_ORGAN_LIFE_SCHEMA", "path": rel})

    template_checks = []
    for name in REQUIRED_TEMPLATES:
        rel = f"ORGANS/_CORE_GOVERNANCE/TEMPLATES/{name}"
        exists = (repo_root / rel).is_file()
        template_checks.append({"path": rel, "exists": exists})
        if not exists:
            blockers.append({"id": "MISSING_ORGAN_LIFE_TEMPLATE", "path": rel})

    verdict = "BLOCK" if blockers else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    return {
        "schema_version": "imperium.organ_life_validation_report.v0_1",
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "verdict": verdict,
        "organ_checks": organ_checks,
        "schema_checks": schema_checks,
        "template_checks": template_checks,
        "warnings": warnings,
        "blockers": blockers,
        "next_action": "Fill organ metadata gaps in V0.2 while preserving current mapped homes." if warnings else "Use this validator in post-work closure.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--output")
    args = parser.parse_args()
    report = build_report(Path(args.repo_root).resolve(), args.task_id)
    encoded = json.dumps(report, indent=2, ensure_ascii=True) + "\n"
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if report["verdict"] in {"PASS", "PASS_WITH_WARNINGS"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
