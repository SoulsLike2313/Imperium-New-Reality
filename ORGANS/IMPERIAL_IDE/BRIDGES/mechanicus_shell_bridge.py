from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TOOL_REGISTRY = "ORGANS/MECHANICUS/REGISTRY/tool_registry.json"
CAPABILITY_REGISTRY = "ORGANS/MECHANICUS/REGISTRY/capability_registry.json"
COMMAND_POLICY = "ORGANS/MECHANICUS/REGISTRY/command_policy.json"
ALIASES = {
    "mechanicus.cli": "MECHANICUS_CLI",
    "mechanicus.doctor": "MECHANICUS_DOCTOR",
    "mechanicus.inventory": "MECHANICUS_INVENTORY",
    "mechanicus.validate": "MECHANICUS_VALIDATE",
    "mechanicus.gateway": "MECHANICUS_COMMAND_GATEWAY",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class MechanicusShellBridge:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()

    def _load(self, relative: str) -> dict[str, Any]:
        with (self.repo_root / relative).open("r", encoding="utf-8-sig") as handle:
            return json.load(handle)

    def registries(self) -> dict[str, Any]:
        return {
            "tools": self._load(TOOL_REGISTRY),
            "capabilities": self._load(CAPABILITY_REGISTRY),
            "policy": self._load(COMMAND_POLICY),
        }

    def list_tools(self) -> dict[str, Any]:
        tools = self._load(TOOL_REGISTRY).get("tools", [])
        return {"status": "PASS", "tools": tools, "count": len(tools)}

    def list_capabilities(self) -> dict[str, Any]:
        capabilities = self._load(CAPABILITY_REGISTRY).get("capabilities", [])
        return {"status": "PASS", "capabilities": capabilities, "count": len(capabilities)}

    def policy(self) -> dict[str, Any]:
        policy = self._load(COMMAND_POLICY)
        return {
            "status": "PASS",
            "policy": policy,
            "unsafe_shell_available": bool(policy.get("arbitrary_shell_execution_allowed")),
        }

    def validate_json(self) -> dict[str, Any]:
        parsed: list[str] = []
        invalid: list[dict[str, str]] = []
        for relative in (TOOL_REGISTRY, CAPABILITY_REGISTRY, COMMAND_POLICY):
            try:
                self._load(relative)
                parsed.append(relative)
            except Exception as exc:
                invalid.append({"path": relative, "error": str(exc)})
        return {"status": "PASS" if not invalid else "BLOCKED", "parsed": parsed, "invalid": invalid}

    def doctor(self) -> dict[str, Any]:
        registries = self.registries()
        policy = registries["policy"]
        unsafe = bool(policy.get("arbitrary_shell_execution_allowed"))
        dry_run = bool(policy.get("dry_run_required_by_default"))
        status = "PASS_WITH_WARNINGS" if not unsafe and dry_run else "BLOCKED"
        return {
            "status": status,
            "tool_registry_loaded": True,
            "capability_registry_loaded": True,
            "command_policy_loaded": True,
            "tool_count": len(registries["tools"].get("tools", [])),
            "capability_count": len(registries["capabilities"].get("capabilities", [])),
            "dry_run_required_by_default": dry_run,
            "unsafe_shell_available": unsafe,
            "real_execution_blocked": True,
        }

    def dry_run_tool(self, requested_tool_id: str) -> dict[str, Any]:
        registries = self.registries()
        policy = registries["policy"]
        resolved_id = ALIASES.get(requested_tool_id, requested_tool_id)
        tools = {item.get("tool_id"): item for item in registries["tools"].get("tools", [])}
        allowlisted = set(policy.get("allowlisted_tool_ids_for_dry_run", []))
        tool = tools.get(resolved_id)
        if not requested_tool_id:
            status, reason = "BLOCKED", "tool_id_required"
        elif tool is None:
            status, reason = "BLOCKED", "tool_not_registered"
        elif resolved_id not in allowlisted:
            status, reason = "BLOCKED", "tool_not_allowlisted_for_dry_run"
        else:
            status, reason = "PASS_WITH_WARNINGS", "dry_run_only"
        return {
            "receipt_type": "imperial_ide_mechanicus_dry_run_receipt",
            "timestamp_utc": utc_now(),
            "requested_tool_id": requested_tool_id,
            "resolved_tool_id": resolved_id,
            "tool": tool,
            "status": status,
            "reason": reason,
            "dry_run": True,
            "executed": False,
            "real_execution_blocked": True,
            "unsafe_shell_available": False,
        }
