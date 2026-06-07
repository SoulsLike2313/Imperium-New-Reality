from __future__ import annotations

import argparse
import json

from shell_router import route

COMMANDS = [
    "doctor", "status", "dashboard", "tasks", "current-task", "reports",
    "latest-report", "receipts", "tools", "capabilities", "policy",
    "extensions", "workspace", "validate", "dry-run-tool", "help",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Imperial IDE controlled local shell")
    parser.add_argument("command", choices=COMMANDS)
    parser.add_argument("command_args", nargs="*")
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = route(args.command, args.command_args)
    print(json.dumps(result, ensure_ascii=False, indent=None if args.compact else 2))
    status = result.get("receipt", {}).get("status")
    return 2 if status == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
