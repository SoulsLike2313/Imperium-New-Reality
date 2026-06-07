from __future__ import annotations

from pathlib import Path
from typing import Any

from dirty_classifier import classify_dirty
from git_closure import plan_git_closure
from handoff_card_viewer import view_handoff_card
from launch_card_viewer import view_launch_card
from operator_next_action import choose_next_action
from safety_center import safety_summary
from station_state import StationState
from taskpack_manager import list_taskpacks


WORKFLOW_STEPS = [
    "start day",
    "inspect system",
    "create task",
    "build taskpack",
    "validate",
    "dry-run register",
    "review promotion",
    "copy launch or handoff card",
    "watch lifecycle",
    "inspect reports and receipts",
    "close task",
    "prepare next task",
]


def lifecycle_summary(task_id: str) -> dict[str, Any]:
    stages = [
        {"stage": "INTENT_CAPTURED", "state": "VISIBLE"},
        {"stage": "TASKPACK_VALIDATED", "state": "VISIBLE"},
        {"stage": "DRY_RUN_REGISTERED", "state": "VISIBLE"},
        {"stage": "LIVE_REGISTERED", "state": "GATED"},
        {"stage": "HANDOFF_READY", "state": "VISIBLE"},
        {"stage": "EXECUTION_STARTED", "state": "GATED"},
        {"stage": "GIT_CLOSURE_CHECKED", "state": "VISIBLE"},
    ]
    return {
        "status": "PASS_WITH_WARNINGS",
        "task_id": task_id,
        "overall_state": "DRY_RUN",
        "stages": stages,
        "real_execution_gated": True,
        "live_registration_gated": True,
    }


def build_daily_ops_board(repo_root: Path) -> dict[str, Any]:
    repo = repo_root.resolve()
    station = StationState(repo)
    snapshot = station.snapshot()
    taskpacks = list_taskpacks(repo)
    latest_taskpack = (taskpacks.get("items") or [{}])[0]
    current_task = snapshot.get("task", {}).get("current", {})
    task_id = current_task.get("task_id", "")
    board = {
        "status": "PASS_WITH_WARNINGS",
        "system_truth": {
            "repo_root": repo.as_posix(),
            "branch": snapshot.get("git_closure", {}).get("branch"),
            "head": snapshot.get("git_closure", {}).get("head"),
            "origin_master": snapshot.get("git_closure", {}).get("origin_master"),
            "head_equals_origin_master": snapshot.get("git_closure", {}).get("head_equals_origin_master"),
        },
        "current_task": current_task,
        "current_expected_task": current_task,
        "agent_roster_summary": {
            "agent_count": snapshot.get("agents", {}).get("agent_count", 0),
            "real_execution_enabled": False,
            "servitor_prime_mode": "EXTERNAL_HANDOFF_ONLY",
        },
        "latest_taskpack": latest_taskpack,
        "latest_launch_card": view_launch_card(repo, latest_taskpack.get("taskpack_id", "")),
        "latest_handoff_card": view_handoff_card(repo, latest_taskpack.get("taskpack_id", "")),
        "lifecycle_state": lifecycle_summary(task_id),
        "safety_state": safety_summary(repo),
        "dirty_state": classify_dirty(repo),
        "git_closure": plan_git_closure(repo),
        "workflow": WORKFLOW_STEPS,
    }
    board["next_recommended_action"] = choose_next_action(board)
    return board
