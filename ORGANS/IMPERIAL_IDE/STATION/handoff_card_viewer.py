from __future__ import annotations

from pathlib import Path
from typing import Any

from launch_card_viewer import view_launch_card


def view_handoff_card(repo_root: Path, taskpack_id: str = "") -> dict[str, Any]:
    launch = view_launch_card(repo_root, taskpack_id)
    if launch.get("status") == "BLOCKED":
        return launch
    return {
        "status": "PASS_WITH_WARNINGS",
        "viewer": "HANDOFF_CARD",
        "task_id": launch["task_id"],
        "handoff_target": "SERVITOR_PRIME",
        "handoff_mode": "COPY_READY_EXTERNAL_HANDOFF",
        "dry_run_status": launch["admission_state"],
        "live_status": launch["live_state"],
        "candidate_status": launch["canon_state"],
        "execution_started": False,
        "execution_done": False,
        "copy_ready_servitor_prime_block": (
            f"SERVITOR PRIME HANDOFF: {launch['task_id']}. "
            "Read taskpack, acknowledge scope, keep forbidden actions blocked, "
            "and wait for explicit owner execution gate."
        ),
        "launch_card": launch,
        "raw_json_available": True,
    }
