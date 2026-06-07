from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED = {"workspace_id", "kernel_root", "active_task", "panels", "extensions", "tool_execution_mode", "unsafe_shell_available"}


def load_workspace(repo_root: Path) -> dict[str, Any]:
    path = repo_root / "ORGANS/IMPERIAL_IDE/WORKSPACE/workspace_state.json"
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def validate_workspace(repo_root: Path) -> dict[str, Any]:
    try:
        workspace = load_workspace(repo_root)
    except Exception as exc:
        return {"status": "BLOCKED", "error": str(exc)}
    missing = sorted(REQUIRED - set(workspace))
    unsafe = bool(workspace.get("unsafe_shell_available"))
    mode = workspace.get("tool_execution_mode")
    status = "PASS" if not missing and not unsafe and mode == "DRY_RUN_ONLY" else "BLOCKED"
    return {
        "status": status,
        "workspace_state_loaded": True,
        "missing_fields": missing,
        "unsafe_shell_available": unsafe,
        "tool_execution_mode": mode,
        "workspace": workspace,
    }
