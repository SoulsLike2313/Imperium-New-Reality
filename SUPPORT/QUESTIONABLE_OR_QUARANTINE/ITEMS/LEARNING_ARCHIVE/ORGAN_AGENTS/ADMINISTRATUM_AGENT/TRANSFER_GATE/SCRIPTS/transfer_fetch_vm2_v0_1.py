#!/usr/bin/env python3
"""Fetch and verify a VM2 response bundle by exact expected filename."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from transfer_gate_core_v0_1 import DEFAULT_TRANSFER_ROOT, fetch_vm2_response_bundle, fetch_vm2_response_bundle_remote


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch a VM2 response bundle from the transfer outbox.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--expected-filename", default=None)
    parser.add_argument("--correlation-id", default=None)
    parser.add_argument("--runtime-root", default=str(DEFAULT_TRANSFER_ROOT))
    parser.add_argument("--pc-remote", action="store_true")
    parser.add_argument("--vm-user", default="vboxuser2")
    parser.add_argument("--vm-host", default="127.0.0.1")
    parser.add_argument("--vm-port", type=int, default=2223)
    parser.add_argument("--vm-key", default=os.environ.get("IMPERIUM_VM2_SSH_KEY"))
    parser.add_argument("--remote-root", default="/home/vboxuser2/IMPERIUM_CONTEXT/LOCAL/ADMINISTRATUM_TRANSFER")
    parser.add_argument("--transport", choices=["ssh", "local"], default="ssh")
    parser.add_argument("--no-quarantine", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.pc_remote:
        result = fetch_vm2_response_bundle_remote(
            task_id=args.task_id,
            expected_filename=args.expected_filename or "",
            correlation_id=args.correlation_id,
            runtime_root=Path(args.runtime_root),
            vm_user=args.vm_user,
            vm_host=args.vm_host,
            vm_port=args.vm_port,
            vm_key=args.vm_key,
            remote_root=args.remote_root,
            transport=args.transport,
        )
    else:
        result = fetch_vm2_response_bundle(
            task_id=args.task_id,
            expected_filename=args.expected_filename,
            correlation_id=args.correlation_id,
            runtime_root=Path(args.runtime_root),
            quarantine_on_mismatch=not args.no_quarantine,
        )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not str(result.get("verdict", "")).startswith("BLOCKED") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
