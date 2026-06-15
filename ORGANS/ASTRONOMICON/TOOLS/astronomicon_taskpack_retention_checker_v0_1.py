#!/usr/bin/env python3
"""Inspect Astronomicon registered taskpack payload retention state."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    import sys

    sys.path.append(str(Path(__file__).resolve().parent))

from astronomicon_task_entry_lib_v0_1 import build_context, utc_now, write_json  # noqa: E402

REVIEW_PATH_MARKERS = {
    "review",
    "reviews",
    "artifact",
    "artifacts",
    "screenshots",
    "screenshot",
    "evidence",
    "proof",
}

HASH_POINTER_MARKERS = {
    "sha256",
    "sha-256",
    "hash",
    "checksum",
    "checksums",
}

TEMP_PATH_MARKERS = {
    "tmp",
    "temp",
    "runtime",
    "_runtime",
    "_tmp",
}

REVIEW_HEAVY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pdf",
    ".zip",
    ".mp4",
    ".mov",
    ".avi",
}

ARCHIVE_EXTENSIONS = {".zip", ".7z", ".rar", ".tar", ".gz", ".bz2", ".xz"}


def to_posix(path_value: Path | str) -> str:
    return str(path_value).replace("\\", "/")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Astronomicon registered taskpack retention checker.")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--task-id", default="", help="Task ID for receipt metadata.")
    parser.add_argument(
        "--registered-root",
        default="",
        help="Override root for registered entries. Defaults to Astronomicon REGISTERED root.",
    )
    parser.add_argument(
        "--small-threshold-bytes",
        type=int,
        default=64 * 1024,
        help="Payload size threshold for KEEP_CANONICAL_SMALL classification.",
    )
    parser.add_argument("--report-json", default="", help="Optional JSON output path.")
    parser.add_argument("--report-md", default="", help="Optional markdown output path.")
    return parser.parse_args()


def file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def iter_files(root: Path) -> list[Path]:
    if not root.exists() or not root.is_dir():
        return []
    return sorted([path for path in root.rglob("*") if path.is_file()], key=to_posix)


def has_marker(path: Path, markers: set[str]) -> bool:
    lowered_parts = [part.lower() for part in path.parts]
    return any(marker in lowered_parts for marker in markers)


def path_contains_text(path: Path, markers: set[str]) -> bool:
    lowered = path.name.lower()
    return any(marker in lowered for marker in markers)


def detect_hash_pointer(files: list[Path]) -> bool:
    for path in files:
        if path.suffix.lower() in {".sha256", ".sha1", ".sha512", ".md5"}:
            return True
        if path_contains_text(path, HASH_POINTER_MARKERS):
            return True
    return False


def detect_review_payload(files: list[Path]) -> bool:
    for path in files:
        suffix = path.suffix.lower()
        if suffix in REVIEW_HEAVY_EXTENSIONS and has_marker(path, REVIEW_PATH_MARKERS):
            return True
    return False


def detect_large_nested_payload(files: list[Path], extracted_root: Path, threshold: int) -> bool:
    total_size = sum(file_size(path) for path in files)
    if total_size > threshold:
        return True
    for path in files:
        if path.suffix.lower() in ARCHIVE_EXTENSIONS and path != extracted_root.parent / "TASKPACK.zip":
            return True
    max_depth = 0
    for path in files:
        try:
            rel = path.relative_to(extracted_root)
        except ValueError:
            continue
        max_depth = max(max_depth, len(rel.parts))
    return max_depth >= 6


def detect_runtime_or_temp(files: list[Path]) -> bool:
    for path in files:
        if has_marker(path, TEMP_PATH_MARKERS):
            return True
    return False


def classify_entry(
    *,
    manifest_present: bool,
    route_manifest_present: bool,
    admission_receipt_present: bool,
    hash_pointer_present: bool,
    review_artifact_payload_present: bool,
    large_nested_payload_present: bool,
    runtime_or_temp_present: bool,
    extracted_present: bool,
    extracted_size_bytes: int,
    small_threshold_bytes: int,
) -> tuple[str, str]:
    if not route_manifest_present or not admission_receipt_present:
        return "MISSING_REQUIRED_RECEIPT", "RESTORE_REQUIRED_RECEIPTS_AND_REVALIDATE"
    if runtime_or_temp_present:
        return "RUNTIME_OR_TEMP_SHOULD_NOT_BE_CANONICAL", "MOVE_RUNTIME_OR_TEMP_OUT_OF_CANONICAL_REGISTERED"
    if review_artifact_payload_present or large_nested_payload_present:
        return "REVIEW_ARTIFACT_PAYLOAD_REVIEW_REQUIRED", "REVIEW_PAYLOAD_AND_PREPARE_HASH_QUARANTINE_PLAN"
    if extracted_present and extracted_size_bytes > small_threshold_bytes and not hash_pointer_present:
        return "HASH_AND_QUARANTINE_RECOMMENDED", "GENERATE_HASH_POINTER_AND_PLAN_QUARANTINE"
    if manifest_present and extracted_present and extracted_size_bytes <= small_threshold_bytes:
        return "KEEP_CANONICAL_SMALL", "KEEP_CANONICAL"
    return "KEEP_MANIFEST_ROUTE_RECEIPTS_ONLY", "KEEP_MANIFEST_ROUTE_RECEIPTS_ONLY"


def build_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    class_counts = summary.get("by_retention_class", {})
    small_safe = int(class_counts.get("KEEP_CANONICAL_SMALL", 0))
    hash_quarantine = int(class_counts.get("HASH_AND_QUARANTINE_RECOMMENDED", 0)) + int(
        class_counts.get("REVIEW_ARTIFACT_PAYLOAD_REVIEW_REQUIRED", 0)
    )
    vm3_blocking = int(summary.get("entries_blocking_vm3_route_proof", 0))
    context_blocking = int(summary.get("entries_blocking_context_optimization", 0))

    lines: list[str] = []
    lines.append("# Taskpack Retention Checker Report")
    lines.append("")
    lines.append(f"Task ID: `{report.get('task_id', '')}`")
    lines.append(f"Timestamp (UTC): `{report.get('timestamp_utc', '')}`")
    lines.append(f"Registered root: `{report.get('registered_root', '')}`")
    lines.append("")
    lines.append(f"- Total entries: `{summary.get('total_entries', 0)}`")
    lines.append(f"- Total bytes: `{summary.get('total_size_bytes', 0)}`")
    lines.append(f"- Small and safe (`KEEP_CANONICAL_SMALL`): `{small_safe}`")
    lines.append(f"- Entries with EXTRACTED payload: `{summary.get('entries_with_extracted_payload', 0)}`")
    lines.append(f"- Hash/quarantine follow-up candidates: `{hash_quarantine}`")
    lines.append(f"- Any VM3 route proof blockers: `{'YES' if vm3_blocking > 0 else 'NO'}` (`{vm3_blocking}`)")
    lines.append(
        f"- Any context optimization blockers: `{'YES' if context_blocking > 0 else 'NO'}` (`{context_blocking}`)"
    )
    lines.append("")
    lines.append("## Retention Class Counts")
    if class_counts:
        for name, count in sorted(class_counts.items()):
            lines.append(f"- `{name}`: `{count}`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Entries")
    for entry in report.get("entries", []):
        lines.append(
            "- "
            + f"`{entry['task_id']}` class=`{entry['retention_class']}` "
            + f"zip_count=`{entry['zip_count']}` extracted_size=`{entry['extracted_size_bytes']}` "
            + f"vm3_block=`{entry['blocks_vm3_route_proof']}` "
            + f"context_block=`{entry['blocks_context_optimization']}`"
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    ctx = build_context(args.repo_root)
    registered_root = Path(args.registered_root).resolve() if args.registered_root else ctx["registered_root"]

    entries: list[dict[str, Any]] = []
    warnings: list[str] = []

    if not registered_root.exists() or not registered_root.is_dir():
        warnings.append(f"Registered root not found: {to_posix(registered_root)}")

    for candidate in sorted([p for p in registered_root.iterdir() if p.is_dir()], key=to_posix):
        task_id = candidate.name
        all_files = iter_files(candidate)
        extracted_root = candidate / "EXTRACTED"
        extracted_files = iter_files(extracted_root)

        total_size_bytes = sum(file_size(path) for path in all_files)
        extracted_size_bytes = sum(file_size(path) for path in extracted_files)
        zip_count = len([path for path in all_files if path.suffix.lower() == ".zip"])

        manifest_present = (candidate / "EXTRACTED/MANIFEST.json").exists() or any(
            path.name == "MANIFEST.json" for path in extracted_files
        )
        route_manifest_present = (candidate / "TASK_ROUTE_MANIFEST.json").exists()
        admission_receipt_present = (candidate / "TASKPACK_ADMISSION_RECEIPT.json").exists()
        hash_pointer_present = detect_hash_pointer(all_files)
        review_artifact_payload_present = detect_review_payload(extracted_files)
        large_nested_payload_present = detect_large_nested_payload(
            extracted_files,
            extracted_root,
            max(1, args.small_threshold_bytes),
        )
        runtime_or_temp_present = detect_runtime_or_temp(all_files)

        retention_class, recommended_action = classify_entry(
            manifest_present=manifest_present,
            route_manifest_present=route_manifest_present,
            admission_receipt_present=admission_receipt_present,
            hash_pointer_present=hash_pointer_present,
            review_artifact_payload_present=review_artifact_payload_present,
            large_nested_payload_present=large_nested_payload_present,
            runtime_or_temp_present=runtime_or_temp_present,
            extracted_present=extracted_root.exists(),
            extracted_size_bytes=extracted_size_bytes,
            small_threshold_bytes=max(1, args.small_threshold_bytes),
        )

        blocks_vm3_route_proof = retention_class in {
            "MISSING_REQUIRED_RECEIPT",
            "RUNTIME_OR_TEMP_SHOULD_NOT_BE_CANONICAL",
        }
        blocks_context_optimization = retention_class in {
            "HASH_AND_QUARANTINE_RECOMMENDED",
            "REVIEW_ARTIFACT_PAYLOAD_REVIEW_REQUIRED",
            "RUNTIME_OR_TEMP_SHOULD_NOT_BE_CANONICAL",
            "MISSING_REQUIRED_RECEIPT",
        }

        entry = {
            "task_id": task_id,
            "registered_path": to_posix(candidate.relative_to(ctx["repo_root"])),
            "total_size_bytes": total_size_bytes,
            "zip_count": zip_count,
            "extracted_size_bytes": extracted_size_bytes,
            "manifest_present": manifest_present,
            "route_manifest_present": route_manifest_present,
            "admission_receipt_present": admission_receipt_present,
            "hash_pointer_present": hash_pointer_present,
            "large_nested_payload_present": large_nested_payload_present,
            "review_artifact_payload_present": review_artifact_payload_present,
            "retention_class": retention_class,
            "blocks_vm3_route_proof": blocks_vm3_route_proof,
            "blocks_context_optimization": blocks_context_optimization,
            "recommended_action": recommended_action,
        }
        entries.append(entry)

    by_retention_class: dict[str, int] = {}
    for entry in entries:
        cls = str(entry["retention_class"])
        by_retention_class[cls] = by_retention_class.get(cls, 0) + 1

    report = {
        "schema_version": "0.1",
        "checker_id": f"ASTRONOMICON_TASKPACK_RETENTION_CHECKER_{utc_now()}",
        "task_id": args.task_id,
        "timestamp_utc": utc_now(),
        "registered_root": to_posix(registered_root),
        "summary": {
            "total_entries": len(entries),
            "total_size_bytes": sum(int(row["total_size_bytes"]) for row in entries),
            "entries_with_extracted_payload": sum(1 for row in entries if int(row["extracted_size_bytes"]) > 0),
            "entries_missing_required_receipt": sum(
                1 for row in entries if row["retention_class"] == "MISSING_REQUIRED_RECEIPT"
            ),
            "entries_hash_and_quarantine_recommended": sum(
                1 for row in entries if row["retention_class"] == "HASH_AND_QUARANTINE_RECOMMENDED"
            ),
            "entries_review_payload_review_required": sum(
                1 for row in entries if row["retention_class"] == "REVIEW_ARTIFACT_PAYLOAD_REVIEW_REQUIRED"
            ),
            "entries_blocking_vm3_route_proof": sum(1 for row in entries if bool(row["blocks_vm3_route_proof"])),
            "entries_blocking_context_optimization": sum(
                1 for row in entries if bool(row["blocks_context_optimization"])
            ),
            "by_retention_class": dict(sorted(by_retention_class.items())),
        },
        "warnings": warnings,
        "entries": entries,
    }

    if args.report_json:
        write_json(Path(args.report_json).resolve(), report)
    if args.report_md:
        report_md_path = Path(args.report_md).resolve()
        report_md_path.parent.mkdir(parents=True, exist_ok=True)
        report_md_path.write_text(build_markdown(report), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
