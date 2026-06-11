#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mechanicus Evidence Vault Sealer V0.1.

Seals an Evidence Vault HOT_BUFFER into a canonical EVIDENCE_PACK.zip plus manifest/index files.
Default mode is non-destructive: the source buffer is retained unless --delete-buffer-after-seal is explicit.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

SURFACE = "MECHANICUS_EVIDENCE_VAULT_SEALER_V0_1"
VERSION = "0.1.0"

SCREEN_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
JSON_EXTS = {".json", ".jsonl"}
CSV_EXTS = {".csv", ".tsv"}
MD_EXTS = {".md", ".markdown"}
LOG_EXTS = {".log", ".txt", ".out", ".err"}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def safe_id(value: str) -> str:
    keep = []
    for ch in value:
        if ch.isalnum() or ch in "._-":
            keep.append(ch)
        else:
            keep.append("_")
    out = "".join(keep).strip("._-")
    return out or "UNNAMED_PATCH"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head(repo_root: Optional[Path]) -> Optional[str]:
    if not repo_root:
        return None
    try:
        cp = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if cp.returncode == 0:
            return cp.stdout.strip()
    except Exception:
        return None
    return None


def iter_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return []
    files: List[Path] = []
    for p in root.rglob("*"):
        if p.is_file():
            files.append(p)
    return files


def classify_counts(files: List[Path], buffer_path: Path) -> Dict[str, int]:
    counts = {
        "files_total": len(files),
        "bytes_total": 0,
        "screenshots": 0,
        "json_reports": 0,
        "csv_tables": 0,
        "markdown_reports": 0,
        "logs": 0,
        "other": 0,
    }
    for f in files:
        try:
            counts["bytes_total"] += f.stat().st_size
        except OSError:
            pass
        ext = f.suffix.lower()
        if ext in SCREEN_EXTS:
            counts["screenshots"] += 1
        elif ext in JSON_EXTS:
            counts["json_reports"] += 1
        elif ext in CSV_EXTS:
            counts["csv_tables"] += 1
        elif ext in MD_EXTS:
            counts["markdown_reports"] += 1
        elif ext in LOG_EXTS:
            counts["logs"] += 1
        else:
            counts["other"] += 1
    return counts


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")


def write_owner_summary(path: Path, report: Dict[str, object]) -> None:
    m = report.get("manifest", {}) or {}
    lines = [
        "# Evidence Vault Sealer Report V0.1",
        "",
        f"Status: **{report.get('status')}**",
        f"Generated: `{report.get('generated_at_utc')}`",
        f"Patch: `{m.get('patch_id')}`",
        f"Pack: `{report.get('pack_path', '')}`",
        "",
        "## Summary",
        "",
        f"- files_total: `{(m.get('contents') or {}).get('files_total', 0)}`",
        f"- bytes_total: `{(m.get('contents') or {}).get('bytes_total', 0)}`",
        f"- raw_buffer_deleted: `{m.get('raw_buffer_deleted')}`",
        f"- retention_class: `{m.get('retention_class')}`",
        f"- sha256: `{report.get('pack_sha256', '')}`",
        "",
        "## Notes",
        "",
        "- Raw buffer is retained unless deletion was explicitly requested.",
        "- Canonical evidence is the sealed pack plus manifest/index files.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def output_report(out_root: Path, report: Dict[str, object]) -> Path:
    out_dir = out_root / f"EVIDENCE_VAULT_SEALER_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "MACHINE_REPORT.json", report)
    write_owner_summary(out_dir / "OWNER_READABLE_REPORT_RU.md", report)
    # small file manifest CSV for quick review
    rows = report.get("file_rows", []) or []
    if rows:
        with (out_dir / "sealed_files.csv").open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader(); writer.writerows(rows)
    return out_dir


def resolve_buffer(vault_root: Path, patch_id: str, buffer_path: Optional[str]) -> Path:
    if buffer_path:
        return Path(buffer_path)
    return vault_root / "buffer" / "active" / patch_id


def pack_root_for(vault_root: Path, patch_id: str) -> Path:
    now = datetime.now(timezone.utc)
    return vault_root / "packs" / f"{now.year:04d}" / f"{now.month:02d}" / safe_id(patch_id)


def seal(args: argparse.Namespace) -> Dict[str, object]:
    vault_root = Path(args.vault_root)
    patch_id = args.patch_id
    buffer_path = resolve_buffer(vault_root, patch_id, args.buffer_path)
    repo_root = Path(args.repo_root) if args.repo_root else None
    pack_root = Path(args.pack_root) if args.pack_root else pack_root_for(vault_root, patch_id)
    pack_path = pack_root / "EVIDENCE_PACK.zip"

    files = list(iter_files(buffer_path))
    contents = classify_counts(files, buffer_path)
    created_at = utc_now()
    evidence_pack_id = f"EVP-{safe_id(patch_id)}"

    file_rows = []
    for f in files:
        rel = f.relative_to(buffer_path).as_posix()
        try:
            size = f.stat().st_size
        except OSError:
            size = 0
        file_rows.append({"relative_path": rel, "size_bytes": size, "sha256": sha256_file(f)})

    manifest = {
        "evidence_pack_id": evidence_pack_id,
        "patch_id": patch_id,
        "created_at_utc": created_at,
        "source_repo_head": git_head(repo_root),
        "h_contour": True,
        "storage_zone": "SEALED_PACK",
        "retention_class": args.retention_class,
        "ttl_hours": args.ttl_hours,
        "buffer_path": str(buffer_path),
        "pack_path": str(pack_path),
        "raw_buffer_deleted": False,
        "contents": contents,
    }

    if args.dry_run:
        return {
            "status": "PASS_DRY_RUN",
            "surface": SURFACE,
            "version": VERSION,
            "generated_at_utc": created_at,
            "mode": "seal",
            "dry_run": True,
            "manifest": manifest,
            "pack_path": str(pack_path),
            "file_rows": file_rows[:50],
            "actions": [f"dry_run_would_pack:{buffer_path} -> {pack_path}"],
        }

    if not buffer_path.exists():
        return {
            "status": "FAIL_BUFFER_NOT_FOUND",
            "surface": SURFACE,
            "version": VERSION,
            "generated_at_utc": created_at,
            "mode": "seal",
            "dry_run": False,
            "manifest": manifest,
            "pack_path": str(pack_path),
            "actions": [],
            "error": f"Buffer path does not exist: {buffer_path}",
        }

    pack_root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(pack_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for f in files:
            rel = f.relative_to(buffer_path).as_posix()
            z.write(f, arcname=f"{safe_id(patch_id)}/{rel}")

    pack_sha = sha256_file(pack_path)
    manifest["pack_sha256"] = pack_sha
    manifest["pack_size_bytes"] = pack_path.stat().st_size

    write_json(pack_root / "EVIDENCE_MANIFEST.json", manifest)
    write_json(pack_root / "MACHINE_INDEX.json", {"manifest": manifest, "files": file_rows})
    (pack_root / "SHA256SUMS.txt").write_text(
        f"{pack_sha}  EVIDENCE_PACK.zip\n", encoding="utf-8", newline="\n"
    )
    write_owner_summary(pack_root / "OWNER_SUMMARY_RU.md", {
        "status": "PASS_SEALED",
        "generated_at_utc": created_at,
        "manifest": manifest,
        "pack_path": str(pack_path),
        "pack_sha256": pack_sha,
    })

    indexes = vault_root / "indexes"
    indexes.mkdir(parents=True, exist_ok=True)
    with (indexes / "evidence_pack_index.jsonl").open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(manifest, ensure_ascii=False) + "\n")
    write_json(indexes / "latest_manifest.json", manifest)

    actions = [f"sealed_pack:{pack_path}", f"indexed:{indexes / 'evidence_pack_index.jsonl'}"]
    if args.delete_buffer_after_seal:
        # Re-check pack before deletion.
        if pack_path.exists() and sha256_file(pack_path) == pack_sha:
            shutil.rmtree(buffer_path)
            manifest["raw_buffer_deleted"] = True
            actions.append(f"deleted_buffer_after_seal:{buffer_path}")
            write_json(pack_root / "EVIDENCE_MANIFEST.json", manifest)
            write_json(indexes / "latest_manifest.json", manifest)
        else:
            actions.append("skip_delete_buffer:pack_verification_failed")

    status = "PASS_SEALED_BUFFER_DELETED" if manifest["raw_buffer_deleted"] else "PASS_SEALED_BUFFER_RETAINED"
    return {
        "status": status,
        "surface": SURFACE,
        "version": VERSION,
        "generated_at_utc": created_at,
        "mode": "seal",
        "dry_run": False,
        "manifest": manifest,
        "pack_path": str(pack_path),
        "pack_sha256": pack_sha,
        "file_rows": file_rows[:200],
        "actions": actions,
    }


def inspect(args: argparse.Namespace) -> Dict[str, object]:
    vault_root = Path(args.vault_root)
    patch_id = args.patch_id
    buffer_path = resolve_buffer(vault_root, patch_id, args.buffer_path)
    files = list(iter_files(buffer_path))
    contents = classify_counts(files, buffer_path)
    return {
        "status": "PASS" if buffer_path.exists() else "WARN_BUFFER_NOT_FOUND",
        "surface": SURFACE,
        "version": VERSION,
        "generated_at_utc": utc_now(),
        "mode": "inspect",
        "buffer_path": str(buffer_path),
        "summary": contents,
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["inspect", "seal"], default="inspect")
    ap.add_argument("--repo-root", default="")
    ap.add_argument("--vault-root", required=True)
    ap.add_argument("--patch-id", required=True)
    ap.add_argument("--buffer-path", default="")
    ap.add_argument("--pack-root", default="")
    ap.add_argument("--out-root", default="")
    ap.add_argument("--retention-class", default="PINNED_EVIDENCE")
    ap.add_argument("--ttl-hours", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--delete-buffer-after-seal", action="store_true")
    args = ap.parse_args(argv)

    if args.mode == "seal":
        report = seal(args)
    else:
        report = inspect(args)

    out_root = Path(args.out_root) if args.out_root else Path(args.vault_root) / "reports"
    out_dir = output_report(out_root, report)
    report["output_root"] = str(out_dir)
    # Rewrite with output_root included.
    write_json(out_dir / "MACHINE_REPORT.json", report)
    print(json.dumps({k:v for k,v in report.items() if k != "file_rows"}, ensure_ascii=False, indent=2))
    return 0 if not str(report.get("status", "")).startswith("FAIL") else 2


if __name__ == "__main__":
    raise SystemExit(main())
