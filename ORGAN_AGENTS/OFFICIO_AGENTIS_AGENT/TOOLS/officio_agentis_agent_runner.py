from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
COMMON_ROOT = HERE.parents[3] / "COMMON_AGENT_CLI"
if str(COMMON_ROOT) not in sys.path:
    sys.path.insert(0, str(COMMON_ROOT))

from base_half_cli import OrganConfig, run_cli

CONFIG = OrganConfig(
    organ_name="OFFICIO_AGENTIS_AGENT",
    organ_slug="officio_agentis",
    root=HERE.parents[1],
    identity_summary="Roles, modes, permissions, stop conditions, and response contracts.",
    domain_commands={},
)


if __name__ == "__main__":
    raise SystemExit(run_cli(CONFIG, sys.argv[1:]))
