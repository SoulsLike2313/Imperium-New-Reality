#!/usr/bin/env python3
"""Stage2 Astronomicon taskpack intake entrypoint."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent))

from astronomicon_task_entry_lib_v0_1 import register_taskpack, write_json  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Register taskpack ZIP into Astronomicon canonical inbox.")
    parser.add_argument("--zip-path", required=True, help="Path to source taskpack ZIP.")
    parser.add_argument("--repo-root", default=".", help="Repository root. Defaults to current working directory.")
    parser.add_argument(
        "--actor",
        default="astronomicon_taskpack_intake_v0_1.py",
        help="Actor string written into generated machine artifacts.",
    )
    parser.add_argument(
        "--receipt-out",
        default="",
        help="Optional explicit output path for a copy of admission receipt JSON.",
    )
    args = parser.parse_args()

    receipt = register_taskpack(repo_root=args.repo_root, source_zip_path=args.zip_path, actor=args.actor)

    if args.receipt_out:
        write_json(Path(args.receipt_out), receipt)

    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    verdict = str(receipt.get("admission_verdict", "ADMISSION_BLOCK"))
    return 0 if verdict in {"ADMISSION_PASS", "ADMISSION_PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
