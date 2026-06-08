#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from local_bridge import SURFACE, VERSION, snapshot


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="../../..")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    data = snapshot(repo)
    data["surface"] = SURFACE
    data["version"] = VERSION
    out = Path(__file__).resolve().parents[1] / "app" / "imperium_snapshot.json"
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(json.dumps({"status": "PASS", "snapshot": str(out)}, indent=2))


if __name__ == "__main__":
    main()
