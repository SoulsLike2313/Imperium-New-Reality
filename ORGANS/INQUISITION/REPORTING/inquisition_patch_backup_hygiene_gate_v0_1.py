#!/usr/bin/env python3
"""Inquisition patch-backup hygiene gate v0.1.1.

Read-only gate for H/manual patch workflow. It detects local/operator zones that
must not be tracked in source history, especially .imperium_patch_backups/ after
apply_patch.ps1 backup creation.

V0.1.1 scope fix:
- block only repo-root local-only zones and hard runtime/cache artefacts;
- do not classify historical/source fixtures merely because their path contains
  words like "smoke", "harness", or "fixture".
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Sequence

SURFACE = "INQUISITION_PATCH_BACKUP_HYGIENE_GATE_V0_1"
VERSION = "0.1.1"

# Repo-root local/operator zones. These are never source.
FORBIDDEN_ROOTS_EXACT = {
    ".imperium_patch_backups",
    "_LOCAL_HANDOFF",
    "LOCAL_HANDOFF",
}

# Repo-root generated evidence smoke vaults. Root-only by design: nested source
# fixture paths that contain "smoke" are not blocked by this H1 gate.
FORBIDDEN_ROOT_PREFIXES = (
    "EVIDENCE_VAULT_SMOKE",
    "IMPERIUM_EVIDENCE_VAULT_SMOKE",
)

# Hard runtime/cache artefacts that are never source regardless of location.
FORBIDDEN_TRACKED_GLOBS = [
    "*.trace.zip",
    "*.har",
    "*.pyc",
    "**/*.pyc",
    "__pycache__/**",
    "**/__pycache__/**",
    ".pytest_cache/**",
    "**/.pytest_cache/**",
    "playwright-report/**",
    "**/playwright-report/**",
    "test-results/**",
    "**/test-results/**",
]

REQUIRED_GITIGNORE_PATTERNS = [
    ".imperium_patch_backups/",
    "_LOCAL_HANDOFF/",
    "LOCAL_HANDOFF/",
    "IMPERIUM_EVIDENCE_VAULT_SMOKE*/",
    "EVIDENCE_VAULT_SMOKE*/",
    "*_SMOKE*/",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_git(repo: Path, args: Sequence[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def normalize_git_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.strip("/")


def list_tracked(repo: Path) -> List[str]:
    result = run_git(repo, ["ls-files", "-z"])
    if not result.stdout:
        return []
    return [normalize_git_path(p) for p in result.stdout.split("\0") if p]


def tracked_status(repo: Path) -> List[str]:
    result = run_git(repo, ["status", "--short"], check=True)
    return [line.rstrip("\n") for line in result.stdout.splitlines() if line.strip()]


def root_segment(path: str) -> str:
    normalized = normalize_git_path(path)
    return normalized.split("/", 1)[0] if normalized else ""


def is_forbidden_tracked(path: str) -> bool:
    normalized = normalize_git_path(path)
    root = root_segment(normalized)
    if root in FORBIDDEN_ROOTS_EXACT:
        return True
    if any(root.startswith(prefix) for prefix in FORBIDDEN_ROOT_PREFIXES):
        return True
    for pattern in FORBIDDEN_TRACKED_GLOBS:
        if fnmatch.fnmatch(normalized, pattern):
            return True
    return False


def classify_forbidden(path: str) -> str:
    normalized = normalize_git_path(path)
    root = root_segment(normalized)
    if root == ".imperium_patch_backups":
        return "PATCH_BACKUP_TRACKED_IN_SOURCE"
    if root in {"_LOCAL_HANDOFF", "LOCAL_HANDOFF"}:
        return "HANDOFF_TRACKED_IN_SOURCE"
    if any(root.startswith(prefix) for prefix in FORBIDDEN_ROOT_PREFIXES):
        return "SMOKE_VAULT_TRACKED_IN_SOURCE"
    return "RUNTIME_CACHE_TRACKED_IN_SOURCE"


def read_gitignore(repo: Path) -> str:
    path = repo / ".gitignore"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def build_report(repo: Path) -> Dict[str, object]:
    repo = repo.resolve()
    tracked = list_tracked(repo)
    forbidden = sorted([path for path in tracked if is_forbidden_tracked(path)])
    gitignore_text = read_gitignore(repo)
    missing_gitignore = [p for p in REQUIRED_GITIGNORE_PATTERNS if p not in gitignore_text]
    status_lines = tracked_status(repo)

    staged_delete_backups = [
        line for line in status_lines
        if line.startswith("D") or line.startswith(" D") or line.startswith("D ")
        if ".imperium_patch_backups/" in normalize_git_path(line[3:] if len(line) > 3 else line)
    ]

    findings: List[Dict[str, object]] = []
    if forbidden:
        by_kind: Dict[str, List[str]] = {}
        for path in forbidden:
            by_kind.setdefault(classify_forbidden(path), []).append(path)
        for finding_id, paths in sorted(by_kind.items()):
            findings.append({
                "finding_id": finding_id,
                "severity": "CRITICAL",
                "count": len(paths),
                "sample": paths[:25],
                "recommended_action_ru": "Remove the local-only path from the git index, usually with git rm -r --cached --ignore-unmatch for the exact root.",
            })
    if missing_gitignore:
        findings.append({
            "finding_id": "MISSING_LOCAL_ONLY_GITIGNORE_RULES",
            "severity": "WARNING",
            "missing_patterns": missing_gitignore,
            "recommended_action_ru": "Append the managed IMPERIUM_H_LOCAL_ONLY_BLOCK_V0_8_9_2_H1 block to .gitignore.",
        })

    status = "PASS_PATCH_BACKUP_HYGIENE" if not forbidden and not missing_gitignore else "FAIL_PATCH_BACKUP_HYGIENE"
    severity = "INFO" if status.startswith("PASS") else ("CRITICAL" if forbidden else "WARNING")

    return {
        "status": status,
        "surface": SURFACE,
        "version": VERSION,
        "generated_at_utc": utc_now(),
        "repo": str(repo),
        "blocking_gate": bool(forbidden),
        "severity": severity,
        "scope_note": "Root-local-only zones only; historical tracked fixtures containing smoke/harness names are not blocked by H1.",
        "checks": {
            "tracked_files_total": len(tracked),
            "forbidden_tracked_files_total": len(forbidden),
            "required_gitignore_patterns_total": len(REQUIRED_GITIGNORE_PATTERNS),
            "missing_gitignore_patterns_total": len(missing_gitignore),
            "staged_backup_deletions_total": len(staged_delete_backups),
        },
        "forbidden_tracked_files": forbidden,
        "missing_gitignore_patterns": missing_gitignore,
        "staged_backup_deletions_sample": staged_delete_backups[:25],
        "findings": findings,
        "recommended_next_action_ru": "Commit the hygiene patch only after this report is PASS and git status contains no tracked local-only additions.",
    }


def write_reports(out_root: Path, report: Dict[str, object]) -> None:
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "MACHINE_REPORT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Inquisition Patch Backup Hygiene Gate v0.1.1",
        "",
        f"Status: `{report['status']}`",
        f"Severity: `{report['severity']}`",
        f"Repo: `{report['repo']}`",
        "",
        str(report.get("scope_note", "")),
        "",
        "## Checks",
        "",
    ]
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    if report.get("findings"):
        lines += ["", "## Findings", ""]
        for finding in report["findings"]:
            lines.append(f"- `{finding['finding_id']}` / `{finding['severity']}`")
    lines += ["", str(report.get("recommended_next_action_ru", "")), ""]
    (out_root / "OWNER_READABLE_REPORT_RU.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Read-only patch backup hygiene gate.")
    ap.add_argument("--repo", required=True, help="Path to H repository root")
    ap.add_argument("--out-report-root", default="", help="Optional report output root")
    args = ap.parse_args(argv)

    repo = Path(args.repo)
    if not (repo / ".git").exists():
        print(json.dumps({
            "status": "FAIL_NOT_A_GIT_REPO",
            "surface": SURFACE,
            "version": VERSION,
            "repo": str(repo),
        }, ensure_ascii=False, indent=2))
        return 2

    report = build_report(repo)
    if args.out_report_root:
        write_reports(Path(args.out_report_root), report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS_PATCH_BACKUP_HYGIENE" else 2


if __name__ == "__main__":
    sys.exit(main())
