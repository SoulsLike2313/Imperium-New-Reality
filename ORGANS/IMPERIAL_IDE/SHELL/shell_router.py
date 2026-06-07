from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

IDE_ROOT = Path(__file__).resolve().parents[1]
for module_dir in (
    IDE_ROOT / "BRIDGES",
    IDE_ROOT / "EXTENSIONS",
    IDE_ROOT / "WORKSPACE",
    IDE_ROOT / "STATION",
):
    module_path = str(module_dir)
    if module_path not in sys.path:
        sys.path.insert(0, module_path)

from shell_receipts import build_receipt
from shell_state import RepositoryState


RISK = {
    "dry-run-tool": "LOW_DRY_RUN",
    "workbench-smoke": "LOW_LOCAL_SMOKE",
    "warp-smoke": "LOW_LOCAL_SMOKE",
    "metaos-smoke": "LOW_LOCAL_SMOKE",
    "metaos-bundle-gate": "LOW_LOCAL_SMOKE",
    "ops-smoke": "LOW_LOCAL_SMOKE",
    "station-smoke": "LOW_LOCAL_SMOKE",
    "station-ux-smoke": "LOW_LOCAL_SMOKE",
    "lifecycle-smoke": "LOW_LOCAL_SMOKE",
    "warp-open": "LOW_DRY_RUN",
    "warp-gate": "LOW_DRY_RUN",
    "metaos-route": "LOW_DRY_RUN",
    "metaos-servitor": "LOW_DRY_RUN",
    "metaos-chronicle": "LOW_DRY_RUN",
    "classify-task": "LOW_DRY_RUN",
    "build-taskpack": "LOW_DRY_RUN",
    "register-taskpack": "LOW_DRY_RUN",
    "launch-card": "LOW_DRY_RUN",
    "lifecycle": "LOW_DRY_RUN",
    "git-closure": "LOW_DRY_RUN",
    "taskpack-manager": "LOW_READ_ONLY",
    "taskpack-list": "LOW_READ_ONLY",
    "taskpack-inspect": "LOW_READ_ONLY",
    "show-json": "LOW_READ_ONLY",
    "show-summary": "LOW_READ_ONLY",
    "path-actions": "LOW_READ_ONLY",
    "dirty-classifier": "LOW_READ_ONLY",
    "live-registration-promote": "HIGH_LOCAL_GATED",
    "station": "LOW_READ_ONLY",
    "station-tui": "LOW_READ_ONLY",
    "station-gui": "LOW_READ_ONLY",
    "agents": "LOW_READ_ONLY",
    "agent-status": "LOW_READ_ONLY",
    "new-task": "LOW_DRY_RUN",
    "validate-taskpack": "LOW_DRY_RUN",
    "handoff-card": "LOW_DRY_RUN",
    "reports-latest": "LOW_READ_ONLY",
    "receipts-latest": "LOW_READ_ONLY",
    "safety": "LOW_READ_ONLY",
}

OPS_COMMANDS = {
    "ops", "ops-smoke", "classify-task", "lifecycle-smoke", "task-templates",
}

STATION_COMMANDS = {
    "station", "station-tui", "station-gui", "station-smoke", "agents",
    "agent-status", "task-console", "new-task", "build-taskpack",
    "validate-taskpack", "register-taskpack", "launch-card", "handoff-card",
    "lifecycle", "reports-latest", "receipts-latest", "safety", "git-closure",
    "station-ux-smoke", "taskpack-manager", "taskpack-list", "taskpack-inspect",
    "show-json", "show-summary", "path-actions", "dirty-classifier",
    "live-registration-promote",
}

INTEGRATION_COMMANDS = {
    "workbench", "workbench-tui", "workbench-gui", "workbench-smoke",
    "workbench-status", "warp", "warp-open", "warp-list", "warp-status",
    "warp-gate", "warp-smoke", "metaos", "metaos-smoke", "metaos-route",
    "metaos-servitor", "metaos-bundle-gate", "metaos-chronicle",
} | OPS_COMMANDS


def _status_from(data: Any) -> str:
    if isinstance(data, dict):
        for key in ("status", "verdict", "validation_status"):
            value = data.get(key)
            if isinstance(value, str):
                return value
    return "PASS_WITH_WARNINGS"


def _palette(state: RepositoryState) -> dict[str, Any]:
    return state.read_json("ORGANS/IMPERIAL_IDE/SHELL/command_palette.json")


def route(command: str, args: list[str] | None = None) -> dict[str, Any]:
    args = list(args or [])
    state = RepositoryState()
    bridge = None
    data_sources: list[str] = []
    tools_invoked: list[str] = []
    live_registration = command == "register-taskpack" and bool(args) and args[0].lower() == "live"
    promotion_live = command == "live-registration-promote" and bool(args) and args[0] == "CONFIRM_LIVE_REGISTRATION"
    dry_run = not live_registration and not promotion_live and (command == "dry-run-tool" or command in {
        "warp-open", "warp-gate", "metaos-route", "metaos-servitor", "metaos-chronicle",
        "classify-task", "build-taskpack", "register-taskpack", "launch-card",
        "validate-taskpack", "handoff-card", "lifecycle", "git-closure", "task-console",
        "new-task", "dirty-classifier", "live-registration-promote",
    })

    if command in {"tools", "capabilities", "policy", "dry-run-tool", "doctor", "validate"}:
        from mechanicus_shell_bridge import MechanicusShellBridge
        bridge = MechanicusShellBridge(state.repo_root)

    if command == "doctor":
        from extension_loader import validate_extensions
        from workspace_state_manager import validate_workspace
        data = {
            "shell": {
                "repo_root": state.repo_root.as_posix(),
                "required_files": state.validate_json(),
                "governance": state.governance(),
                "current_task": state.current_task(),
            },
            "mechanicus": bridge.doctor(),
            "extensions": validate_extensions(state.repo_root),
            "workspace": validate_workspace(state.repo_root),
        }
        status = "PASS_WITH_WARNINGS" if all(
            item.get("status") in {"PASS", "PASS_WITH_WARNINGS"}
            for item in (data["shell"]["required_files"], data["mechanicus"], data["extensions"], data["workspace"])
        ) else "BLOCKED"
        data["status"] = status
        data_sources = ["governance", "task_registry", "mechanicus_registry", "extensions", "workspace"]
    elif command == "status":
        data = {"overview": state.overview(), "git": state.git_status(), "status": "PASS_WITH_WARNINGS"}
        data_sources = ["git", "governance", "current_task"]
    elif command == "dashboard":
        data = {
            "status": "PASS_WITH_WARNINGS",
            "overview": state.overview(),
            "governance": state.governance(),
            "current_task": state.current_task(),
            "tasks": state.registered_tasks(limit=10),
            "reports": state.reports(limit=10),
            "receipts": state.receipts(limit=10),
            "tools": bridge.list_tools() if bridge else {},
            "capabilities": bridge.list_capabilities() if bridge else {},
        }
        if bridge is None:
            from mechanicus_shell_bridge import MechanicusShellBridge
            bridge = MechanicusShellBridge(state.repo_root)
            data["tools"] = bridge.list_tools()
            data["capabilities"] = bridge.list_capabilities()
        data_sources = ["panel_registry", "governance", "astronomicon", "reports", "mechanicus"]
    elif command == "tasks":
        data = state.registered_tasks()
        data["status"] = "PASS" if data.get("found") else "BLOCKED"
        data_sources = ["ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED"]
    elif command == "current-task":
        data = state.current_task()
        data["status"] = "PASS" if data.get("found") else "BLOCKED"
        data_sources = ["ORGANS/ASTRONOMICON/TASK_REGISTRY/current_expected_task.json"]
    elif command == "reports":
        data = state.reports()
        data["status"] = "PASS" if data.get("found") else "BLOCKED"
        data_sources = ["REPORTS"]
    elif command == "latest-report":
        data = state.latest_report()
        data["status"] = "PASS" if data.get("found") else "BLOCKED"
        data_sources = ["REPORTS"]
    elif command == "receipts":
        data = state.receipts()
        data["status"] = "PASS_WITH_WARNINGS" if data.get("found") else "BLOCKED"
        data_sources = ["REPORTS", "ORGANS/IMPERIAL_IDE/RECEIPTS"]
    elif command == "tools":
        data = bridge.list_tools()
        data_sources = ["ORGANS/MECHANICUS/REGISTRY/tool_registry.json"]
    elif command == "capabilities":
        data = bridge.list_capabilities()
        data_sources = ["ORGANS/MECHANICUS/REGISTRY/capability_registry.json"]
    elif command == "policy":
        data = bridge.policy()
        data_sources = ["ORGANS/MECHANICUS/REGISTRY/command_policy.json"]
    elif command == "extensions":
        from extension_loader import validate_extensions
        data = validate_extensions(state.repo_root)
        data_sources = ["ORGANS/IMPERIAL_IDE/EXTENSIONS"]
    elif command == "workspace":
        from workspace_state_manager import validate_workspace
        data = validate_workspace(state.repo_root)
        data_sources = ["ORGANS/IMPERIAL_IDE/WORKSPACE/workspace_state.json"]
    elif command == "validate":
        data = {
            "status": "PASS",
            "shell_json": state.validate_json(),
            "mechanicus": bridge.validate_json(),
        }
        if data["shell_json"]["status"] != "PASS" or data["mechanicus"]["status"] != "PASS":
            data["status"] = "BLOCKED"
        data_sources = state.shell_json_paths()
        tools_invoked = ["MECHANICUS_VALIDATE"]
    elif command == "dry-run-tool":
        target = args[0] if args else ""
        data = bridge.dry_run_tool(target)
        data_sources = [
            "ORGANS/MECHANICUS/REGISTRY/tool_registry.json",
            "ORGANS/MECHANICUS/REGISTRY/command_policy.json",
        ]
        tools_invoked = [target] if target else []
    elif command in STATION_COMMANDS:
        from station_router import route as route_station
        data = route_station(command, args, state.repo_root)
        data_sources = [
            "ORGANS/IMPERIAL_IDE/STATION",
            "ORGANS/IMPERIAL_IDE/AGENTS/agent_registry.json",
        ]
        if "smoke" in command:
            tools_invoked = ["IMPERIAL_IDE_OPERATIONAL_STATION"]
        elif command == "register-taskpack" and live_registration:
            tools_invoked = ["ASTRONOMICON_LOCAL_REGISTRATION_GATE"]
        elif command == "live-registration-promote" and promotion_live:
            tools_invoked = ["ASTRONOMICON_LOCAL_REGISTRATION_GATE"]
    elif command in INTEGRATION_COMMANDS:
        from integration_surfaces import route_surface
        data = route_surface(state.repo_root, command, args)
        if command in OPS_COMMANDS:
            data_sources = [
                "ORGANS/IMPERIAL_IDE/OPS/INTEGRATION_STATUS.json",
                "ORGANS/IMPERIAL_IDE/OPS/ENGINE/imperium_ops",
            ]
            if "smoke" in command:
                tools_invoked = ["IMPERIAL_IDE_OPS_TASK_CONSOLE"]
        else:
            component = command.split("-", 1)[0]
            status_path = {
                "workbench": "ORGANS/IMPERIAL_IDE/WORKBENCH/INTEGRATION_STATUS.json",
                "warp": "ORGANS/IMPERIAL_IDE/WARP/INTEGRATION_STATUS.json",
                "metaos": "ORGANS/IMPERIAL_IDE/METAOS/INTEGRATION_STATUS.json",
            }.get(component)
            data_sources = [status_path] if status_path else []
            if "smoke" in command or command == "metaos-bundle-gate":
                tools_invoked = [{
                    "workbench": "MECHANICUS_WORKBENCH_BRIDGE",
                    "warp": "MECHANICUS_WARP_BRIDGE",
                    "metaos": "MECHANICUS_METAOS_BRIDGE",
                }[component]]
    elif command == "help":
        data = _palette(state)
        data["status"] = "PASS"
        data_sources = ["ORGANS/IMPERIAL_IDE/SHELL/command_palette.json"]
    else:
        data = {"status": "BLOCKED", "reason": "unknown_command", "command": command}

    status = _status_from(data)
    receipt = build_receipt(
        command=command,
        args=args,
        repo_root=state.repo_root,
        status=status,
        risk_class=RISK.get(command, "LOW_READ_ONLY"),
        data_sources=data_sources,
        tools_invoked=tools_invoked,
        dry_run=dry_run,
        output_summary=f"{command}:{status}",
    )
    return {"data": data, "receipt": receipt}
