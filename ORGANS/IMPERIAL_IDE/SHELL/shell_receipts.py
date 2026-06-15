from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TASK_ID = "TASK-NEWREALITY-IMPERIAL-IDE-OPERATIONAL-STATION-TRUTH-FIX-DAILY-OPS-SHELL-PC-V0_1"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_receipt(
    *,
    command: str,
    args: list[str],
    repo_root: Path,
    status: str,
    risk_class: str,
    data_sources: list[str],
    tools_invoked: list[str],
    dry_run: bool,
    mutates_repo: bool,
    output_summary: str,
    receipt_path: str | None = None,
) -> dict[str, Any]:
    return {
        "timestamp_utc": utc_now(),
        "task_id": TASK_ID,
        "command": command,
        "args": args,
        "repo_root": repo_root.as_posix(),
        "status": status,
        "risk_class": risk_class,
        "data_sources": data_sources,
        "tools_invoked": tools_invoked,
        "dry_run": dry_run,
        "mutates_repo": mutates_repo,
        "real_execution": False,
        "unsafe_shell_available": False,
        "output_summary": output_summary,
        "receipt_path": receipt_path,
    }


def write_receipt(receipt: dict[str, Any], path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path.as_posix()
