from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
COMMON_ROOT = HERE.parents[3] / "COMMON_AGENT_CLI"
if str(COMMON_ROOT) not in sys.path:
    sys.path.insert(0, str(COMMON_ROOT))

from base_half_cli import OrganConfig, run_cli

CONFIG = OrganConfig(
    organ_name="INQUISITION_AGENT",
    organ_slug="inquisition",
    root=HERE.parents[1],
    identity_summary="Audit, anti-fake-green, scope integrity, and evidence truth enforcement.",
    domain_commands={
        "fake-green-check": "Detect unsupported PASS claims and missing evidence links.",
        "scope-drift-check": "Surface changed paths and highlight potential scope drift.",
        "hygiene-scan": "Scan Identity Half required files and report missing artifacts.",
        "audit-claims": "Summarize claim/evidence anchors for current organ status.",
    },
    domain_aliases={
        "fake_green_check": "fake-green-check",
        "scope_drift_check": "scope-drift-check",
    },
)


if __name__ == "__main__":
    raise SystemExit(run_cli(CONFIG, sys.argv[1:]))
