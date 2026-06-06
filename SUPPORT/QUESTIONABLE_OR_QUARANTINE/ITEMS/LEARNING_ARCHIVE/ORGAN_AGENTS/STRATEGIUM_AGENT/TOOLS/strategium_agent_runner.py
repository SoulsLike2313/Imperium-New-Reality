from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
COMMON_ROOT = HERE.parents[3] / "COMMON_AGENT_CLI"
if str(COMMON_ROOT) not in sys.path:
    sys.path.insert(0, str(COMMON_ROOT))

from base_half_cli import OrganConfig, run_cli

CONFIG = OrganConfig(
    organ_name="STRATEGIUM_AGENT",
    organ_slug="strategium",
    root=HERE.parents[1],
    identity_summary="Strategy, priorities, campaigns, and risk-aware planning.",
    domain_commands={
        "priority-matrix": "Emit a compact priority matrix for execution focus.",
        "campaign-plan-outline": "Outline phased campaign sequence for task delivery.",
        "resource-estimate": "Estimate resource footprint from current organ state.",
        "freeze-list": "List frozen/forbidden paths and no-touch boundaries.",
    },
    domain_aliases={
        "priority_matrix": "priority-matrix",
        "campaign_plan_outline": "campaign-plan-outline",
    },
)


if __name__ == "__main__":
    raise SystemExit(run_cli(CONFIG, sys.argv[1:]))
