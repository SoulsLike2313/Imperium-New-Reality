#!/usr/bin/env python3
"""Administratum task report bundle packager v0.1."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from administratum_bundle_gate_v0_1 import (  # noqa: E402
    BLOCK,
    COMPOSITION_RECEIPT,
    MISSING_REQUEST,
    PASS,
    adjacent_matches,
    ensure_under,
    evaluate_report,
    find_repo_root,
    to_posix,
    write_gate_outputs,
    write_json,
)


BUNDLE_NAME = "task_report_bundle.zip"
INVENTORY_NAME = "bundle_file_inventory.json"
SHA256SUMS_NAME = "sha256sums.txt"
ADJACENT_MANIFEST_NAME = "adjacent_receipts_manifest.json"

SELF_REFERENCE_ADJACENT = (
    {
        "path": BUNDLE_NAME,
        "class_ids": [],
        "reason": "The bundle cannot include itself.",
        "status": "ADJACENT_SELF_REFERENCE_LIMIT",
    },
    {
        "path": SHA256SUMS_NAME,
        "class_ids": ["sha256_sums"],
        "reason": "Final sums record the final bundle hash and remain adjacent.",
        "status": "ADJACENT_SELF_REFERENCE_LIMIT",
    },
    {
        "path": INVENTORY_NAME,
        "class_ids": ["bundle_manifest_and_file_inventory"],
        "reason": "Inventory records the final included file set and remains adjacent.",
        "status": "ADJACENT_SELF_REFERENCE_LIMIT",
    },
    {
        "path": COMPOSITION_RECEIPT,
        "class_ids": ["administratum_composition_receipt"],
        "reason": "Composition receipt records final bundle creation state and remains adjacent.",
        "status": "ADJACENT_SELF_REFERENCE_LIMIT",
    },
    {
        "path": "git_closure_receipt.json",
        "class_ids": [
            "commit_chain_identifiers",
            "git_closure_and_remote_closure_proof",
            "worktree_clean_or_explicit_cap_receipt",
        ],
        "reason": "Final git closure may be refreshed after the bundle commit.",
        "status": "ADJACENT_SELF_REFERENCE_LIMIT",
    },
    {
        "path": "remote_closure_receipt.json",
        "class_ids": ["git_closure_and_remote_closure_proof"],
        "reason": "Final remote closure may be refreshed after push.",
        "status": "ADJACENT_SELF_REFERENCE_LIMIT",
    },
)

EXCLUDED_FROM_ZIP = {
    BUNDLE_NAME,
    SHA256SUMS_NAME,
    INVENTORY_NAME,
    COMPOSITION_RECEIPT,
    "git_closure_receipt.json",
    "remote_closure_receipt.json",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def ensure_adjacent_manifest(report_dir: Path, task_id: str) -> Path:
    payload = {
        "manifest_type": "adjacent_receipts_manifest",
        "task_id": task_id,
        "matrix_version": "0.1",
        "timestamp_utc": utc_now(),
        "reason": "Self-reference-limited files are stored next to the final bundle.",
        "adjacent_files": list(SELF_REFERENCE_ADJACENT),
    }
    path = report_dir / ADJACENT_MANIFEST_NAME
    write_json(path, payload)
    return path


def collect_included_files(report_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in report_dir.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(report_dir).as_posix()
        if rel in EXCLUDED_FROM_ZIP:
            continue
        if rel == MISSING_REQUEST:
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(report_dir).as_posix())


def inventory_payload(
    report_dir: Path,
    included_files: list[Path],
    *,
    task_id: str,
    bundle_path: Path,
    bundle_sha256: str = "",
) -> dict[str, Any]:
    adjacent_entries: list[dict[str, Any]] = []
    for entry in SELF_REFERENCE_ADJACENT:
        path = report_dir / str(entry["path"])
        row = dict(entry)
        row["exists"] = path.is_file()
        row["sha256"] = sha256_file(path) if path.is_file() and path.name != SHA256SUMS_NAME else ""
        adjacent_entries.append(row)
    return {
        "inventory_type": "task_report_bundle_file_inventory",
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "report_dir": to_posix(report_dir),
        "bundle_path": to_posix(bundle_path),
        "bundle_sha256": bundle_sha256,
        "included_file_count": len(included_files),
        "included_files": [
            {
                "path": file_path.relative_to(report_dir).as_posix(),
                "size_bytes": file_path.stat().st_size,
                "sha256": sha256_file(file_path),
            }
            for file_path in included_files
        ],
        "adjacent_self_reference_files": adjacent_entries,
        "excluded_from_bundle_due_self_reference": sorted(EXCLUDED_FROM_ZIP),
    }


def write_inventory(
    report_dir: Path,
    included_files: list[Path],
    *,
    task_id: str,
    bundle_path: Path,
    bundle_sha256: str = "",
) -> Path:
    path = report_dir / INVENTORY_NAME
    write_json(path, inventory_payload(report_dir, included_files, task_id=task_id, bundle_path=bundle_path, bundle_sha256=bundle_sha256))
    return path


def write_sha256sums(report_dir: Path, included_files: list[Path], bundle_path: Path | None = None) -> Path:
    sha_paths: list[Path] = list(included_files)
    for name in EXCLUDED_FROM_ZIP:
        path = report_dir / name
        if path.is_file() and name != SHA256SUMS_NAME:
            sha_paths.append(path)
    if bundle_path is not None and bundle_path.is_file():
        sha_paths.append(bundle_path)
    seen: set[str] = set()
    lines: list[str] = []
    for path in sorted(sha_paths, key=lambda item: item.relative_to(report_dir).as_posix() if report_dir in item.resolve().parents else item.name):
        rel = path.relative_to(report_dir).as_posix() if report_dir in path.resolve().parents else path.name
        if rel in seen:
            continue
        seen.add(rel)
        lines.append(f"{sha256_file(path)}  {rel}")
    sha_path = report_dir / SHA256SUMS_NAME
    write_text(sha_path, "\n".join(lines))
    return sha_path


def build_zip(report_dir: Path, bundle_path: Path, included_files: list[Path]) -> dict[str, Any]:
    if bundle_path.exists():
        bundle_path.unlink()
    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in included_files:
            archive.write(file_path, file_path.relative_to(report_dir).as_posix())
    return {
        "bundle_path": to_posix(bundle_path),
        "bundle_sha256": sha256_file(bundle_path),
        "bundle_size_bytes": bundle_path.stat().st_size,
        "included_file_count": len(included_files),
        "included_files": [path.relative_to(report_dir).as_posix() for path in included_files],
    }


def package_report(report_dir: Path, *, task_id: str, bundle_name: str = BUNDLE_NAME) -> dict[str, Any]:
    repo_root = find_repo_root(report_dir)
    report_dir = ensure_under(repo_root, report_dir)
    bundle_path = ensure_under(repo_root, report_dir / bundle_name)
    receipt_path = ensure_under(repo_root, report_dir / COMPOSITION_RECEIPT)
    missing_path = ensure_under(repo_root, report_dir / MISSING_REQUEST)

    ensure_adjacent_manifest(report_dir, task_id)
    included_before_gate = collect_included_files(report_dir)
    write_inventory(report_dir, included_before_gate, task_id=task_id, bundle_path=bundle_path)
    write_sha256sums(report_dir, included_before_gate)

    gate_result = evaluate_report(report_dir, task_id=task_id, receipt_path=receipt_path)
    if gate_result["verdict"] == BLOCK:
        if bundle_path.exists():
            bundle_path.unlink()
        receipt = write_gate_outputs(
            gate_result,
            receipt_path=receipt_path,
            missing_request_path=missing_path,
            bundle_created=False,
            bundle_path=bundle_path,
        )
        return {
            "verdict": BLOCK,
            "bundle_created": False,
            "bundle_path": to_posix(bundle_path),
            "missing_items_request_path": to_posix(missing_path),
            "composition_receipt": receipt,
        }

    included_files = collect_included_files(report_dir)
    bundle = build_zip(report_dir, bundle_path, included_files)
    final_receipt = write_gate_outputs(
        evaluate_report(report_dir, task_id=task_id, receipt_path=receipt_path),
        receipt_path=receipt_path,
        missing_request_path=missing_path,
        bundle_created=True,
        bundle_path=bundle_path,
        bundle_sha256=bundle["bundle_sha256"],
    )
    write_inventory(
        report_dir,
        included_files,
        task_id=task_id,
        bundle_path=bundle_path,
        bundle_sha256=bundle["bundle_sha256"],
    )
    write_sha256sums(report_dir, included_files, bundle_path)
    return {
        "verdict": PASS,
        "bundle_created": True,
        "bundle": bundle,
        "composition_receipt": final_receipt,
        "inventory_path": to_posix(report_dir / INVENTORY_NAME),
        "sha256sums_path": to_posix(report_dir / SHA256SUMS_NAME),
        "adjacent_manifest_path": to_posix(report_dir / ADJACENT_MANIFEST_NAME),
        "sha256_class_adjacent": adjacent_matches(report_dir, {"adjacent_files": list(SELF_REFERENCE_ADJACENT)}, "sha256_sums"),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Administratum task report bundle packager v0.1.")
    parser.add_argument("--report-dir", required=True, help="Task report directory to package.")
    parser.add_argument("--task-id", required=True, help="Task ID for receipts.")
    parser.add_argument("--bundle-name", default=BUNDLE_NAME, help="Bundle filename.")
    parser.add_argument("--result-out", default="", help="Optional path for the packager result receipt.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    result = package_report(Path(args.report_dir), task_id=args.task_id, bundle_name=args.bundle_name)
    if args.result_out:
        repo_root = find_repo_root(Path(args.report_dir))
        write_json(ensure_under(repo_root, Path(args.result_out)), result)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if result["verdict"] == PASS else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
