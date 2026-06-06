from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
NEWGEN_ROOT = HERE.parents[2]
SHELL_ROOT = NEWGEN_ROOT / "ORGAN_AGENT_COMMON" / "SHELL"
if str(SHELL_ROOT) not in sys.path:
    sys.path.insert(0, str(SHELL_ROOT))

from organ_shell_v0_1 import run_organ_shell

TASK_ID_DEFAULT = "TASK-20260524-NEWGEN-IMPORTANT-SIX-ORGAN-SHELL-V1-PC-V0_1"


def _load_theme(organ_id: str) -> dict[str, str]:
    registry_path = SHELL_ROOT / "organ_shell_theme_registry_v0_1.json"
    fallback = {"identity": organ_id, "accent": "cyan", "header": "bold cyan", "panel": "cyan", "prompt": "cyan"}
    if not registry_path.exists():
        return fallback
    try:
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception:
        return fallback
    themes = payload.get("themes", {})
    if not isinstance(themes, dict):
        return fallback
    theme = themes.get(organ_id)
    return theme if isinstance(theme, dict) else fallback


def build_config() -> dict[str, Any]:
    return {
        "organ_id": "OFFICIO_AGENTIS",
        "organ_slug": "officio",
        "task_id_default": TASK_ID_DEFAULT,
        "shell_version": "v1.0.0",
        "organ_root": HERE.parents[1],
        "query_script": NEWGEN_ROOT / "OFFICIO_AGENTIS" / "TOOLS" / "officio_organ_query_v0_1.py",
        "report_root": NEWGEN_ROOT / "REPORTS" / TASK_ID_DEFAULT,
        "mission_focus": "Enforce role contract, language rule, and stop-condition discipline.",
        "specific_commands": {
            "role": "Show active role contract summary",
            "language": "Show owner-facing language contract",
        },
        "theme": _load_theme("OFFICIO_AGENTIS"),
    }


def main() -> int:
    return run_organ_shell(build_config())


if __name__ == "__main__":
    raise SystemExit(main())
