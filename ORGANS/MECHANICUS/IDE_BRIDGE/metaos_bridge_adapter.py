from __future__ import annotations

import json
from pathlib import Path

from triple_bridge_common import GovernedCandidateBridge


class MetaOSBridgeAdapter(GovernedCandidateBridge):
    def __init__(self, repo_root: Path) -> None:
        super().__init__(repo_root, "metaos")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[3]
    bridge = MetaOSBridgeAdapter(root)
    print(json.dumps({
        "snapshot": bridge.snapshot(),
        "known": bridge.dry_run_tool("MECHANICUS_INVENTORY"),
        "unknown": bridge.dry_run_tool("arbitrary.shell"),
        "real": bridge.request_real_execution("MECHANICUS_INVENTORY"),
    }, indent=2))
