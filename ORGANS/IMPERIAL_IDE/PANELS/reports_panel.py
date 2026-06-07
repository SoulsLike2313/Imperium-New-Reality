from __future__ import annotations

from typing import Any

PANEL_ID = "reports"


def render(state: Any) -> dict:
    return state.reports()
