from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

IDE_ROOT = Path(__file__).resolve().parents[1]
for module_dir in (IDE_ROOT / "BRIDGES", IDE_ROOT / "EXTENSIONS", IDE_ROOT / "WORKSPACE"):
    module_path = str(module_dir)
    if module_path not in sys.path:
        sys.path.insert(0, module_path)

from shell_receipts import build_receipt
from shell_state import RepositoryState


RISK = {
    "dry-run-tool": "LOW_DRY_RUN",
}


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
    dry_run = command == "dry-run-tool"

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
