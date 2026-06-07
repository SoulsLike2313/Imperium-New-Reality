from __future__ import annotations

from typing import Any

PANEL_ID = "validation"


def render(state: Any) -> dict:
    return state.validate_json()
