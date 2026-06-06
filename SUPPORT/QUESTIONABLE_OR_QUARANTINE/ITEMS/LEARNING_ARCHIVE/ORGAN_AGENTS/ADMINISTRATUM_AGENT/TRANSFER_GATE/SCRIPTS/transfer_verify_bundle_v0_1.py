#!/usr/bin/env python3
"""Verify a Logos prompt pack ZIP for Administratum Transfer Gate V0.1."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from transfer_gate_core_v0_1 import DEFAULT_TRANSFER_ROOT, verify_prompt_pack


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify an Administratum prompt pack ZIP.")
    parser.add_argument("pack_zip", help="Path to prompt pack ZIP.")
    parser.add_argument("--runtime-root", default=str(DEFAULT_TRANSFER_ROOT))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = verify_prompt_pack(Path(args.pack_zip), Path(args.runtime_root))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("verdict") != "BLOCKED" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
