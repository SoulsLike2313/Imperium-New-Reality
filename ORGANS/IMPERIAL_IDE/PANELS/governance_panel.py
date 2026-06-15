from __future__ import annotations

from typing import Any

PANEL_ID = "governance"


def render(state: Any) -> dict:
    return state.governance()
