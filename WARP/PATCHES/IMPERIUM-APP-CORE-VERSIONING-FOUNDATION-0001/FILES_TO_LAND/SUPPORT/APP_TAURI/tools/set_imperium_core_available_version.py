#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, time
from pathlib import Path

def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for c in [cur, *cur.parents]:
        if (c/"SUPPORT"/"APP_TAURI").is_dir() and (c/"WARP").is_dir():
            return c
    raise SystemExit("Repo root not found")

def main() -> int:
    ap = argparse.ArgumentParser(description="Stage an available Imperium Core version for app detection.")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--version", required=True)
    ap.add_argument("--notes", default="Terminal patch staged a new Imperium Core version.")
    ap.add_argument("--ready", action="store_true", default=True)
    args = ap.parse_args()
    repo = find_repo_root(Path(args.repo_root))
    state = repo/"SUPPORT"/"APP_TAURI"/"state"
    state.mkdir(parents=True, exist_ok=True)
    path = state/"imperium_core_available_version.json"
    value = {
        "app_id": "IMPERIUM_CORE",
        "product_name": "Imperium Core",
        "available_version": args.version,
        "published_by": "terminal_patch_lane",
        "update_ready": bool(args.ready),
        "notes": [args.notes],
        "generated_at_unix": int(time.time()),
        "truth_boundary": "This file advertises availability only; update/install still requires valid patch receipts."
    }
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(f"IMPERIUM_CORE_AVAILABLE_VERSION: {args.version}")
    print(f"PATH: {path}")
    return 0
if __name__ == "__main__": raise SystemExit(main())
