#!/usr/bin/env python3
"""Astronomicon patch-pack inventory.

Script-first, no LLM dependency. Scans WARP/PATCHES and reports which packs
look standard, candidate, legacy, dirty nested, or long-path blocked.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TASK_ID = "ASTRONOMICON-PATCH-PACK-INVENTORY-V0-1"
VERDICT = "PASS_ASTRONOMICON_PATCH_PACK_INVENTORY_READY"
LONG_PATH_LIMIT = 240


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def has_any(path: Path, pattern: str) -> bool:
    return any(path.glob(pattern))


def list_short(paths: list[str], limit: int = 12) -> list[str]:
    return paths[:limit]


def classify_pack(repo_root: Path, pack_dir: Path) -> dict[str, Any]:
    files_to_land = pack_dir / "FILES_TO_LAND"
    patch_pack = pack_dir / "PATCH_PACK.md"
    manifest = pack_dir / "PATCH_FILE_MANIFEST_SHA256.json"
    intent = pack_dir / "INTENT.json"
    polished = pack_dir / "POLISHED_PACK.json"
    runner_paths = sorted(pack_dir.glob("RUN*.ps1"))
    files_to_land_files = [p for p in files_to_land.rglob("*") if p.is_file()] if files_to_land.exists() else []
    nested_warp = [rel(repo_root, p) for p in files_to_land.rglob("WARP/PATCHES/*") if p.exists()] if files_to_land.exists() else []
    candidate_markers = []
    pack_id = pack_dir.name
    if "CANDIDATE" in pack_id.upper():
        candidate_markers.append("id_contains_candidate")
    if intent.exists():
        candidate_markers.append("intent_json")
    if any("TASK_CANDIDATES" in rel(repo_root, p) for p in files_to_land_files):
        candidate_markers.append("task_candidates_payload")
    if polished.exists() or "POLISHED" in pack_id.upper():
        candidate_markers.append("polished_marker")

    required_missing = []
    if not patch_pack.exists():
        required_missing.append("PATCH_PACK.md")
    if not files_to_land.exists():
        required_missing.append("FILES_TO_LAND")
    if not runner_paths:
        required_missing.append("RUN*.ps1")
    if not manifest.exists():
        required_missing.append("PATCH_FILE_MANIFEST_SHA256.json")

    all_tracked_like = [p for p in pack_dir.rglob("*") if p.is_file()]
    long_paths = [rel(repo_root, p) for p in all_tracked_like if len(rel(repo_root, p)) > LONG_PATH_LIMIT]

    if nested_warp:
        classification = "DIRTY_NESTED_WARP_PAYLOAD"
    elif long_paths:
        classification = "LONG_PATH_BLOCKED"
    elif candidate_markers and "polished_marker" not in candidate_markers:
        classification = "REGISTERABLE_CANDIDATE_PACK"
    elif not required_missing:
        classification = "STANDARD_WARP_PATCH_PACK"
    else:
        classification = "LEGACY_OR_INCOMPLETE_PACK"

    return {
        "patch_id": pack_id,
        "classification": classification,
        "required_missing": required_missing,
        "runner_count": len(runner_paths),
        "files_to_land_count": len(files_to_land_files),
        "has_manifest": manifest.exists(),
        "has_patch_pack_md": patch_pack.exists(),
        "has_files_to_land": files_to_land.exists(),
        "candidate_markers": candidate_markers,
        "nested_warp_count": len(nested_warp),
        "nested_warp_examples": list_short(nested_warp, 5),
        "long_path_count": len(long_paths),
        "long_path_examples": list_short(long_paths, 5),
        "modified_time_utc": datetime.fromtimestamp(pack_dir.stat().st_mtime, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }


def build_inventory(repo_root: Path) -> dict[str, Any]:
    warp_root = repo_root / "WARP" / "PATCHES"
    errors: list[str] = []
    warnings: list[str] = []
    if not warp_root.exists():
        errors.append("WARP/PATCHES missing")
        pack_records = []
    else:
        pack_records = [classify_pack(repo_root, p) for p in sorted(warp_root.iterdir()) if p.is_dir()]

    counts: dict[str, int] = {}
    for rec in pack_records:
        counts[rec["classification"]] = counts.get(rec["classification"], 0) + 1

    long_blockers = [r for r in pack_records if r["long_path_count"]]
    dirty_nested = [r for r in pack_records if r["nested_warp_count"]]
    legacy = [r for r in pack_records if r["classification"] == "LEGACY_OR_INCOMPLETE_PACK"]
    candidates = [r for r in pack_records if r["classification"] == "REGISTERABLE_CANDIDATE_PACK"]
    standard = [r for r in pack_records if r["classification"] == "STANDARD_WARP_PATCH_PACK"]

    if dirty_nested:
        warnings.append(f"dirty nested WARP payload packs visible: {len(dirty_nested)}")
    if long_blockers:
        warnings.append(f"long path blocker packs visible: {len(long_blockers)}")
    if legacy:
        warnings.append(f"legacy/incomplete packs visible: {len(legacy)}")

    verdict = VERDICT if not errors else "FAIL_ASTRONOMICON_PATCH_PACK_INVENTORY"
    return {
        "task_id": TASK_ID,
        "validator_id": "astronomicon_patch_pack_inventory.v0_1",
        "verdict": verdict,
        "generated_at_utc": utc_now(),
        "repo_root": str(repo_root),
        "warp_root": rel(repo_root, warp_root),
        "pack_count": len(pack_records),
        "classification_counts": counts,
        "standard_pack_count": len(standard),
        "candidate_pack_count": len(candidates),
        "legacy_or_incomplete_count": len(legacy),
        "dirty_nested_warp_count": len(dirty_nested),
        "long_path_blocker_count": len(long_blockers),
        "recent_packs": [r["patch_id"] for r in sorted(pack_records, key=lambda r: r["modified_time_utc"], reverse=True)[:12]],
        "candidate_packs": [r["patch_id"] for r in candidates[:20]],
        "legacy_examples": [{"patch_id": r["patch_id"], "missing": r["required_missing"]} for r in legacy[:12]],
        "dirty_examples": [{"patch_id": r["patch_id"], "nested": r["nested_warp_examples"]} for r in dirty_nested[:8]],
        "long_path_examples": [{"patch_id": r["patch_id"], "paths": r["long_path_examples"]} for r in long_blockers[:8]],
        "pack_records": pack_records,
        "errors": errors,
        "warnings": warnings,
    }


def write_md(report: dict[str, Any]) -> str:
    lines = [
        f"# Astronomicon Patch Pack Inventory V0.1",
        "",
        f"- verdict: `{report['verdict']}`",
        f"- generated_at_utc: `{report['generated_at_utc']}`",
        f"- pack_count: `{report['pack_count']}`",
        f"- standard_pack_count: `{report['standard_pack_count']}`",
        f"- candidate_pack_count: `{report['candidate_pack_count']}`",
        f"- legacy_or_incomplete_count: `{report['legacy_or_incomplete_count']}`",
        f"- dirty_nested_warp_count: `{report['dirty_nested_warp_count']}`",
        f"- long_path_blocker_count: `{report['long_path_blocker_count']}`",
        "",
        "## Classification counts",
        "",
    ]
    for k, v in sorted(report["classification_counts"].items()):
        lines.append(f"- `{k}`: `{v}`")
    lines += ["", "## Recent packs", ""]
    for p in report["recent_packs"]:
        lines.append(f"- `{p}`")
    if report["legacy_examples"]:
        lines += ["", "## Legacy / incomplete examples", ""]
        for item in report["legacy_examples"]:
            lines.append(f"- `{item['patch_id']}` missing={item['missing']}")
    if report["dirty_examples"]:
        lines += ["", "## Dirty nested WARP examples", ""]
        for item in report["dirty_examples"]:
            lines.append(f"- `{item['patch_id']}` nested={item['nested']}")
    if report["warnings"]:
        lines += ["", "## Warnings", ""]
        for w in report["warnings"]:
            lines.append(f"- {w}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    report = build_inventory(repo_root)

    reports_dir = repo_root / "ORGANS" / "ASTRONOMICON" / "REPORTS"
    receipts_dir = repo_root / "ORGANS" / "ASTRONOMICON" / "RECEIPTS"
    app_receipts = repo_root / "SUPPORT" / "APP_TAURI" / "receipts"
    reports_dir.mkdir(parents=True, exist_ok=True)
    receipts_dir.mkdir(parents=True, exist_ok=True)
    app_receipts.mkdir(parents=True, exist_ok=True)

    report_json = reports_dir / "ASTRONOMICON_PATCH_PACK_INVENTORY_REPORT_V0_1.json"
    report_md = reports_dir / "ASTRONOMICON_PATCH_PACK_INVENTORY_REPORT_V0_1.md"
    summary_json = reports_dir / "ASTRONOMICON_PATCH_PACK_INVENTORY_SUMMARY_V0_1.json"
    receipt_json = receipts_dir / "astronomicon_patch_pack_inventory_receipt.json"

    summary = {k: report[k] for k in [
        "task_id", "verdict", "generated_at_utc", "pack_count", "standard_pack_count",
        "candidate_pack_count", "legacy_or_incomplete_count", "dirty_nested_warp_count",
        "long_path_blocker_count", "classification_counts", "errors", "warnings"
    ]}

    report_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    report_md.write_text(write_md(report), encoding="utf-8")
    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    receipt = dict(summary)
    receipt.update({
        "report_json": rel(repo_root, report_json),
        "report_md": rel(repo_root, report_md),
        "summary": rel(repo_root, summary_json),
    })
    receipt_json.write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")
    (app_receipts / "astronomicon_patch_pack_inventory_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.compact:
        print(f"ASTRONOMICON: packs={report['pack_count']} standard={report['standard_pack_count']} candidate={report['candidate_pack_count']} legacy={report['legacy_or_incomplete_count']} dirty={report['dirty_nested_warp_count']} long={report['long_path_blocker_count']}")
        if report["warnings"]:
            print("ASTRA_WARN: " + " | ".join(report["warnings"][:3]))
    else:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if not report["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
