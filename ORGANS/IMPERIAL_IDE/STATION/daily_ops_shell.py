from __future__ import annotations

from pathlib import Path
from typing import Any

from daily_ops_state import WORKFLOW_STEPS, build_daily_ops_board
from operator_next_action import choose_next_action


def daily_ops(repo_root: Path) -> dict[str, Any]:
    board = build_daily_ops_board(repo_root)
    return {
        "status": "PASS_WITH_WARNINGS",
        "surface": "DAILY_OPERATIONS",
        "board": board,
        "surfaces": ["daily-ops", "operator-board", "next-action", "task-flow"],
        "shows_current_task": bool(board.get("current_task")),
        "shows_agent_roster": board.get("agent_roster_summary", {}).get("agent_count", 0) >= 12,
        "shows_taskpack_state": bool(board.get("latest_taskpack")),
        "shows_lifecycle": bool(board.get("lifecycle_state")),
        "shows_safety": bool(board.get("safety_state")),
        "shows_dirty_state": bool(board.get("dirty_state")),
        "shows_git_closure": bool(board.get("git_closure")),
        "shows_next_action": bool(board.get("next_recommended_action")),
    }


def next_action(repo_root: Path) -> dict[str, Any]:
    board = build_daily_ops_board(repo_root)
    return choose_next_action(board)


def task_flow(repo_root: Path) -> dict[str, Any]:
    board = build_daily_ops_board(repo_root)
    return {
        "status": "PASS_WITH_WARNINGS",
        "workflow": [
            {
                "index": index,
                "step": step,
                "mode": "GATED" if step in {"review promotion", "close task"} else "READ_OR_DRY_RUN",
            }
            for index, step in enumerate(WORKFLOW_STEPS, 1)
        ],
        "next_action": board.get("next_recommended_action"),
        "real_execution_required": False,
    }


def smoke(repo_root: Path) -> dict[str, Any]:
    result = daily_ops(repo_root)
    board = result.get("board", {})
    checks = {
        "current_task": bool(board.get("current_task")),
        "agents": board.get("agent_roster_summary", {}).get("agent_count", 0) >= 12,
        "taskpack": bool(board.get("latest_taskpack")),
        "lifecycle": bool(board.get("lifecycle_state")),
        "safety": bool(board.get("safety_state")),
        "dirty": bool(board.get("dirty_state")),
        "git_closure": bool(board.get("git_closure")),
        "next_action": bool(board.get("next_recommended_action")),
    }
    return {
        "status": "PASS_WITH_WARNINGS" if all(checks.values()) else "BLOCKED",
        "checks": checks,
        "board_available": True,
        "workflow_steps": WORKFLOW_STEPS,
        "real_execution_enabled": False,
        "live_registration_auto_run": False,
    }
