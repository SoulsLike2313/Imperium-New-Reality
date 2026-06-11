#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mechanicus Evidence Vault Packager V0.1

Modes:
  init    - create or dry-run HOT_BUFFER structure for a patch id
  seal    - zip a HOT_BUFFER into a sealed evidence pack and write manifest/index
  inspect - report vault state

The tool does not write to source repo. It writes only to Evidence Vault and out-root reports.
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
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

VERSION = "0.1.0"
SURFACE = "MECHANICUS_EVIDENCE_VAULT_PACKAGER_V0_1"
BUFFER_SUBDIRS = ["raw", "screenshots", "json", "csv", "logs", "reports"]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def safe_id(value: str) -> str:
    out = []
    for ch in value.strip():
        if ch.isalnum() or ch in "._-":
            out.append(ch)
        else:
            out.append("-")
    s = "".join(out).strip("-._")
    return s or "UNNAMED-PATCH"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head(repo_root: Path) -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo_root), text=True, capture_output=True, timeout=15)
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return "UNKNOWN"


def count_contents(root: Path) -> Dict[str, int]:
    counts = {
        "files_total": 0,
        "bytes_total": 0,
        "screenshots": 0,
        "json_reports": 0,
        "csv_tables": 0,
        "markdown_reports": 0,
        "logs": 0,
        "other": 0,
    }
    if not root.exists():
        return counts
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix().lower()
        ext = p.suffix.lower()
        counts["files_total"] += 1
        try:
            counts["bytes_total"] += p.stat().st_size
        except OSError:
            pass
        if ext in {".png", ".jpg", ".jpeg", ".webp"} or "/screenshots/" in f"/{rel}":
            counts["screenshots"] += 1
        elif ext == ".json":
            counts["json_reports"] += 1
        elif ext == ".csv":
            counts["csv_tables"] += 1
        elif ext in {".md", ".markdown"}:
            counts["markdown_reports"] += 1
        elif ext in {".log", ".txt"} or "/logs/" in f"/{rel}":
            counts["logs"] += 1
        else:
            counts["other"] += 1
    return counts


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_owner_report(path: Path, title: str, report: Dict[str, object]) -> None:
    lines = [f"# {title}", "", f"Generated: `{report.get('generated_at_utc')}`", "", "## Summary", ""]
    for k, v in (report.get("summary") or {}).items():
        lines.append(f"- {k}: `{v}`")
    if report.get("manifest"):
        lines += ["", "## Manifest", ""]
        manifest = report["manifest"]
        if isinstance(manifest, dict):
            for k in ["evidence_pack_id", "patch_id", "storage_zone", "retention_class", "pack_path", "raw_buffer_deleted"]:
                if k in manifest:
                    lines.append(f"- {k}: `{manifest[k]}`")
    if report.get("notes"):
        lines += ["", "## Notes", ""]
        for note in report["notes"]:
            lines.append(f"- {note}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def init_buffer(args: argparse.Namespace, out_dir: Path) -> Dict[str, object]:
    patch_id = safe_id(args.patch_id)
    vault_root = Path(args.vault_root)
    buffer_root = vault_root / "buffer" / "active" / patch_id
    manifest = {
        "evidence_pack_id": f"EVP-{patch_id}",
        "patch_id": patch_id,
        "created_at_utc": utc_now(),
        "source_repo_head": git_head(Path(args.repo_root)),
        "h_contour": True,
        "storage_zone": "HOT_BUFFER",
        "retention_class": args.retention_class,
        "ttl_hours": args.ttl_hours,
        "buffer_path": str(buffer_root),
        "raw_buffer_deleted": False,
        "contents": count_contents(buffer_root),
    }
    actions = []
    if not args.dry_run:
        for sub in BUFFER_SUBDIRS:
            (buffer_root / sub).mkdir(parents=True, exist_ok=True)
        write_json(buffer_root / "MANIFEST_DRAFT.json", manifest)
        actions.append(f"created_buffer:{buffer_root}")
    else:
        actions.append(f"dry_run_would_create_buffer:{buffer_root}")
    return {
        "status": "PASS",
        "surface": SURFACE,
        "version": VERSION,
        "generated_at_utc": utc_now(),
        "mode": "init",
        "dry_run": bool(args.dry_run),
        "summary": {"actions_total": len(actions), "buffer_subdirs": len(BUFFER_SUBDIRS)},
        "manifest": manifest,
        "actions": actions,
        "output_root": str(out_dir),
    }


def zip_dir(src: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for p in sorted(src.rglob("*")):
            if p.is_file():
                zf.write(p, p.relative_to(src).as_posix())


def seal_buffer(args: argparse.Namespace, out_dir: Path) -> Dict[str, object]:
    patch_id = safe_id(args.patch_id)
    repo_root = Path(args.repo_root)
    vault_root = Path(args.vault_root)
    buffer_root = vault_root / "buffer" / "active" / patch_id
    if not buffer_root.exists():
        return {
            "status": "FAIL",
            "surface": SURFACE,
            "version": VERSION,
            "generated_at_utc": utc_now(),
            "mode": "seal",
            "summary": {"errors_total": 1},
            "errors": [f"buffer_not_found:{buffer_root}"],
            "output_root": str(out_dir),
        }
    now = datetime.now(timezone.utc)
    pack_dir = vault_root / "packs" / f"{now.year:04d}" / f"{now.month:02d}" / patch_id
    zip_path = pack_dir / "EVIDENCE_PACK.zip"
    manifest_path = pack_dir / "EVIDENCE_MANIFEST.json"
    owner_path = pack_dir / "OWNER_SUMMARY_RU.md"
    machine_path = pack_dir / "MACHINE_INDEX.json"
    sums_path = pack_dir / "SHA256SUMS.txt"
    actions = []
    contents = count_contents(buffer_root)
    if not args.dry_run:
        pack_dir.mkdir(parents=True, exist_ok=True)
        zip_dir(buffer_root, zip_path)
        digest = sha256_file(zip_path)
        manifest = {
            "evidence_pack_id": f"EVP-{patch_id}",
            "patch_id": patch_id,
            "created_at_utc": utc_now(),
            "source_repo_head": git_head(repo_root),
            "h_contour": True,
            "storage_zone": "SEALED_PACK",
            "retention_class": args.retention_class,
            "ttl_hours": args.ttl_hours,
            "pack_path": str(zip_path),
            "manifest_path": str(manifest_path),
            "owner_summary_path": str(owner_path),
            "machine_index_path": str(machine_path),
            "sha256": digest,
            "raw_buffer_deleted": False,
            "contents": contents,
        }
        write_json(manifest_path, manifest)
        write_json(machine_path, {"manifest": manifest, "contents": contents})
        sums_path.write_text(f"{digest}  EVIDENCE_PACK.zip\n", encoding="utf-8")
        write_owner_report(owner_path, "Evidence Pack Owner Summary V0.1", {
            "generated_at_utc": utc_now(),
            "summary": contents,
            "manifest": manifest,
            "notes": ["Evidence sealed into ZIP.", "Raw buffer deletion requires explicit flag."],
        })
        index = vault_root / "indexes" / "evidence_pack_index.jsonl"
        index.parent.mkdir(parents=True, exist_ok=True)
        with index.open("a", encoding="utf-8") as f:
            f.write(json.dumps(manifest, ensure_ascii=False) + "\n")
        write_json(vault_root / "indexes" / "latest_manifest.json", manifest)
        actions.append(f"sealed_pack:{zip_path}")
        if args.delete_raw_after_seal:
            shutil.rmtree(buffer_root)
            manifest["raw_buffer_deleted"] = True
            write_json(manifest_path, manifest)
            write_json(vault_root / "indexes" / "latest_manifest.json", manifest)
            actions.append(f"deleted_raw_buffer:{buffer_root}")
    else:
        digest = "DRY_RUN"
        manifest = {
            "evidence_pack_id": f"EVP-{patch_id}",
            "patch_id": patch_id,
            "created_at_utc": utc_now(),
            "source_repo_head": git_head(repo_root),
            "h_contour": True,
            "storage_zone": "SEALED_PACK",
            "retention_class": args.retention_class,
            "ttl_hours": args.ttl_hours,
            "pack_path": str(zip_path),
            "sha256": digest,
            "raw_buffer_deleted": False,
            "contents": contents,
        }
        actions.append(f"dry_run_would_seal:{zip_path}")
    return {
        "status": "PASS",
        "surface": SURFACE,
        "version": VERSION,
        "generated_at_utc": utc_now(),
        "mode": "seal",
        "dry_run": bool(args.dry_run),
        "summary": {"actions_total": len(actions), **contents},
        "manifest": manifest,
        "actions": actions,
        "output_root": str(out_dir),
    }


def inspect_vault(args: argparse.Namespace, out_dir: Path) -> Dict[str, object]:
    vault_root = Path(args.vault_root)
    roots = {
        "buffer_active": vault_root / "buffer" / "active",
        "packs": vault_root / "packs",
        "indexes": vault_root / "indexes",
        "quarantine": vault_root / "quarantine",
    }
    summary = {}
    for name, p in roots.items():
        dirs = 0
        files = 0
        bytes_total = 0
        if p.exists():
            for item in p.rglob("*"):
                if item.is_dir():
                    dirs += 1
                elif item.is_file():
                    files += 1
                    try:
                        bytes_total += item.stat().st_size
                    except OSError:
                        pass
        summary[f"{name}_dirs"] = dirs
        summary[f"{name}_files"] = files
        summary[f"{name}_bytes"] = bytes_total
    return {
        "status": "PASS",
        "surface": SURFACE,
        "version": VERSION,
        "generated_at_utc": utc_now(),
        "mode": "inspect",
        "summary": summary,
        "output_root": str(out_dir),
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--vault-root", default=r"E:\IMPERIUM_EVIDENCE_VAULT")
    ap.add_argument("--patch-id", default="UNNAMED-PATCH")
    ap.add_argument("--mode", choices=["init", "seal", "inspect"], default="inspect")
    ap.add_argument("--out-root", default=r"E:\_LOCAL_HANDOFF\SERVITOR_OUTPUTS")
    ap.add_argument("--retention-class", default="PINNED_EVIDENCE", choices=["PINNED_EVIDENCE", "TTL_48", "OWNER_REVIEW", "PURGE_ALLOWED"])
    ap.add_argument("--ttl-hours", type=int, default=None)
    ap.add_argument("--delete-raw-after-seal", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    out_dir = Path(args.out_root) / f"EVIDENCE_VAULT_PACKAGER_{stamp()}"
    if not args.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)
    else:
        out_dir.mkdir(parents=True, exist_ok=True)

    if args.mode == "init":
        report = init_buffer(args, out_dir)
    elif args.mode == "seal":
        report = seal_buffer(args, out_dir)
    else:
        report = inspect_vault(args, out_dir)

    write_json(out_dir / "MACHINE_REPORT.json", report)
    write_owner_report(out_dir / "OWNER_READABLE_REPORT_RU.md", "Mechanicus Evidence Vault Packager Report V0.1", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if str(report.get("status", "")).startswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
