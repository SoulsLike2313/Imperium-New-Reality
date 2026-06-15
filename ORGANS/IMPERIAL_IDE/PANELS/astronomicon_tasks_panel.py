from __future__ import annotations

from typing import Any

PANEL_ID = "astronomicon_tasks"


def render(state: Any) -> dict:
    return state.registered_tasks()
