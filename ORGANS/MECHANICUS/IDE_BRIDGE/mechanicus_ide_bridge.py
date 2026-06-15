from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class MechanicusIdeBridge:
    """Mechanicus-owned read-only facade for Imperial IDE consumers."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()

    def load_registry(self, relative: str) -> dict[str, Any]:
        with (self.repo_root / relative).open("r", encoding="utf-8-sig") as handle:
            return json.load(handle)

    def snapshot(self) -> dict[str, Any]:
        tools = self.load_registry("ORGANS/MECHANICUS/REGISTRY/tool_registry.json")
        capabilities = self.load_registry("ORGANS/MECHANICUS/REGISTRY/capability_registry.json")
        policy = self.load_registry("ORGANS/MECHANICUS/REGISTRY/command_policy.json")
        return {
            "status": "PASS_WITH_WARNINGS",
            "tool_count": len(tools.get("tools", [])),
            "capability_count": len(capabilities.get("capabilities", [])),
            "dry_run_required": policy.get("dry_run_required_by_default"),
            "unsafe_shell_available": policy.get("arbitrary_shell_execution_allowed"),
            "real_execution_blocked": True,
        }
