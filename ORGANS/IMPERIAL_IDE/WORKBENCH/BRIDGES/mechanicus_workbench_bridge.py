#!/usr/bin/env python3
"""Read-only Workbench facade over the active Mechanicus shell bridge."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PKG_ROOT = HERE.parent


def _repo_root() -> Path | None:
    env = os.environ.get("IMPERIUM_ROOT")
    if env:
        candidate = Path(env).resolve()
        if (candidate / "AGENTS.md").is_file() and (candidate / "ORGANS").is_dir():
            return candidate
    for candidate in (HERE, *HERE.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / "ORGANS").is_dir():
            return candidate
    return None


class MechanicusBridge:
    def __init__(self) -> None:
        self.root = _repo_root()
        self.bridge: Any | None = None
        if self.root:
            bridge_dir = self.root / "ORGANS" / "IMPERIAL_IDE" / "BRIDGES"
            sys.path.insert(0, str(bridge_dir))
            from mechanicus_shell_bridge import MechanicusShellBridge

            self.bridge = MechanicusShellBridge(self.root)

    @property
    def mode(self) -> str:
        return "LIVE_READ_ONLY" if self.bridge else "SAMPLE"

    def _sample(self, name: str) -> dict[str, Any]:
        path = PKG_ROOT / "BRIDGES" / f"sample_{name}.json"
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8-sig"))
        return {}

    def list_tools(self) -> dict[str, Any]:
        return self.bridge.list_tools() if self.bridge else self._sample("tools")

    def get_capabilities(self) -> dict[str, Any]:
        return self.bridge.list_capabilities() if self.bridge else self._sample("capabilities")

    def get_policy(self) -> dict[str, Any]:
        return self.bridge.policy() if self.bridge else self._sample("policy")

    def dry_run_tool(self, tool_id: str, task: str = "") -> dict[str, Any]:
        if self.bridge:
            receipt = self.bridge.dry_run_tool(tool_id)
            receipt["workbench_task"] = task
            return receipt
        known = {item.get("tool_id") for item in self._sample("tools").get("tools", [])}
        if tool_id not in known:
            return {
                "tool_id": tool_id,
                "status": "BLOCKED",
                "reason": "tool_not_registered",
                "executed": False,
                "real_execution_blocked": True,
            }
        return {
            "tool_id": tool_id,
            "status": "PASS_WITH_WARNINGS",
            "reason": "sample_dry_run_only",
            "executed": False,
            "real_execution_blocked": True,
        }


if __name__ == "__main__":
    bridge = MechanicusBridge()
    print(json.dumps({
        "status": "PASS_WITH_WARNINGS",
        "mode": bridge.mode,
        "root": str(bridge.root) if bridge.root else None,
        "tools": bridge.list_tools(),
        "policy": bridge.get_policy(),
        "negative_test": bridge.dry_run_tool("arbitrary.shell", "negative safety test"),
    }, ensure_ascii=False, indent=2))
