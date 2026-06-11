#!/usr/bin/env python3
"""Inquisition Hygiene Janitor V0.1.

Read-only by default. It classifies source dirt, local TTL candidates and safe cleanup lanes.
Optional --execute-quarantine only moves local TTL candidates into _LOCAL_HANDOFF/QUARANTINE.
Optional --execute-source-cache-clean only removes obvious generated Python/cache files from source.
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
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

VERSION = "0.1.0"
SURFACE = "INQUISITION_HYGIENE_JANITOR_V0_1"

TEXT_EXT = {
    ".py", ".ps1", ".psm1", ".js", ".cjs", ".mjs", ".ts", ".tsx", ".html", ".css",
    ".json", ".jsonl", ".md", ".txt", ".csv", ".yaml", ".yml", ".toml", ".sql", ".sh"
}
TOOL_EXT = {".py", ".ps1", ".js", ".cjs", ".ts", ".sh"}
ARCHIVE_EXT = {".zip", ".7z", ".rar", ".tar", ".gz", ".tgz"}
SCREEN_EXT = {".png", ".jpg", ".jpeg", ".webp"}
CACHE_DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".cache"}
RUNTIME_DIR_NAMES = {"playwright-report", "test-results", "screenshots", "SERVITOR_OUTPUTS", "reports", "FINAL_REPORT_BUNDLES"}
MOJIBAKE_MARKERS = ["Рџ", "рџ", "В·", "в†", "вЂ", "ЊЂ", "њЃ", "нЬ", "нБ", "�"]
KNOWN_ORGANS = {
    "ADMINISTRATUM", "ASTRONOMICON", "CORE_GOVERNANCE", "CUSTODES", "DOCTRINARIUM",
    "IMPERIAL_IDE", "INQUISITION", "MECHANICUS", "OFFICIO_AGENTIS", "SCHOLA_IMPERIALIS",
    "SPECULUM", "STRATEGIUM", "SUPPORT"
}
LOCAL_ROOTS_DEFAULT = [
    r"E:\_LOCAL_HANDOFF\SERVITOR_OUTPUTS",
    r"E:\_LOCAL_HANDOFF\DEBUG_PACKS",
    r"E:\_LOCAL_HANDOFF\PATCH_BACKUPS",
    r"E:\IMPERIUM_LOCAL_HANDOFF\WARP_RUNS",
]

@dataclass
class Finding:
    severity: str
    risk_type: str
    path: str
    organ: str
    evidence: str
    recommended_action: str
    cleanup_lane: str
    source_allowed: bool
    ttl_hours: int | None = None
    size_bytes: int = 0
    mtime_utc: str = ""


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def rel_to(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except Exception:
        return str(path).replace("\\", "/")


def organ_for_rel(rel: str) -> str:
    parts = rel.split("/")
    if len(parts) >= 2 and parts[0] == "ORGANS":
        return parts[1]
    return "ROOT"


def file_mtime_utc(path: Path) -> str:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return ""


def safe_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except Exception:
        return 0


def is_tool_like(path: Path) -> bool:
    name = path.name.lower()
    if path.suffix.lower() not in TOOL_EXT:
        return False
    hints = ["tool", "runner", "scanner", "auditor", "builder", "checker", "validator", "launcher", "bridge", "manager", "smoke", "probe", "packager"]
    return any(h in name for h in hints)


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "utf-8", "cp1251"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def load_registered_paths(repo: Path) -> set[str]:
    candidates = [
        repo / "ORGANS" / "MECHANICUS" / "TOOL_INTELLIGENCE" / "PASSPORTS" / "seed_tool_passports_v0_1.json",
    ]
    registered = set()
    for p in candidates:
        if not p.exists():
            continue
        try:
            data = json.loads(read_text(p))
        except Exception:
            continue
        tools = data.get("tools") or data.get("seed_tool_passports") or []
        if isinstance(tools, dict):
            tools = list(tools.values())
        for t in tools:
            if not isinstance(t, dict):
                continue
            for key in ("path", "script_path", "primary_path"):
                v = t.get(key)
                if isinstance(v, str) and v:
                    registered.add(v.replace("\\", "/"))
            for key in ("paths", "source_paths"):
                vals = t.get(key)
                if isinstance(vals, list):
                    for v in vals:
                        if isinstance(v, str):
                            registered.add(v.replace("\\", "/"))
    return registered


def git_untracked(repo: Path) -> set[str]:
    try:
        cp = subprocess.run(["git", "-C", str(repo), "ls-files", "--others", "--exclude-standard"], capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        return {line.strip().replace("\\", "/") for line in cp.stdout.splitlines() if line.strip()}
    except Exception:
        return set()


def scan_source(repo: Path, ttl_hours: int) -> list[Finding]:
    findings: list[Finding] = []
    registered = load_registered_paths(repo)
    untracked = git_untracked(repo)

    organs_root = repo / "ORGANS"
    if organs_root.exists():
        for child in organs_root.iterdir():
            if child.is_dir() and child.name not in KNOWN_ORGANS:
                rel = rel_to(child, repo)
                findings.append(Finding("CRITICAL", "UNKNOWN_ORGAN_FOLDER", rel, child.name, "Directory under ORGANS is not in approved organ list.", "Register organ/folder or move/quarantine by owner-reviewed patch.", "BLOCK_AND_CLASSIFY", False, ttl_hours, 0, file_mtime_utc(child)))

    skip_parts = {".git", "node_modules", ".venv", "venv"}
    for p in repo.rglob("*"):
        if any(part in skip_parts for part in p.parts):
            continue
        rel = rel_to(p, repo)
        organ = organ_for_rel(rel)
        name = p.name
        lower = name.lower()
        if p.is_dir():
            if name in CACHE_DIR_NAMES:
                findings.append(Finding("WARNING", "SOURCE_GENERATED_CACHE", rel, organ, "Generated cache directory exists in source tree.", "Delete if untracked/generated; add ignore rule if needed.", "SOURCE_CACHE_CLEAN", False, ttl_hours, 0, file_mtime_utc(p)))
            elif name in RUNTIME_DIR_NAMES and "ORGANS/" in rel:
                findings.append(Finding("CRITICAL", "SOURCE_RUNTIME_EVIDENCE_LEAK", rel, organ, "Runtime/evidence-like directory exists inside source tree.", "Classify as fixture/source or move to local handoff by owner-reviewed patch.", "OWNER_REVIEW_MOVE", False, ttl_hours, 0, file_mtime_utc(p)))
            continue
        ext = p.suffix.lower()
        size = safe_size(p)
        if ext in {".pyc", ".pyo"}:
            findings.append(Finding("WARNING", "SOURCE_GENERATED_CACHE", rel, organ, "Compiled Python cache file exists in source tree.", "Delete if untracked/generated.", "SOURCE_CACHE_CLEAN", False, ttl_hours, size, file_mtime_utc(p)))
        if ext in ARCHIVE_EXT:
            findings.append(Finding("WARNING", "ARCHIVE_REVIEW_REQUIRED", rel, organ, "Archive file exists under source tree.", "Classify lifecycle: fixture/source/archive-review/quarantine/local handoff.", "OWNER_REVIEW_CLASSIFY", False, None, size, file_mtime_utc(p)))
        if ext in SCREEN_EXT and ("screenshot" in lower or "playwright" in rel.lower() or "reports" in rel.lower()):
            findings.append(Finding("WARNING", "SOURCE_SCREENSHOT_OR_EVIDENCE", rel, organ, "Image/screenshot-like evidence exists under source tree.", "Move runtime screenshots to local handoff unless it is a documented fixture.", "OWNER_REVIEW_MOVE", False, ttl_hours, size, file_mtime_utc(p)))
        if is_tool_like(p):
            if rel not in registered:
                findings.append(Finding("WARNING", "NO_TOOL_PASSPORT", rel, organ, "Tool-like script not present in Mechanicus seed tool passports.", "Create tool passport or classify as legacy/quarantine/not-a-tool.", "MECHANICUS_PASSPORT_QUEUE", True, None, size, file_mtime_utc(p)))
        if ext in TEXT_EXT:
            try:
                text = read_text(p)
            except Exception:
                text = ""
            hits = [m for m in MOJIBAKE_MARKERS if m in text]
            if hits:
                findings.append(Finding("CRITICAL", "ENCODING_MOJIBAKE", rel, organ, "Mojibake marker(s): " + ", ".join(hits[:6]), "Repair source encoding and add UTF-8 guard.", "BLOCK_AND_REPAIR", False, None, size, file_mtime_utc(p)))
            if ext in {".json", ".py", ".js", ".cjs"} and "writes_allowed" in text and "safety" not in text:
                findings.append(Finding("CRITICAL", "WRITE_ACTION_WITHOUT_SAFETY", rel, organ, "writes_allowed appears without nearby safety declaration.", "Add safety/passport or block action registration.", "BLOCK_AND_REVIEW", False, None, size, file_mtime_utc(p)))
    return findings


def local_ttl_candidates(local_roots: list[Path], ttl_hours: int) -> list[Finding]:
    findings: list[Finding] = []
    cutoff = datetime.now(timezone.utc).timestamp() - ttl_hours * 3600
    for root in local_roots:
        if not root.exists():
            continue
        for p in root.iterdir():
            try:
                st = p.stat()
            except Exception:
                continue
            if st.st_mtime <= cutoff:
                findings.append(Finding("INFO", "LOCAL_TTL_EXPIRED", str(p), "LOCAL_HANDOFF", f"Local runtime/evidence item older than TTL-{ttl_hours}h.", "Quarantine or delete after owner-approved TTL policy.", "TTL_48_QUARANTINE", True, ttl_hours, st.st_size if p.is_file() else 0, datetime.fromtimestamp(st.st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")))
    return findings


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def write_report(out_dir: Path, repo: Path, source_findings: list[Finding], ttl_findings: list[Finding], execute_summary: dict) -> dict:
    all_findings = source_findings + ttl_findings
    risk_counts: dict[str, int] = {}
    severity_counts: dict[str, int] = {}
    cleanup_counts: dict[str, int] = {}
    for f in all_findings:
        risk_counts[f.risk_type] = risk_counts.get(f.risk_type, 0) + 1
        severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1
        cleanup_counts[f.cleanup_lane] = cleanup_counts.get(f.cleanup_lane, 0) + 1
    status = "PASS" if not all_findings else "PASS_WITH_FINDINGS"
    report = {
        "status": status,
        "surface": SURFACE,
        "version": VERSION,
        "generated_at_utc": utc_now(),
        "repo_root": str(repo),
        "summary": {
            "findings_total": len(all_findings),
            "source_findings_total": len(source_findings),
            "local_ttl_candidates_total": len(ttl_findings),
            "critical_total": severity_counts.get("CRITICAL", 0),
            "warning_total": severity_counts.get("WARNING", 0),
            "info_total": severity_counts.get("INFO", 0),
            "risk_types_detected": len(risk_counts),
            "cleanup_lanes_detected": len(cleanup_counts),
        },
        "risk_counts": dict(sorted(risk_counts.items(), key=lambda kv: (-kv[1], kv[0]))),
        "severity_counts": severity_counts,
        "cleanup_lane_counts": cleanup_counts,
        "execute_summary": execute_summary,
        "findings_sample": [asdict(f) for f in all_findings[:80]],
        "output_root": str(out_dir),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "MACHINE_REPORT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(out_dir / "findings.csv", [asdict(f) for f in all_findings], list(asdict(Finding("", "", "", "", "", "", "", False)).keys()))
    write_csv(out_dir / "ttl_candidates.csv", [asdict(f) for f in ttl_findings], list(asdict(Finding("", "", "", "", "", "", "", False)).keys()))
    write_csv(out_dir / "cleanup_plan.csv", [asdict(f) for f in all_findings if f.cleanup_lane not in {"MECHANICUS_PASSPORT_QUEUE"}], list(asdict(Finding("", "", "", "", "", "", "", False)).keys()))
    write_csv(out_dir / "risk_counts.csv", [{"risk_type": k, "count": v} for k, v in report["risk_counts"].items()], ["risk_type", "count"])
    md = [
        "# Inquisition Hygiene Janitor Report V0.1",
        "",
        f"Status: **{status}**",
        f"Generated: `{report['generated_at_utc']}`",
        f"Repo: `{repo}`",
        "",
        "## Summary",
        "",
    ]
    for k, v in report["summary"].items():
        md.append(f"- {k}: `{v}`")
    md += ["", "## Risk counts", ""]
    for k, v in report["risk_counts"].items():
        md.append(f"- {k}: `{v}`")
    md += ["", "## Cleanup lane counts", ""]
    for k, v in cleanup_counts.items():
        md.append(f"- {k}: `{v}`")
    md += ["", "## First recommendations", "", "- Do not delete source files automatically.", "- TTL-48 local outputs should be quarantined first, then deleted by separate gate.", "- Connect these findings to Data Atlas entity cards.", "- Convert NO_TOOL_PASSPORT lane into Mechanicus passport backlog.", "- Treat ENCODING_MOJIBAKE and SOURCE_RUNTIME_EVIDENCE_LEAK as blocking lanes."]
    if execute_summary.get("actions"):
        md += ["", "## Executed actions", ""]
        for item in execute_summary["actions"][:50]:
            md.append(f"- {item}")
    (out_dir / "OWNER_READABLE_REPORT_RU.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return report


def cleanup_source_cache(repo: Path, source_findings: list[Finding]) -> list[str]:
    actions = []
    targets = [f for f in source_findings if f.cleanup_lane == "SOURCE_CACHE_CLEAN"]
    untracked = git_untracked(repo)
    for f in targets:
        p = repo / f.path.replace("/", os.sep)
        rel = f.path
        # Only remove known generated caches. If git sees it as tracked, skip.
        if rel not in untracked and p.is_file():
            actions.append(f"SKIP tracked or unknown file: {rel}")
            continue
        try:
            if p.is_dir() and p.name in CACHE_DIR_NAMES:
                shutil.rmtree(p)
                actions.append(f"REMOVED source cache dir: {rel}")
            elif p.is_file() and p.suffix.lower() in {".pyc", ".pyo"}:
                p.unlink()
                actions.append(f"REMOVED source cache file: {rel}")
        except Exception as exc:
            actions.append(f"ERROR removing {rel}: {exc}")
    return actions


def quarantine_local(ttl_findings: list[Finding], quarantine_root: Path) -> list[str]:
    actions = []
    stamp = now_stamp()
    qroot = quarantine_root / f"TTL_48_QUARANTINE_{stamp}"
    qroot.mkdir(parents=True, exist_ok=True)
    for f in ttl_findings:
        p = Path(f.path)
        if not p.exists():
            continue
        try:
            drive_safe = str(p).replace(":", "").replace("\\", "__").replace("/", "__")
            dest = qroot / drive_safe
            if p.is_dir():
                shutil.move(str(p), str(dest))
                actions.append(f"QUARANTINED dir: {p} -> {dest}")
            elif p.is_file():
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(p), str(dest))
                actions.append(f"QUARANTINED file: {p} -> {dest}")
        except Exception as exc:
            actions.append(f"ERROR quarantining {p}: {exc}")
    return actions


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--out-root", default=r"E:\_LOCAL_HANDOFF\SERVITOR_OUTPUTS")
    ap.add_argument("--ttl-hours", type=int, default=48)
    ap.add_argument("--local-root", action="append", default=[])
    ap.add_argument("--execute-source-cache-clean", action="store_true")
    ap.add_argument("--execute-quarantine-local-ttl", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()
    out_root = Path(args.out_root)
    out_dir = out_root / f"INQUISITION_HYGIENE_JANITOR_{now_stamp()}"
    local_roots = [Path(x) for x in (args.local_root or LOCAL_ROOTS_DEFAULT)]
    source_findings = scan_source(repo, args.ttl_hours)
    ttl_findings = local_ttl_candidates(local_roots, args.ttl_hours)
    execute_summary = {"executed": False, "actions": []}
    if args.execute_source_cache_clean:
        execute_summary["executed"] = True
        execute_summary["actions"].extend(cleanup_source_cache(repo, source_findings))
    if args.execute_quarantine_local_ttl:
        execute_summary["executed"] = True
        execute_summary["actions"].extend(quarantine_local(ttl_findings, Path(r"E:\_LOCAL_HANDOFF\QUARANTINE")))
    report = write_report(out_dir, repo, source_findings, ttl_findings, execute_summary)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
