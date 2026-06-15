from __future__ import annotations

from typing import Any

PANEL_ID = "extensions"


def render(state: Any) -> dict:
    return {"status": "ROUTED_THROUGH_EXTENSION_LOADER"}
