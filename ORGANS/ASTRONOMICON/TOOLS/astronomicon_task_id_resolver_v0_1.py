#!/usr/bin/env python3
"""Stage2 Astronomicon task ID resolver entrypoint."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent))

from astronomicon_task_entry_lib_v0_1 import resolve_task_id, write_json  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve task_id via Astronomicon task registry.")
    parser.add_argument("--task-id", default="", help="Task ID to resolve. If empty, use current expected task.")
    parser.add_argument("--repo-root", default=".", help="Repository root. Defaults to current working directory.")
    parser.add_argument(
        "--actor",
        default="astronomicon_task_id_resolver_v0_1.py",
        help="Actor string written into generated machine artifacts.",
    )
    parser.add_argument(
        "--receipt-out",
        default="",
        help="Optional explicit output path for resolver receipt JSON.",
    )
    args = parser.parse_args()

    receipt = resolve_task_id(
        repo_root=args.repo_root,
        task_id=args.task_id if args.task_id else None,
        actor=args.actor,
        write_receipt=True,
        receipt_output_path=args.receipt_out if args.receipt_out else None,
    )

    if args.receipt_out:
        write_json(Path(args.receipt_out), receipt)

    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt.get("resolver_verdict") in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
