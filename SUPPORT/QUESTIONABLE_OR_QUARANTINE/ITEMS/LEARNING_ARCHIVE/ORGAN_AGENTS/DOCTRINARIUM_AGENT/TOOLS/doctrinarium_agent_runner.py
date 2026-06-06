from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
COMMON_ROOT = HERE.parents[3] / "COMMON_AGENT_CLI"
if str(COMMON_ROOT) not in sys.path:
    sys.path.insert(0, str(COMMON_ROOT))

from base_half_cli import OrganConfig, run_cli

CONFIG = OrganConfig(
    organ_name="DOCTRINARIUM_AGENT",
    organ_slug="doctrinarium",
    root=HERE.parents[1],
    identity_summary="Laws, policy gates, compliance, and conflict resolution.",
    domain_commands={
        "law-list": "List gate-law inventory from Doctrinarium registry.",
        "doctrine-check": "Check baseline doctrine files are present and accessible.",
        "violation-report": "Report forbidden-path or scope violations from git drift.",
        "gate-before-work": "Emit gate-before-work truth check requirements.",
    },
    domain_aliases={
        "law_list": "law-list",
        "doctrine_check": "doctrine-check",
    },
)


if __name__ == "__main__":
    raise SystemExit(run_cli(CONFIG, sys.argv[1:]))
