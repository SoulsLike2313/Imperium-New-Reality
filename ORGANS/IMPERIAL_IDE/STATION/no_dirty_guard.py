from __future__ import annotations

import hashlib
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from read_only_policy import READ_ONLY_COMMANDS


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
    )
    return completed.stdout.rstrip("\r\n")


def _fingerprint(repo_root: Path) -> dict[str, Any]:
    unstaged = _git(repo_root, "diff", "--binary")
    staged = _git(repo_root, "diff", "--cached", "--binary")
    tracked_status = _git(repo_root, "status", "--porcelain=v1", "-uno")
    return {
        "tracked_status": tracked_status,
        "unstaged_diff_sha256": hashlib.sha256(unstaged.encode("utf-8", errors="replace")).hexdigest(),
        "staged_diff_sha256": hashlib.sha256(staged.encode("utf-8", errors="replace")).hexdigest(),
    }


def _file_set(root: Path) -> set[str]:
    if not root.is_dir():
        return set()
    return {path.as_posix() for path in root.rglob("*") if path.is_file()}


def run_readonly_no_dirty_smoke(repo_root: Path, commands: list[list[str]] | None = None) -> dict[str, Any]:
    repo = repo_root.resolve()
    command_args = commands or [[command] for command in READ_ONLY_COMMANDS]
    runtime_root = repo / "ORGANS" / "IMPERIAL_IDE" / "STATION" / "receipts" / "runtime"
    report_root = repo / "REPORTS"
    before = _fingerprint(repo)
    runtime_before = _file_set(runtime_root)
    reports_before = _file_set(report_root)
    results = []
    cli = repo / "ORGANS" / "IMPERIAL_IDE" / "SHELL" / "imperial_ide_cli.py"
    for item in command_args:
        completed = subprocess.run(
            [sys.executable, str(cli), *item, "--compact"],
            cwd=repo,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            check=False,
        )
        results.append({
            "command": item,
            "exit_code": completed.returncode,
            "stdout_prefix": completed.stdout[:240],
            "stderr_prefix": completed.stderr[:240],
        })
    after = _fingerprint(repo)
    runtime_after = _file_set(runtime_root)
    reports_after = _file_set(report_root)
    tracked_changed = before != after
    return {
        "status": "PASS" if not tracked_changed else "BLOCKED",
        "commands_tested": command_args,
        "command_results": results,
        "git_status_before": before["tracked_status"],
        "git_status_after": after["tracked_status"],
        "tracked_files_modified_by_readonly_commands": tracked_changed,
        "tracked_diff_before_after_equal": not tracked_changed,
        "runtime_receipts_written": sorted(runtime_after - runtime_before),
        "report_receipts_written": sorted(reports_after - reports_before),
        "pass": not tracked_changed,
        "blockers": [] if not tracked_changed else ["read-only command changed tracked git diff or index"],
        "timestamp": utc_now(),
    }
