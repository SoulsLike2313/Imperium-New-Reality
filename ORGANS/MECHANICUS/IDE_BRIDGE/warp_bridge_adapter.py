from __future__ import annotations

import json
from pathlib import Path

from triple_bridge_common import GovernedCandidateBridge


class WarpBridgeAdapter(GovernedCandidateBridge):
    def __init__(self, repo_root: Path) -> None:
        super().__init__(repo_root, "warp")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[3]
    bridge = WarpBridgeAdapter(root)
    print(json.dumps({
        "snapshot": bridge.snapshot(),
        "known": bridge.dry_run_tool("MECHANICUS_VALIDATE"),
        "unknown": bridge.dry_run_tool("arbitrary.shell"),
        "real": bridge.request_real_execution("MECHANICUS_VALIDATE"),
    }, indent=2))
