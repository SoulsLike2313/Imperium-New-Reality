from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, Dict, Tuple

HERE = Path(__file__).resolve()
COMMON_ROOT = HERE.parents[3] / "COMMON_AGENT_CLI"
if str(COMMON_ROOT) not in sys.path:
    sys.path.insert(0, str(COMMON_ROOT))

from textual_operator_shell import launch_textual_operator_shell

PayloadLoader = Callable[[str, bool], Dict[str, Any]]


def run_mechanicus_textual_tui_v0_4(
    *,
    organ_name: str,
    mission: str,
    payload_loader: PayloadLoader,
    screenshot_dir: str | None = None,
    shell_version: str = "v0.4",
) -> Tuple[bool, str]:
    return launch_textual_operator_shell(
        organ_name=organ_name,
        mission=mission,
        payload_loader=payload_loader,
        shell_version=shell_version,
        screenshot_dir=screenshot_dir,
    )

