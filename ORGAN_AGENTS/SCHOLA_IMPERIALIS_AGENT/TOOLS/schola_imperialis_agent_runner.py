from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
COMMON_ROOT = HERE.parents[3] / "COMMON_AGENT_CLI"
if str(COMMON_ROOT) not in sys.path:
    sys.path.insert(0, str(COMMON_ROOT))

from base_half_cli import OrganConfig, run_cli

CONFIG = OrganConfig(
    organ_name="SCHOLA_IMPERIALIS_AGENT",
    organ_slug="schola_imperialis",
    root=HERE.parents[1],
    identity_summary="Lessons, training packs, examples, and skill growth loops.",
    domain_commands={
        "lesson-register": "List lesson/example anchors for current Schola scope.",
        "training-pack-outline": "Outline required training-pack components.",
        "skill-map": "Map currently visible skills/resources for training flow.",
        "example-check": "Verify domain example files are present and readable.",
    },
    domain_aliases={
        "lesson_register": "lesson-register",
        "training_pack_outline": "training-pack-outline",
    },
)


if __name__ == "__main__":
    raise SystemExit(run_cli(CONFIG, sys.argv[1:]))
