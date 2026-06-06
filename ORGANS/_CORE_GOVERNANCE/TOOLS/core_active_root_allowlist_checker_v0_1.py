#!/usr/bin/env python3
"""Check active repository root against the strict core shape allowlist."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1"
ADDRESS_BOOK_DEFAULT = "ORGANS/ADMINISTRATUM/ADDRESS_BOOK/physical_root_migration_address_book_v0_1.json"
ALLOWED_ROOT_DIRS = {"ORGANS", "SUPPORT"}
TECHNICAL_ROOT_HOLDS = {
    ".gitignore": "Git ignore policy file must remain at root.",
    "AGENTS.md": "Root agent contract must remain at root.",
    "REPORTS": "Root report evidence is required by current and historical task contracts.",
}
REQUIRED_ORGANS = {
    "ADMINISTRATUM",
    "ASTRONOMICON",
    "CUSTODES",
    "DOCTRINARIUM",
    "INQUISITION",
    "MECHANICUS",
    "OFFICIO_AGENTIS",
    "SCHOLA_IMPERIALIS",
    "STRATEGIUM",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def load_address_book(repo_root: Path, rel_path: str) -> dict[str, Any]:
    path = repo_root / rel_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_hold_map(address_book: dict[str, Any]) -> dict[str, str]:
    holds = dict(TECHNICAL_ROOT_HOLDS)
    for row in address_book.get("hold_items", []):
        path = row.get("path")
        reasons = row.get("hold_reasons", [])
        if isinstance(path, str) and path:
            holds[path] = "; ".join(str(item) for item in reasons) if reasons else "HOLD_WITH_REASON recorded in migration address book."
    return holds


def check_organs(repo_root: Path) -> list[dict[str, Any]]:
    rows = []
    for organ in sorted(REQUIRED_ORGANS):
        path = repo_root / "ORGANS" / organ
        rows.append({"organ_id": organ, "path": f"ORGANS/{organ}", "exists": path.is_dir(), "status": "PASS" if path.is_dir() else "BLOCK"})
    return rows


def build_report(repo_root: Path, task_id: str, address_book_path: str) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    address_book = load_address_book(repo_root, address_book_path)
    hold_map = build_hold_map(address_book)
    root_entries = []
    impurities = []
    holds = []
    for child in sorted(repo_root.iterdir(), key=lambda p: p.name.upper()):
        if child.name == ".git":
            continue
        item = {"name": child.name, "kind": "directory" if child.is_dir() else "file"}
        if child.name in ALLOWED_ROOT_DIRS:
            item["classification"] = "ALLOWED_ACTIVE_ROOT"
            item["status"] = "PASS"
        elif child.name in hold_map:
            item["classification"] = "HOLD_WITH_REASON"
            item["status"] = "PASS_WITH_WARNINGS"
            item["hold_reason"] = hold_map[child.name]
            holds.append(item)
        else:
            item["classification"] = "ACTIVE_ROOT_IMPURITY"
            item["status"] = "BLOCK"
            item["hold_reason"] = ""
            impurities.append(item)
        root_entries.append(item)
    organ_checks = check_organs(repo_root)
    support_checks = [
        {"path": "SUPPORT/COMMON_IMPERIUM_SUPPORT", "exists": (repo_root / "SUPPORT" / "COMMON_IMPERIUM_SUPPORT").is_dir()},
        {"path": "SUPPORT/QUESTIONABLE_OR_QUARANTINE", "exists": (repo_root / "SUPPORT" / "QUESTIONABLE_OR_QUARANTINE").is_dir()},
    ]
    blockers = []
    if impurities:
        blockers.append({"id": "ACTIVE_ROOT_IMPURITY_WITHOUT_HOLD", "count": len(impurities), "items": impurities})
    missing_organs = [row for row in organ_checks if not row["exists"]]
    if missing_organs:
        blockers.append({"id": "MISSING_REQUIRED_ORGAN_HOME", "items": missing_organs})
    missing_support = [row for row in support_checks if not row["exists"]]
    if missing_support:
        blockers.append({"id": "MISSING_REQUIRED_SUPPORT_ZONE", "items": missing_support})
    warnings = []
    if holds:
        warnings.append({"id": "TECHNICAL_OR_SAFETY_HOLDS_REMAIN", "count": len(holds)})
    verdict = "BLOCK" if blockers else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    return {
        "schema_version": "imperium.core_active_root_allowlist_check_report.v0_1",
        "task_id": task_id,
        "created_at_utc": utc_now(),
        "repo_root": str(repo_root).replace("\\", "/"),
        "allowed_root_dirs": sorted(ALLOWED_ROOT_DIRS),
        "active_root_entries": root_entries,
        "active_root_entry_count": len(root_entries),
        "active_root_impurity_count": len(impurities),
        "hold_count": len(holds),
        "remaining_top_level_entries": [item["name"] for item in root_entries],
        "hold_items": holds,
        "impurity_items": impurities,
        "organ_checks": organ_checks,
        "support_checks": support_checks,
        "verdict": verdict,
        "warnings": warnings,
        "blockers": blockers,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check active root allowlist.")
    parser.add_argument("--root", "--repo-root", dest="repo_root", default=".")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--address-book", default=ADDRESS_BOOK_DEFAULT)
    parser.add_argument("--out", "--output", dest="out", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(Path(args.repo_root), args.task_id, args.address_book)
    if args.out:
        write_json(Path(args.out), report)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["verdict"] in {"PASS", "PASS_WITH_WARNINGS"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
