from __future__ import annotations

from typing import Any

PANEL_ID = "command_policy"


def render(state: Any) -> dict:
    return {"status": "ROUTED_THROUGH_MECHANICUS_BRIDGE"}
