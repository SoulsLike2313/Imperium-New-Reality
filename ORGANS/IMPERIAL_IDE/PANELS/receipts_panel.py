from __future__ import annotations

from typing import Any

PANEL_ID = "receipts"


def render(state: Any) -> dict:
    return state.receipts()
