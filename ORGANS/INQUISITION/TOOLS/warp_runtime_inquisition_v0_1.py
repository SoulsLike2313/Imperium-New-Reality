#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SURFACE = "INQUISITION_WARP_RUNTIME_VALIDATOR_V0_8_1"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo = Path(args.repo_root).resolve()
    manager = repo / "ORGANS" / "IMPERIAL_IDE" / "WARP" / "warp_manager.py"
    process = subprocess.run(
        [sys.executable, str(manager), "--repo-root", str(repo), "validate"],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    try:
        payload = json.loads(process.stdout)
    except Exception:
        payload = {"status": "FAIL", "stdout": process.stdout, "stderr": process.stderr}
    payload["inquisition_surface"] = SURFACE
    print(json.dumps(payload, indent=2))
    return 0 if payload.get("status") in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
