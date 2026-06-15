from __future__ import annotations

from typing import Any

PANEL_ID = "overview"


def render(state: Any) -> dict:
    return state.overview()
