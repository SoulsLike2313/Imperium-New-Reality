from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from lifecycle_tracker import smoke as lifecycle_smoke
from dirty_classifier import classify_dirty
from handoff_card_viewer import view_handoff_card
from json_viewer import view_json_path, view_payload
from launch_card_viewer import view_launch_card
from live_registration_promoter import promotion_state
from path_actions import actions_for_path
from receipts_browser import list_receipts
from reports_browser import list_reports
from safety_center import safety_summary
from station_state import StationState, find_repo_root
from summary_renderer import summarize_payload
from taskpack_manager import inspect_taskpack, list_taskpacks, validate_taskpack as validate_generated_taskpack
from station_workflow import StationWorkflow

DEFAULT_TITLE = "Station operator sample task"
DEFAULT_GOAL = "Build and validate an Astronomicon-compatible taskpack inside Imperial IDE"


def _intent_text(args: list[str]) -> tuple[str, str, str]:
    template = "integration"
    words = list(args)
    if words and words[0].startswith("template="):
        template = words.pop(0).split("=", 1)[1] or template
    title = " ".join(words).strip() or DEFAULT_TITLE
    return title, DEFAULT_GOAL if title == DEFAULT_TITLE else title, template


def route(command: str, args: list[str] | None = None, repo_root: Path | None = None) -> dict[str, Any]:
    args = list(args or [])
    repo = (repo_root or find_repo_root()).resolve()
    state = StationState(repo)
    workflow = StationWorkflow(repo)

    if command in {"station", "dashboard"}:
        return {"status": "PASS_WITH_WARNINGS", "surface": "OPERATIONAL_STATION", "snapshot": state.snapshot()}
    if command == "station-tui":
        return {
            "status": "PASS_WITH_WARNINGS",
            "surface": "WORKBENCH_TUI",
            "launch_command": "python ORGANS/IMPERIAL_IDE/WORKBENCH/TUI/imperial_tui.py",
            "executed": False,
        }
    if command == "station-gui":
        return {
            "status": "PASS_WITH_WARNINGS",
            "surface": "WORKBENCH_GUI",
            "launch_command": "python ORGANS/IMPERIAL_IDE/WORKBENCH/GUI/imperial_gui_workbench.py",
            "executed": False,
            "manual_windows_interaction_required": True,
        }
    if command == "station-smoke":
        result = workflow.smoke()
        result["lifecycle_tracker_smoke"] = lifecycle_smoke()
        return result
    if command == "station-ux-smoke":
        from station_ux_reports import build_task_receipts
        return build_task_receipts(repo)
    if command == "show-summary":
        payload = state.snapshot()
        return {"status": "PASS_WITH_WARNINGS", "summary": summarize_payload("Operational Station", payload)}
    if command == "show-json":
        if args:
            return view_json_path(repo, args[0])
        return view_payload("Operational Station snapshot", state.snapshot())
    if command == "path-actions":
        target = args[0] if args else "ORGANS/IMPERIAL_IDE/STATION"
        return {"status": "PASS", "path_actions": actions_for_path(repo, target)}
    if command == "agents":
        return {"status": "PASS", **state.agent_state()}
    if command == "agent-status":
        agent_id = args[0] if args else ""
        agents = state.agent_state()["agents"]
        agent = next((item for item in agents if item["agent_id"] == agent_id), None)
        return {"status": "PASS" if agent else "BLOCKED", "agent": agent, "requested_agent_id": agent_id}
    if command in {"task-console", "new-task"}:
        title, goal, template = _intent_text(args)
        _, preview = workflow.create_intent(title, goal, template)
        preview["templates"] = workflow.templates()["templates"]
        return preview
    if command == "build-taskpack":
        title, goal, template = _intent_text(args)
        return workflow.build_taskpack(title, goal, template)
    if command in {"taskpack-manager", "taskpacks", "taskpack-list"}:
        return list_taskpacks(repo)
    if command == "taskpack-inspect":
        return inspect_taskpack(repo, args[0] if args else "")
    if command == "taskpack-validate":
        return validate_generated_taskpack(repo, args[0] if args else "")
    if command in {"taskpack-open", "taskpack-copy-path"}:
        inspected = inspect_taskpack(repo, args[0] if args else "")
        if inspected.get("status") == "BLOCKED":
            return inspected
        target_key = "taskpack_path" if command == "taskpack-open" else "taskpack_zip_path"
        path_action = actions_for_path(repo, inspected[target_key])
        command_key = "open_path_command" if command == "taskpack-open" else "copy_path_command"
        return {
            "status": "PASS_WITH_WARNINGS",
            "taskpack_id": inspected["taskpack_id"],
            "action": command,
            "target_path": path_action["path"],
            "copy_ready_command": path_action[command_key],
            "path_actions": path_action,
            "executed": False,
        }
    if command == "validate-taskpack":
        if args and not args[0].startswith("TASK-"):
            return workflow.validate_taskpack(args[0])
        if args:
            return validate_generated_taskpack(repo, args[0])
        built = workflow.build_taskpack(DEFAULT_TITLE, DEFAULT_GOAL, "integration")
        return workflow.validate_taskpack(built["extracted_path"])
    if command == "register-taskpack":
        live = bool(args and args[0].lower() == "live")
        title_args = args[1:] if live else args
        title, goal, template = _intent_text(title_args)
        return workflow.register_taskpack(title, goal, template, live=live)
    if command == "launch-card":
        return view_launch_card(repo, args[0] if args else "")
    if command == "handoff-card":
        return view_handoff_card(repo, args[0] if args else "")
    if command == "lifecycle":
        title, goal, template = _intent_text(args)
        return workflow.lifecycle(title, goal, template)
    if command == "reports-latest":
        return list_reports(repo)
    if command == "receipts-latest":
        return list_receipts(repo)
    if command == "dirty-classifier":
        return classify_dirty(repo)
    if command == "safety":
        return safety_summary(repo)
    if command == "live-registration-promote":
        token = args[0] if args and args[0] == "CONFIRM_LIVE_REGISTRATION" else ""
        taskpack_id = args[1] if token and len(args) > 1 else (args[0] if args and not token else "")
        return promotion_state(repo, taskpack_id, token)
    if command == "git-closure":
        git_state = state.git_state()
        git_state["dirty_classification"] = classify_dirty(repo)
        git_state["classified_dirty_table"] = git_state["dirty_classification"].get("classified_items", [])
        git_state["push_allowed_state"] = git_state["dirty_classification"].get("push_allowed_state")
        git_state["recommended_action"] = git_state["dirty_classification"].get("recommended_action")
        return {"status": "PASS_WITH_WARNINGS", **git_state}
    return {"status": "BLOCKED", "reason": "unknown_station_command", "command": command}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Imperial IDE operational station router")
    parser.add_argument("command")
    parser.add_argument("command_args", nargs="*")
    parser.add_argument("--compact", action="store_true")
    parsed = parser.parse_args(argv)
    result = route(parsed.command, parsed.command_args)
    print(json.dumps(result, ensure_ascii=False, indent=None if parsed.compact else 2))
    return 2 if result.get("status") == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
