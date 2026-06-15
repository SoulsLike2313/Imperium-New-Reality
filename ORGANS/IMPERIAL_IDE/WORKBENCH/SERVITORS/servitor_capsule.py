#!/usr/bin/env python3
"""One-shot dry-run servitor capsule candidate.

Persistent workers and real command execution are intentionally unavailable.
Queues and results must live under ignored Workbench runtime paths.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run servitor capsule candidate")
    parser.add_argument("--capsule", required=True)
    parser.add_argument("--queue-dir", default=str(Path(__file__).resolve().parent / "runtime"))
    parser.add_argument("--task", default="smoke")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--allow-real", action="store_true")
    args = parser.parse_args(argv)

    if args.allow_real:
        print(json.dumps({
            "status": "BLOCKED",
            "reason": "allow_real_forbidden_by_current_governance",
            "capsule": args.capsule,
            "executed": False,
        }, indent=2))
        return 2
    if not args.once:
        print(json.dumps({
            "status": "BLOCKED",
            "reason": "persistent_capsule_runtime_not_enabled",
            "capsule": args.capsule,
            "executed": False,
        }, indent=2))
        return 2

    print(json.dumps({
        "timestamp_utc": utc_now(),
        "status": "PASS_WITH_WARNINGS",
        "capsule": args.capsule,
        "task": args.task,
        "mode": "DRY_RUN_ONCE",
        "queue_dir": str(Path(args.queue_dir).resolve()),
        "executed": False,
        "real_execution_blocked": True,
        "persistent_runtime_started": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
