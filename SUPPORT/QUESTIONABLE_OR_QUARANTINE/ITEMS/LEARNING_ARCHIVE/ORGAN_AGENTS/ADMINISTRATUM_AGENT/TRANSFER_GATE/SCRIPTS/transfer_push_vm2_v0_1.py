#!/usr/bin/env python3
"""Push a prompt pack to VM2 with remote SHA256 and size verification."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from transfer_gate_core_v0_1 import DEFAULT_TRANSFER_ROOT, push_vm2_prompt_pack


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Push an Administratum prompt pack to VM2.")
    parser.add_argument("--pack-zip", default=None)
    parser.add_argument("--step-name", default="")
    parser.add_argument("--source-head", default="UNKNOWN")
    parser.add_argument("--operator", default="OWNER")
    parser.add_argument("--task-id", default=None)
    parser.add_argument("--vm-user", default="vboxuser2")
    parser.add_argument("--vm-host", default="127.0.0.1")
    parser.add_argument("--vm-port", type=int, default=2223)
    parser.add_argument("--vm-key", default=os.environ.get("IMPERIUM_VM2_SSH_KEY"))
    parser.add_argument("--remote-root", default="/home/vboxuser2/IMPERIUM_CONTEXT/LOCAL/ADMINISTRATUM_TRANSFER")
    parser.add_argument("--runtime-root", default=str(DEFAULT_TRANSFER_ROOT))
    parser.add_argument("--transport", choices=["ssh", "local"], default="ssh")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = push_vm2_prompt_pack(
        args.pack_zip,
        step_name=args.step_name,
        source_head=args.source_head,
        operator=args.operator,
        task_id=args.task_id,
        vm_user=args.vm_user,
        vm_host=args.vm_host,
        vm_port=args.vm_port,
        vm_key=args.vm_key,
        remote_root=args.remote_root,
        runtime_root=Path(args.runtime_root),
        transport=args.transport,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not str(result.get("verdict", "")).startswith("BLOCKED") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
