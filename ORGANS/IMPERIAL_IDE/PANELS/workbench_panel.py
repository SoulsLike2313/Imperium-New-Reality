from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "SHELL"))
from integration_surfaces import load_status

PANEL_ID = "workbench"


def render(state):
    return load_status(state.repo_root, "workbench")
