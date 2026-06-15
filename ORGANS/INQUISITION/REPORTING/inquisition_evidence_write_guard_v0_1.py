#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inquisition Evidence Write Guard V0.1

Read-only auditor for evidence/storage discipline.
It flags raw evidence/runtime/cache in source repo and checks Evidence Vault structure.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

VERSION = "0.1.0"
SURFACE = "INQUISITION_EVIDENCE_WRITE_GUARD_V0_1"
SKIP_DIRS = {".git", "node_modules", ".venv", "venv"}
SOURCE_CACHE_DIRS = {"__pycache__", ".pytest_cache", "playwright-report", "test-results"}
SOURCE_CACHE_EXTS = {".pyc", ".pyo", ".coverage"}
EVIDENCE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".mp4", ".har"}
ARCHIVE_EXTS = {".zip", ".7z", ".tar", ".gz", ".tgz"}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


@dataclass
class Finding:
    severity: str
    risk_type: str
    path: str
    storage_zone: str
    evidence: str
    recommended_action: str
    cleanup_lane: str
    source_allowed: bool
    ttl_hours: Optional[int]
    size_bytes: int


def rel(p: Path, root: Path) -> str:
    try:
        return p.relative_to(root).as_posix()
    except Exception:
        return str(p)


def iter_repo_files(repo_root: Path):
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        current = Path(dirpath)
        for d in list(dirnames):
            if d in SOURCE_CACHE_DIRS:
                yield current / d
        for fn in filenames:
            yield current / fn


def scan_repo(repo_root: Path) -> List[Finding]:
    findings: List[Finding] = []
    for p in iter_repo_files(repo_root):
        rp = rel(p, repo_root)
        lower = rp.lower()
        try:
            size = p.stat().st_size if p.is_file() else 0
        except OSError:
            size = 0
        if p.is_dir() and p.name in SOURCE_CACHE_DIRS:
            findings.append(Finding(
                severity="WARNING",
                risk_type="SOURCE_RUNTIME_CACHE",
                path=rp,
                storage_zone="SOURCE_REPO",
                evidence="Runtime/cache directory exists under source repo.",
                recommended_action="Clean cache from source and keep ignored by .gitignore.",
                cleanup_lane="SOURCE_CACHE_CLEAN",
                source_allowed=False,
                ttl_hours=48,
                size_bytes=0,
            ))
            continue
        if not p.is_file():
            continue
        ext = p.suffix.lower()
        if ext in SOURCE_CACHE_EXTS or any(part in SOURCE_CACHE_DIRS for part in p.parts):
            findings.append(Finding("WARNING", "SOURCE_RUNTIME_CACHE", rp, "SOURCE_REPO", "Runtime/cache file exists under source repo.", "Clean cache from source and keep ignored by .gitignore.", "SOURCE_CACHE_CLEAN", False, 48, size))
        elif ext in EVIDENCE_EXTS or "screenshot" in lower or "playwright-report" in lower or "test-results" in lower:
            findings.append(Finding("WARNING", "SOURCE_EVIDENCE_LEAK", rp, "SOURCE_REPO", "Raw evidence/screenshot/test artifact exists under source repo.", "Move to Evidence Vault buffer or classify as fixture by owner-reviewed patch.", "OWNER_REVIEW_MOVE", False, None, size))
        elif ext in ARCHIVE_EXTS:
            findings.append(Finding("WARNING", "SOURCE_ARCHIVE_REVIEW", rp, "SOURCE_REPO", "Archive exists under source repo.", "Classify lifecycle: fixture/source/archive-review/quarantine/local handoff.", "OWNER_REVIEW_CLASSIFY", False, None, size))
    return findings


def inspect_vault(vault_root: Path, ttl_hours: int) -> List[Finding]:
    findings: List[Finding] = []
    required = [vault_root / "buffer" / "active", vault_root / "packs", vault_root / "indexes", vault_root / "quarantine"]
    for p in required:
        if not p.exists():
            findings.append(Finding("CRITICAL", "EVIDENCE_VAULT_MISSING_ZONE", str(p), "EVIDENCE_VAULT", "Required Evidence Vault zone is missing.", "Create vault skeleton with Mechanicus evidence packager/apply script.", "BLOCK_AND_CLASSIFY", False, None, 0))
    active = vault_root / "buffer" / "active"
    now = datetime.now(timezone.utc).timestamp()
    if active.exists():
        for child in active.iterdir():
            if not child.is_dir():
                continue
            try:
                age_hours = (now - child.stat().st_mtime) / 3600
            except OSError:
                age_hours = 0
            if age_hours > ttl_hours:
                findings.append(Finding("WARNING", "UNSEALED_BUFFER_EXPIRED", str(child), "EVIDENCE_VAULT_BUFFER", f"Unsealed evidence buffer age {age_hours:.1f}h exceeds TTL {ttl_hours}h.", "Seal into evidence pack or quarantine by owner-reviewed gate.", "TTL_48_QUARANTINE", False, ttl_hours, 0))
    return findings


def counts(findings: List[Finding], field: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for f in findings:
        key = getattr(f, field)
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], kv[0])))


def write_csv(path: Path, rows: List[dict], fields: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def write_owner(path: Path, report: Dict[str, object]) -> None:
    lines = ["# Inquisition Evidence Write Guard Report V0.1", "", f"Status: **{report['status']}**", f"Generated: `{report['generated_at_utc']}`", "", "## Summary", ""]
    for k, v in report["summary"].items():
        lines.append(f"- {k}: `{v}`")
    lines += ["", "## Risk counts", ""]
    for k, v in report["risk_counts"].items():
        lines.append(f"- {k}: `{v}`")
    lines += ["", "## Cleanup lane counts", ""]
    for k, v in report["cleanup_lane_counts"].items():
        lines.append(f"- {k}: `{v}`")
    lines += ["", "## Notes", "", "- Source repo is not an evidence storage.", "- Raw evidence should be in Evidence Vault buffer and then sealed into pack.", "- TTL/quarantine does not delete source repo."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--vault-root", default=r"E:\IMPERIUM_EVIDENCE_VAULT")
    ap.add_argument("--out-root", default=r"E:\_LOCAL_HANDOFF\SERVITOR_OUTPUTS")
    ap.add_argument("--ttl-hours", type=int, default=48)
    args = ap.parse_args(argv)

    repo_root = Path(args.repo_root)
    vault_root = Path(args.vault_root)
    out_dir = Path(args.out_root) / f"INQUISITION_EVIDENCE_WRITE_GUARD_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    findings = scan_repo(repo_root) + inspect_vault(vault_root, args.ttl_hours)
    risk_counts = counts(findings, "risk_type")
    severity_counts = counts(findings, "severity")
    lane_counts = counts(findings, "cleanup_lane")
    rows = [asdict(f) for f in findings]
    fields = list(asdict(Finding("", "", "", "", "", "", "", False, None, 0)).keys())
    write_csv(out_dir / "findings.csv", rows, fields)
    write_csv(out_dir / "risk_counts.csv", [{"risk_type": k, "count": v} for k, v in risk_counts.items()], ["risk_type", "count"])
    write_csv(out_dir / "cleanup_lane_counts.csv", [{"cleanup_lane": k, "count": v} for k, v in lane_counts.items()], ["cleanup_lane", "count"])

    critical = severity_counts.get("CRITICAL", 0)
    warnings = severity_counts.get("WARNING", 0)
    status = "PASS" if not findings else "PASS_WITH_FINDINGS"
    report = {
        "status": status,
        "surface": SURFACE,
        "version": VERSION,
        "generated_at_utc": utc_now(),
        "repo_root": str(repo_root),
        "vault_root": str(vault_root),
        "summary": {
            "findings_total": len(findings),
            "critical_total": critical,
            "warning_total": warnings,
            "risk_types_detected": len(risk_counts),
            "cleanup_lanes_detected": len(lane_counts),
        },
        "risk_counts": risk_counts,
        "severity_counts": severity_counts,
        "cleanup_lane_counts": lane_counts,
        "findings_sample": rows[:40],
        "output_root": str(out_dir),
    }
    write_json(out_dir / "MACHINE_REPORT.json", report)
    write_owner(out_dir / "OWNER_READABLE_REPORT_RU.md", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
