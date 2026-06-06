#!/usr/bin/env python3
"""Detect active-use references to SUPPORT/QUESTIONABLE_OR_QUARANTINE."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260605-PC-CORE-SHAPE-DRIFT-CLEANUP-MIGRATION-QUEUE-QUARANTINE-GATE-V0_1"
QUARANTINE_INDEX = Path("SUPPORT/QUESTIONABLE_OR_QUARANTINE/QUARANTINE_INDEX.json")
NEEDLES = ("SUPPORT/QUESTIONABLE_OR_QUARANTINE", "SUPPORT\\QUESTIONABLE_OR_QUARANTINE")
SKIP_SUFFIXES = {
    ".zip",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".pdf",
    ".dll",
    ".exe",
    ".pyc",
    ".sqlite",
    ".db",
}
POLICY_REFERENCE_PREFIXES = (
    "ORGANS/_CORE_GOVERNANCE/",
    "ORGANS/ADMINISTRATUM/ADDRESS_BOOK/",
    "ORGANS/INQUISITION/QUARANTINE_POLICY/",
    "ORGANS/ADMINISTRATUM/MIGRATION_QUEUE/",
    "ORGANS/SCHOLA_IMPERIALIS/LEARNING/",
    "REPORTS/",
    "SUPPORT/QUESTIONABLE_OR_QUARANTINE/",
    "ORGANS/ASTRONOMICON/TASK_INBOX/",
)
POLICY_REFERENCE_FILES = {
    "SUPPORT/COMMON_IMPERIUM_SUPPORT/SUPPORT_ADDRESS_POLICY.md",
}
PRUNED_DIR_PREFIXES = (
    ".git/",
    "REPORTS/",
    "ORGANS/ASTRONOMICON/TASK_INBOX/",
    "ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/FIXTURES/",
    "ORGANS/ADMINISTRATUM/BUNDLE_GATE/FIXTURES/",
    "ORGANS/INQUISITION/REPORTS/",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def to_posix(path: Path) -> str:
    return str(path).replace("\\", "/")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def load_exceptions(repo_root: Path) -> list[dict[str, Any]]:
    index_path = repo_root / QUARANTINE_INDEX
    if not index_path.exists():
        return []
    data = json.loads(index_path.read_text(encoding="utf-8"))
    exceptions = data.get("allowed_active_use_exceptions", [])
    return exceptions if isinstance(exceptions, list) else []


def exception_matches(rel_path: str, exceptions: list[dict[str, Any]]) -> dict[str, Any] | None:
    for item in exceptions:
        if not isinstance(item, dict):
            continue
        pattern = item.get("path") or item.get("path_glob")
        if not isinstance(pattern, str) or not pattern:
            continue
        if rel_path == pattern or fnmatch.fnmatch(rel_path, pattern):
            return item
    return None


def is_policy_reference_path(rel_path: str) -> bool:
    return rel_path in POLICY_REFERENCE_FILES or rel_path.startswith(POLICY_REFERENCE_PREFIXES)


def should_scan(path: Path, rel_path: str) -> bool:
    if ".git/" in rel_path or rel_path.startswith(".git/"):
        return False
    if path.suffix.lower() in SKIP_SUFFIXES:
        return False
    if not path.is_file():
        return False
    try:
        if path.stat().st_size > 2_000_000:
            return False
    except OSError:
        return False
    return True


def is_pruned_dir(rel_path: str) -> bool:
    normalized = rel_path.strip("/")
    if not normalized:
        return False
    with_slash = normalized + "/"
    return any(with_slash.startswith(prefix) for prefix in PRUNED_DIR_PREFIXES)


def iter_candidate_files(repo_root: Path) -> tuple[list[Path], int]:
    files: list[Path] = []
    pruned_dir_count = 0
    for dirpath, dirnames, filenames in os.walk(repo_root):
        current = Path(dirpath)
        rel_current = to_posix(current.relative_to(repo_root)) if current != repo_root else ""
        kept_dirs = []
        for dirname in dirnames:
            child_rel = f"{rel_current}/{dirname}" if rel_current else dirname
            if is_pruned_dir(child_rel):
                pruned_dir_count += 1
                continue
            kept_dirs.append(dirname)
        dirnames[:] = kept_dirs
        for filename in filenames:
            files.append(current / filename)
    return files, pruned_dir_count


def read_text_or_none(path: Path) -> str | None:
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in raw[:4096]:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("utf-8", errors="replace")


def scan_file(repo_root: Path, path: Path, exceptions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rel_path = to_posix(path.relative_to(repo_root))
    text = read_text_or_none(path)
    if text is None:
        return []
    findings = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if not any(needle in line for needle in NEEDLES):
            continue
        matched_exception = exception_matches(rel_path, exceptions)
        if is_policy_reference_path(rel_path):
            reference_class = "POLICY_REFERENCE"
            severity = "INFO"
            active_use_violation = False
            reason = "Reference is in governance, policy, report, taskpack, migration queue, quarantine index, or Schola learning context."
        elif matched_exception is not None:
            reference_class = "ADMITTED_EXCEPTION"
            severity = "INFO"
            active_use_violation = False
            reason = f"Allowed by quarantine exception {matched_exception.get('exception_id', 'UNNAMED_EXCEPTION')}."
        else:
            reference_class = "ACTIVE_USE_REFERENCE"
            severity = "BLOCK"
            active_use_violation = True
            reason = "Active repository file references quarantine path without a salvage/admission exception."
        findings.append(
            {
                "path": rel_path,
                "line": line_no,
                "reference_class": reference_class,
                "severity": severity,
                "active_use_violation": active_use_violation,
                "reason": reason,
                "snippet": line.strip()[:240],
            }
        )
    return findings


def build_report(repo_root: Path, task_id: str) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    exceptions = load_exceptions(repo_root)
    findings: list[dict[str, Any]] = []
    scanned = 0
    candidate_files, pruned_dir_count = iter_candidate_files(repo_root)
    for path in candidate_files:
        rel_path = to_posix(path.relative_to(repo_root))
        if not should_scan(path, rel_path):
            continue
        scanned += 1
        findings.extend(scan_file(repo_root, path, exceptions))
    violations = [item for item in findings if item["active_use_violation"]]
    policy_refs = [item for item in findings if item["reference_class"] == "POLICY_REFERENCE"]
    admitted = [item for item in findings if item["reference_class"] == "ADMITTED_EXCEPTION"]
    blockers = [
        {
            "id": "ACTIVE_USE_OF_QUARANTINE_WITHOUT_EXCEPTION",
            "path": item["path"],
            "line": item["line"],
            "required_action": "Remove active dependency or create explicit salvage/admission exception.",
        }
        for item in violations
    ]
    return {
        "schema_version": "imperium.quarantine_active_use_check_report.v0_1",
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "verdict": "BLOCK" if blockers else "PASS",
        "repo_root": to_posix(repo_root),
        "quarantine_index_path": to_posix(QUARANTINE_INDEX),
        "pruned_dir_count": pruned_dir_count,
        "pruned_dir_prefixes": list(PRUNED_DIR_PREFIXES),
        "scanned_text_file_count": scanned,
        "reference_count": len(findings),
        "policy_reference_count": len(policy_refs),
        "admitted_exception_reference_count": len(admitted),
        "active_use_violation_count": len(violations),
        "findings": findings,
        "exceptions_loaded": exceptions,
        "blockers": blockers,
        "warnings": [],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check quarantine active-use references.")
    parser.add_argument("--repo-root", "--root", dest="repo_root", default=".")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--output", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(Path(args.repo_root), args.task_id)
    if args.output:
        write_json(Path(args.output), report)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["verdict"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
