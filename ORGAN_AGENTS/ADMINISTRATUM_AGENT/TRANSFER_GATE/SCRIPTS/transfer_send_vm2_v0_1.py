#!/usr/bin/env python3
"""Sign and place a verified prompt pack in the manual VM2 intake zone."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from transfer_gate_core_v0_1 import DEFAULT_TRANSFER_ROOT, send_vm2_prompt_pack


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Send a prompt pack to the VM2 manual intake zone.")
    parser.add_argument("pack_zip", help="Path to prompt pack ZIP.")
    parser.add_argument("--step-name", required=True, help="Human step name supplied by Owner/operator.")
    parser.add_argument("--source-head", default="UNKNOWN", help="Source repository HEAD to stamp in receipt.")
    parser.add_argument("--operator", default="OWNER")
    parser.add_argument("--runtime-root", default=str(DEFAULT_TRANSFER_ROOT))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = send_vm2_prompt_pack(
        Path(args.pack_zip),
        step_name=args.step_name,
        source_head=args.source_head,
        operator=args.operator,
        runtime_root=Path(args.runtime_root),
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not str(result.get("verdict", "")).startswith("BLOCKED") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
