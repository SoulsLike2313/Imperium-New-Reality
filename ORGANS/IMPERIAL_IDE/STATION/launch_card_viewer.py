from __future__ import annotations

from pathlib import Path
from typing import Any

from path_actions import actions_for_path
from taskpack_manager import inspect_taskpack


def view_launch_card(repo_root: Path, taskpack_id: str = "") -> dict[str, Any]:
    inspected = inspect_taskpack(repo_root, taskpack_id)
    if inspected.get("status") == "BLOCKED":
        return inspected
    task_id = inspected["taskpack_id"]
    command = f"TASK_ID: {task_id} start task"
    return {
        "status": "PASS_WITH_WARNINGS",
        "viewer": "LAUNCH_CARD",
        "task_id": task_id,
        "title": inspected.get("title", ""),
        "admission_state": "DRY_RUN_CANDIDATE",
        "canon_state": "CANDIDATE_NOT_CANON",
        "live_state": "NOT_LIVE_REGISTERED_BY_VIEWER",
        "handoff_ready": True,
        "execution_done": False,
        "copy_ready_servitor_prime_block": command,
        "taskpack_zip_path": inspected.get("taskpack_zip_path", ""),
        "taskpack_sha256": inspected.get("latest_taskpack_sha256", ""),
        "extracted_root_files_found": inspected.get("extracted_root_files_found", []),
        "raw_json_available": True,
        "path_actions": actions_for_path(repo_root, inspected.get("taskpack_path", "")),
        "human_summary": (
            "Launch card is ready for Servitor Prime handoff. "
            "This is not execution completion and not live registration."
        ),
    }
