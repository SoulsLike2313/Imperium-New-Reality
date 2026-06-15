#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inquisition gate for Imperium Intelligence Pack hygiene."""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sqlite3
import sys
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Optional

SURFACE = "INQUISITION_INTELLIGENCE_PACK_HYGIENE_GATE_V0_1"
VERSION = "0.1.0"
REQUIRED = {
    "MANIFEST.json",
    "GIT_TRUTH.json",
    "TREE_INDEX.jsonl",
    "FILE_KIND_COUNTS.json",
    "ORGAN_MAP.json",
    "TOOL_PASSPORT_INDEX.json",
    "DEPENDENCY_EDGES.jsonl",
    "SOURCE_SLICE_MANIFEST.json",
    "ATLAS_INDEX.sqlite",
    "OWNER_SUMMARY_RU.md",
}
FORBIDDEN_PARTS = (".imperium_patch_backups/", "_LOCAL_HANDOFF/", "LOCAL_HANDOFF/", "__pycache__/", ".pytest_cache/", "node_modules/", "playwright-report/", "test-results/")
FORBIDDEN_SUFFIXES = (".pyc", ".pyo", ".trace.zip", ".har")
FORBIDDEN_BINARY_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".zip", ".7z", ".tar", ".gz", ".pdf")


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_entries_from_zip(path: Path) -> Dict[str, bytes]:
    data = {}
    with zipfile.ZipFile(path, "r") as zf:
        for info in zf.infolist():
            if not info.is_dir():
                with zf.open(info, "r") as f:
                    data[info.filename.replace("\\", "/")] = f.read()
    return data


def read_entries_from_dir(path: Path) -> Dict[str, bytes]:
    data = {}
    for p in path.rglob("*"):
        if p.is_file():
            rel = p.relative_to(path).as_posix()
            data[rel] = p.read_bytes()
    return data


def load_pack(path: Path) -> Dict[str, bytes]:
    if path.is_file() and path.suffix.lower() == ".zip":
        return read_entries_from_zip(path)
    if path.is_dir():
        return read_entries_from_dir(path)
    raise SystemExit(f"Pack path is not a zip or directory: {path}")


def sqlite_probe(sqlite_bytes: bytes) -> Dict[str, object]:
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
        tmp.write(sqlite_bytes)
        tmp_path = tmp.name
    try:
        con = sqlite3.connect(tmp_path)
        try:
            tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
            file_count = con.execute("SELECT COUNT(*) FROM files").fetchone()[0] if "files" in tables else None
            edge_count = con.execute("SELECT COUNT(*) FROM edges").fetchone()[0] if "edges" in tables else None
            return {"ok": True, "tables": tables, "file_count": file_count, "edge_count": edge_count}
        finally:
            con.close()
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def evaluate(entries: Dict[str, bytes], max_pack_mb: int) -> Dict[str, object]:
    names = set(entries)
    missing = sorted(REQUIRED - names)
    forbidden = []
    nested_archives = []
    binary_slices = []
    for name in sorted(names):
        low = name.lower()
        if any(part.lower() in low for part in FORBIDDEN_PARTS) or low.endswith(FORBIDDEN_SUFFIXES):
            forbidden.append(name)
        if name.startswith("PATCH_TARGET_SLICES/") and low.endswith(FORBIDDEN_BINARY_SUFFIXES):
            binary_slices.append(name)
        if low.endswith((".zip", ".7z", ".tar", ".gz")):
            nested_archives.append(name)
    manifest = None
    try:
        manifest = json.loads(entries.get("MANIFEST.json", b"{}").decode("utf-8"))
    except Exception as exc:
        missing.append(f"MANIFEST.json:invalid_json:{exc}")
    edges_count = 0
    if "DEPENDENCY_EDGES.jsonl" in entries:
        edges_count = len([x for x in entries["DEPENDENCY_EDGES.jsonl"].decode("utf-8", errors="replace").splitlines() if x.strip()])
    sqlite_status = sqlite_probe(entries["ATLAS_INDEX.sqlite"]) if "ATLAS_INDEX.sqlite" in entries else {"ok": False, "error": "missing"}
    pack_size = sum(len(v) for v in entries.values())
    findings = []
    if missing:
        findings.append({"finding_id": "INTELLIGENCE_PACK_REQUIRED_ARTIFACTS_MISSING", "severity": "CRITICAL", "count": len(missing), "sample": missing[:20]})
    if forbidden:
        findings.append({"finding_id": "INTELLIGENCE_PACK_FORBIDDEN_LOCAL_OR_RUNTIME_PATH", "severity": "CRITICAL", "count": len(forbidden), "sample": forbidden[:20]})
    if nested_archives:
        findings.append({"finding_id": "INTELLIGENCE_PACK_NESTED_ARCHIVE", "severity": "WARNING", "count": len(nested_archives), "sample": nested_archives[:20]})
    if binary_slices:
        findings.append({"finding_id": "INTELLIGENCE_PACK_BINARY_SOURCE_SLICE", "severity": "WARNING", "count": len(binary_slices), "sample": binary_slices[:20]})
    if not sqlite_status.get("ok"):
        findings.append({"finding_id": "INTELLIGENCE_PACK_SQLITE_INDEX_INVALID", "severity": "CRITICAL", "count": 1, "sample": [sqlite_status.get("error")]})
    if edges_count <= 0:
        findings.append({"finding_id": "INTELLIGENCE_PACK_NO_DEPENDENCY_EDGES", "severity": "CRITICAL", "count": 1, "sample": []})
    if pack_size > max_pack_mb * 1024 * 1024:
        findings.append({"finding_id": "INTELLIGENCE_PACK_TOO_LARGE", "severity": "WARNING", "count": 1, "sample": [pack_size]})
    blocking = any(f["severity"] == "CRITICAL" for f in findings)
    return {
        "status": "FAIL_INTELLIGENCE_PACK_HYGIENE" if blocking else "PASS_INTELLIGENCE_PACK_HYGIENE",
        "surface": SURFACE,
        "version": VERSION,
        "generated_at_utc": utc_now(),
        "blocking_gate": blocking,
        "severity": "CRITICAL" if blocking else ("WARNING" if findings else "INFO"),
        "checks": {
            "entries_total": len(entries),
            "required_missing_total": len(missing),
            "forbidden_paths_total": len(forbidden),
            "nested_archives_total": len(nested_archives),
            "binary_slices_total": len(binary_slices),
            "dependency_edges_total": edges_count,
            "sqlite_ok": bool(sqlite_status.get("ok")),
            "pack_payload_bytes": pack_size,
            "max_pack_mb": max_pack_mb,
        },
        "manifest_digest": manifest,
        "sqlite_status": sqlite_status,
        "findings": findings,
        "recommended_next_action_ru": "Use this pack as handoff if PASS; otherwise rebuild without forbidden/runtime/archive content.",
    }


def write_reports(root: Path, report: Dict[str, object]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "MACHINE_REPORT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Intelligence Pack Hygiene Gate", "", f"Status: {report['status']}", "", "## Checks"]
    for k, v in report.get("checks", {}).items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Findings")
    for f in report.get("findings", []):
        lines.append(f"- {f.get('severity')}: {f.get('finding_id')} ({f.get('count')})")
    (root / "OWNER_REPORT_RU.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Check Imperium Intelligence Pack hygiene")
    ap.add_argument("--pack", required=True, help="Pack zip or pack directory")
    ap.add_argument("--max-pack-mb", type=int, default=20)
    ap.add_argument("--out-report-root", default="")
    args = ap.parse_args(argv)
    entries = load_pack(Path(args.pack))
    report = evaluate(entries, args.max_pack_mb)
    if args.out_report_root:
        write_reports(Path(args.out_report_root), report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"].startswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
