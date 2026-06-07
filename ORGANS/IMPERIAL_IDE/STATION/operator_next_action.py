from __future__ import annotations

from typing import Any


def choose_next_action(board: dict[str, Any]) -> dict[str, Any]:
    safety = board.get("safety_state", {})
    dirty = board.get("dirty_state", {})
    taskpack = board.get("latest_taskpack", {})
    current_task = board.get("current_task", {})
    if safety.get("result") == "BLOCKED":
        action = "Review Safety Center blockers before task mutation."
        reason = "safety_blocked"
    elif dirty.get("secrets_detected") or dirty.get("local_configs"):
        action = "Remove secret/local-config paths from the staged or dirty set."
        reason = "dirty_safety_blocker"
    elif dirty.get("unknown_items"):
        action = "Classify unknown dirty paths before staging or push."
        reason = "unknown_dirty"
    elif taskpack.get("validation_status") == "PASS":
        action = "Review live registration promotion; do not run live registration unless Owner explicitly types LIVE."
        reason = "taskpack_ready_for_review"
    elif current_task.get("task_id"):
        action = "Inspect Daily Ops board, then build or validate the next taskpack."
        reason = "current_task_available"
    else:
        action = "Create a task intent and build a taskpack."
        reason = "no_current_task"
    return {
        "status": "PASS_WITH_WARNINGS",
        "next_action": action,
        "reason": reason,
        "real_execution_required": False,
        "live_registration_required": False,
    }
