#!/usr/bin/env python3
"""Dry-run classifier for Imperium core file ownership V0.1."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260605-PC-IMPERIUM-CORE-SHAPE-ORGAN-LIFE-METRICS-QUARANTINE-V0_1"
REGISTRY = Path("ORGANS/_CORE_GOVERNANCE/REQUIRED_9_ORGANS_V0_1.json")
LEGACY_ORGAN_TOP_LEVEL = {
    "ADMINISTRATUM",
    "ASTRONOMICON",
    "DOCTRINARIUM",
    "INQUISITION",
    "MECHANICUS",
    "OFFICIO_AGENTIS",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_organs(repo_root: Path) -> list[str]:
    registry = json.loads((repo_root / REGISTRY).read_text(encoding="utf-8"))
    return [entry["organ_id"] for entry in registry["required_organs"]]


def classify_path(rel_path: str, required_organs: set[str]) -> dict[str, Any]:
    parts = rel_path.replace("\\", "/").split("/")
    top = parts[0]
    if top == "ORGANS" and len(parts) == 1:
        return {"classification": "CORE_CONTAINER", "owner_organ": "ADMINISTRATUM", "confidence": "HIGH", "next_action": "container for required organs and core governance"}
    if top == "ORGANS" and len(parts) > 1 and parts[1] in required_organs:
        return {"classification": "ORGAN_OWNED", "owner_organ": parts[1], "confidence": "HIGH", "next_action": "keep under organ authority"}
    if top == "ORGANS" and len(parts) > 1 and parts[1] == "_CORE_GOVERNANCE":
        return {"classification": "CORE_GOVERNANCE", "owner_organ": "ADMINISTRATUM", "confidence": "HIGH", "next_action": "keep under governance authority"}
    if top == "ORGANS" and len(parts) > 1 and parts[1] == "_POST_WORK_RING":
        return {"classification": "COMMON_SUPPORT", "owner_organ": "ADMINISTRATUM", "confidence": "MEDIUM", "next_action": "preserve until post-work authority migrates or is mapped"}
    if top == "SUPPORT" and len(parts) > 1 and parts[1] == "COMMON_IMPERIUM_SUPPORT":
        return {"classification": "COMMON_SUPPORT", "owner_organ": "ADMINISTRATUM", "confidence": "HIGH", "next_action": "admitted common support"}
    if top == "SUPPORT" and len(parts) > 1 and parts[1] == "QUESTIONABLE_OR_QUARANTINE":
        return {"classification": "QUESTIONABLE_OR_QUARANTINE", "owner_organ": "INQUISITION", "confidence": "HIGH", "next_action": "active use banned unless salvage receipt exists"}
    if top == "SUPPORT" and len(parts) == 1:
        return {"classification": "SUPPORT_CONTAINER", "owner_organ": "ADMINISTRATUM", "confidence": "HIGH", "next_action": "container for common support and quarantine"}
    if top == "REPORTS":
        return {"classification": "COMMON_SUPPORT", "owner_organ": "ADMINISTRATUM", "confidence": "MEDIUM", "next_action": "report bundle history; do not treat as organ authority"}
    if top in LEGACY_ORGAN_TOP_LEVEL or top in required_organs:
        owner = top if top in required_organs else top
        return {"classification": "LEGACY_ORGAN_MIRROR", "owner_organ": owner, "confidence": "MEDIUM", "next_action": "dry-run migration candidate only"}
    if top in {"QUARANTINE", "ANCIENT_EMPIRE_REFERENCE.md", "IMPERIUM_NEW_GENERATION"}:
        return {"classification": "QUESTIONABLE_OR_QUARANTINE", "owner_organ": "INQUISITION", "confidence": "MEDIUM", "next_action": "do not use as active source without admission receipt"}
    return {"classification": "UNKNOWN_WITH_REASON", "owner_organ": "ADMINISTRATUM", "confidence": "UNKNOWN_WITH_REASON", "next_action": "requires future address-book classification"}


def build_report(repo_root: Path, task_id: str, max_entries: int) -> dict[str, Any]:
    required_organs = set(load_organs(repo_root))
    entries = []
    counts: dict[str, int] = {}
    scanned_count = 0
    for child in sorted(repo_root.iterdir(), key=lambda p: p.name.upper()):
        if child.name == ".git":
            continue
        rel_path = child.name
        info = classify_path(rel_path, required_organs)
        counts[info["classification"]] = counts.get(info["classification"], 0) + 1
        scanned_count += 1
        if len(entries) < max_entries:
            entries.append({
                "schema_version": "imperium.core_file_ownership_entry.v0_1",
                "path": rel_path,
                "kind": "directory" if child.is_dir() else "file",
                "dry_run_only": True,
                "move_or_delete_performed": False,
                **info,
                "evidence": ["top-level dry-run classification rule"],
            })
    warnings = []
    if counts.get("UNKNOWN_WITH_REASON", 0):
        warnings.append({"id": "UNKNOWN_CLASSIFICATION_PRESENT", "count": counts["UNKNOWN_WITH_REASON"]})
    if counts.get("LEGACY_ORGAN_MIRROR", 0):
        warnings.append({"id": "LEGACY_ORGAN_MIRROR_PRESENT", "count": counts["LEGACY_ORGAN_MIRROR"], "meaning": "Dry-run only; no physical migration performed."})
    return {
        "schema_version": "imperium.core_file_classifier_dry_run_report.v0_1",
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "verdict": "PASS_WITH_WARNINGS" if warnings else "PASS",
        "mode": "DRY_RUN_ONLY",
        "move_or_delete_performed": False,
        "import_rewrite_performed": False,
        "scanned_top_level_count": scanned_count,
        "reported_entry_limit": max_entries,
        "classification_counts": counts,
        "entries": entries,
        "warnings": warnings,
        "blockers": [],
        "next_action": "Feed UNKNOWN_WITH_REASON rows into Administratum address book classification V0.2.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--max-entries", type=int, default=200)
    parser.add_argument("--output")
    args = parser.parse_args()

    report = build_report(Path(args.repo_root).resolve(), args.task_id, args.max_entries)
    encoded = json.dumps(report, indent=2, ensure_ascii=True) + "\n"
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
