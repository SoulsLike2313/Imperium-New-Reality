from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class GovernedCandidateBridge:
    """Mechanicus facade for a candidate IDE component.

    All invocation attempts are receipts. Tool execution remains dry-run only.
    """

    def __init__(self, repo_root: Path, component: str) -> None:
        self.repo_root = repo_root.resolve()
        self.component = component.lower()
        bridge_dir = self.repo_root / "ORGANS" / "IMPERIAL_IDE" / "BRIDGES"
        import sys

        if str(bridge_dir) not in sys.path:
            sys.path.insert(0, str(bridge_dir))
        from mechanicus_shell_bridge import MechanicusShellBridge

        self.bridge = MechanicusShellBridge(self.repo_root)

    @property
    def receipt_dir(self) -> Path:
        component_root = self.repo_root / "ORGANS" / "IMPERIAL_IDE" / self.component.upper()
        if self.component == "workbench":
            return component_root / "SERVITORS" / "runtime" / "mechanicus_receipts"
        return component_root / "runtime" / "mechanicus_receipts"

    def _write(self, receipt: dict[str, Any]) -> dict[str, Any]:
        self.receipt_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        path = self.receipt_dir / f"{self.component}_{stamp}_{uuid4().hex[:8]}.json"
        receipt["receipt_path"] = path.relative_to(self.repo_root).as_posix()
        path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return receipt

    def snapshot(self) -> dict[str, Any]:
        doctor = self.bridge.doctor()
        return self._write({
            "receipt_type": "mechanicus_candidate_bridge_receipt",
            "timestamp_utc": utc_now(),
            "component": self.component,
            "operation": "snapshot",
            "status": doctor["status"],
            "tool_registry_loaded": doctor["tool_registry_loaded"],
            "capability_registry_loaded": doctor["capability_registry_loaded"],
            "command_policy_loaded": doctor["command_policy_loaded"],
            "dry_run": True,
            "executed": False,
            "real_execution_blocked": True,
            "unsafe_shell_available": False,
        })

    def dry_run_tool(self, tool_id: str) -> dict[str, Any]:
        result = self.bridge.dry_run_tool(tool_id)
        result.update({
            "receipt_type": "mechanicus_candidate_bridge_receipt",
            "component": self.component,
            "operation": "dry_run_tool",
            "real_execution_blocked": True,
            "unsafe_shell_available": False,
        })
        return self._write(result)

    def request_real_execution(self, tool_id: str) -> dict[str, Any]:
        return self._write({
            "receipt_type": "mechanicus_candidate_bridge_receipt",
            "timestamp_utc": utc_now(),
            "component": self.component,
            "operation": "request_real_execution",
            "requested_tool_id": tool_id,
            "status": "BLOCKED",
            "reason": "future_owner_allowlist_gate_required",
            "dry_run": False,
            "executed": False,
            "real_execution_blocked": True,
            "unsafe_shell_available": False,
        })
