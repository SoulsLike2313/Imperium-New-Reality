from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
COMMON_ROOT = HERE.parents[3] / "COMMON_AGENT_CLI"
if str(COMMON_ROOT) not in sys.path:
    sys.path.insert(0, str(COMMON_ROOT))

from base_half_cli import OrganConfig, run_cli

CONFIG = OrganConfig(
    organ_name="MECHANICUS_AGENT",
    organ_slug="mechanicus",
    root=HERE.parents[1],
    identity_summary="Tools, scripts, validators, registry intelligence, and premium Textual operator-console machinery.",
    domain_commands={
        "tool-list": "List local Mechanicus toolchain artifacts from TOOLS.",
        "validator-check": "Validate Identity Half JSON payload integrity.",
        "capability-map": "Show base and domain capability map for this organ.",
        "script-receipt-check": "Report receipt coverage for script-oriented runs.",
    },
    domain_aliases={
        "tool_list": "tool-list",
        "validator_check": "validator-check",
        "capability_map": "capability-map",
    },
)


if __name__ == "__main__":
    raise SystemExit(run_cli(CONFIG, sys.argv[1:]))
