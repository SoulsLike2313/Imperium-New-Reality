from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
COMMON_ROOT = HERE.parents[3] / "COMMON_AGENT_CLI"
if str(COMMON_ROOT) not in sys.path:
    sys.path.insert(0, str(COMMON_ROOT))

from base_half_cli import OrganConfig, run_cli

CONFIG = OrganConfig(
    organ_name="ASTRONOMICON_AGENT",
    organ_slug="astronomicon",
    root=HERE.parents[1],
    identity_summary="Task intake, decomposition, stage maps, and route readiness.",
    domain_commands={
        "task-route": "Outline canonical intake-to-delivery route stages.",
        "stage-map-outline": "Emit a compact stage map for current task flow.",
        "ready-for-agent-check": "Check readiness of identity artifacts for handoff.",
        "route-report": "Produce route summary with backend path references.",
    },
    domain_aliases={
        "task_route": "task-route",
        "stage_map_outline": "stage-map-outline",
    },
)


if __name__ == "__main__":
    raise SystemExit(run_cli(CONFIG, sys.argv[1:]))
