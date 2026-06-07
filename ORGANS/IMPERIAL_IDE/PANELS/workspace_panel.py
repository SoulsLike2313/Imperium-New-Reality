from __future__ import annotations

from typing import Any

PANEL_ID = "workspace"


def render(state: Any) -> dict:
    return {"status": "ROUTED_THROUGH_WORKSPACE_MANAGER"}
