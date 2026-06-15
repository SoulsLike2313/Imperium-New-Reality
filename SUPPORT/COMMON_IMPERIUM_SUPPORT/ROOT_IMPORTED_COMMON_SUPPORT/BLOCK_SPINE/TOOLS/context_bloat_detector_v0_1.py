#!/usr/bin/env python3
"""Detect context bloat and missing context contract elements."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
from typing import Dict, List


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def detect_bloat(context_pack: dict, max_files: int, max_chars: int) -> dict:
    mandatory = context_pack.get("mandatory_context", [])
    optional = context_pack.get("optional_context", [])
    read_order = context_pack.get("route_read_order", [])
    required_organs = context_pack.get("required_organs", [])
    protected_zones: Dict[str, List[str]] = context_pack.get("protected_zones", {})

    warnings: List[str] = []
    blocking: List[str] = []
    caps: List[str] = []

    total_context_items = len(mandatory) + len(optional)
    if total_context_items > max_files:
        warnings.append(f"Context item count {total_context_items} exceeds max_files {max_files}")
        caps.append("CAP_CONTEXT_BLOAT_DETECTOR_MISSING")

    est_chars = int(context_pack.get("estimated_character_count", 0))
    if est_chars > max_chars:
        warnings.append(f"Estimated character count {est_chars} exceeds max_chars {max_chars}")
        caps.append("CAP_CONTEXT_BLOAT_DETECTOR_MISSING")

    seen = set()
    duplicates = []
    for entry in read_order:
        if entry in seen:
            duplicates.append(entry)
        seen.add(entry)
    if duplicates:
        warnings.append(f"Duplicate read-first entries: {len(duplicates)}")
        caps.append("CAP_CONTEXT_BLOAT_DETECTOR_MISSING")

    forbidden_patterns = [
        entry for entry in read_order if "*" in entry or entry.endswith("ORGANS/") or entry.endswith("ORGANS")
    ]
    if forbidden_patterns:
        warnings.append("Forbidden broad-read patterns detected in route_read_order")
        caps.append("CAP_CONTEXT_BLOAT_DETECTOR_MISSING")

    all_context = mandatory + optional
    missing_digests = []
    for organ in required_organs:
        digest = f"IMPERIUM_NEW_GENERATION/ORGANS/{organ}/BLOCK/CONTEXT_DIGEST_V0_1.md"
        if digest not in all_context:
            missing_digests.append(organ)
    if missing_digests:
        blocking.append(f"Missing compact digest for organs: {', '.join(missing_digests)}")
        caps.append("CAP_ORGAN_BLOCK_PASSPORTS_MISSING")

    missing_protected = []
    for organ in required_organs:
        zones = protected_zones.get(organ, [])
        if not zones:
            missing_protected.append(organ)
    if missing_protected:
        blocking.append(f"Missing protected zone declaration for organs: {', '.join(missing_protected)}")
        caps.append("CAP_PROTECTED_ZONE_CONTRACT_MISSING")

    if not context_pack.get("expected_outputs"):
        blocking.append("Missing expected outputs declaration")
        caps.append("CAP_PENDING_COMMIT_PUSH_FIELDS_LEFT_OPEN")

    if blocking:
        verdict = "BLOCK"
    elif warnings:
        verdict = "PASS_WITH_WARNINGS"
    else:
        verdict = "PASS"

    return {
        "generated_at_utc": utc_now(),
        "total_context_items": total_context_items,
        "mandatory_context_count": len(mandatory),
        "optional_context_count": len(optional),
        "estimated_character_count": est_chars,
        "duplicate_read_first_count": len(duplicates),
        "forbidden_pattern_count": len(forbidden_patterns),
        "missing_digest_organs": missing_digests,
        "missing_protected_zone_organs": missing_protected,
        "warnings": warnings,
        "blocking_issues": blocking,
        "caps_triggered": sorted(set(caps)),
        "verdict": verdict,
    }


def write_outputs(output_dir: pathlib.Path, result: dict, source_context_pack: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "context_bloat_detector_report.md"
    receipt_path = output_dir / "context_bloat_detector_receipt.json"

    lines = [
        "# Context Bloat Detector Report",
        "",
        f"Source context pack: `{source_context_pack}`",
        f"Generated at UTC: `{result['generated_at_utc']}`",
        "",
        "## Metrics",
        "",
        f"- total_context_items: {result['total_context_items']}",
        f"- mandatory_context_count: {result['mandatory_context_count']}",
        f"- optional_context_count: {result['optional_context_count']}",
        f"- estimated_character_count: {result['estimated_character_count']}",
        f"- duplicate_read_first_count: {result['duplicate_read_first_count']}",
        f"- forbidden_pattern_count: {result['forbidden_pattern_count']}",
        "",
        "## Warnings",
        "",
    ]
    if result["warnings"]:
        for warning in result["warnings"]:
            lines.append(f"- {warning}")
    else:
        lines.append("- none")

    lines.extend(["", "## Blocking issues", ""])
    if result["blocking_issues"]:
        for issue in result["blocking_issues"]:
            lines.append(f"- {issue}")
    else:
        lines.append("- none")

    lines.extend(["", "## Caps triggered", ""])
    if result["caps_triggered"]:
        for cap in result["caps_triggered"]:
            lines.append(f"- {cap}")
    else:
        lines.append("- none")

    lines.extend(["", f"## Verdict: `{result['verdict']}`", ""])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    receipt_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    return report_path, receipt_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect context pack bloat")
    parser.add_argument("--context-pack", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--max-files", type=int, default=80)
    parser.add_argument("--max-chars", type=int, default=200000)
    args = parser.parse_args()

    context_pack_path = pathlib.Path(args.context_pack).resolve()
    context_pack = load_json(context_pack_path)
    result = detect_bloat(context_pack, max_files=args.max_files, max_chars=args.max_chars)
    write_outputs(pathlib.Path(args.output_dir), result, context_pack_path)


if __name__ == "__main__":
    main()
