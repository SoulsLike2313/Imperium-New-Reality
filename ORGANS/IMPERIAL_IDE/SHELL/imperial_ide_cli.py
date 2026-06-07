from __future__ import annotations

import argparse
import json
import sys

from shell_router import route

COMMANDS = [
    "doctor", "status", "dashboard", "tasks", "current-task", "reports",
    "latest-report", "receipts", "tools", "capabilities", "policy",
    "extensions", "workspace", "validate", "dry-run-tool", "help",
    "workbench", "workbench-tui", "workbench-gui", "workbench-smoke",
    "workbench-status", "warp", "warp-open", "warp-list", "warp-status",
    "warp-gate", "warp-smoke", "metaos", "metaos-smoke", "metaos-route",
    "metaos-servitor", "metaos-bundle-gate", "metaos-chronicle",
    "ops", "ops-smoke", "task-console", "classify-task", "build-taskpack",
    "register-taskpack", "launch-card", "lifecycle", "lifecycle-smoke",
    "git-closure", "task-templates",
    "station", "station-tui", "station-gui", "station-smoke", "agents",
    "agent-status", "new-task", "validate-taskpack", "handoff-card",
    "reports-latest", "receipts-latest", "safety", "station-ux-smoke",
    "taskpack-manager", "taskpacks", "taskpack-list", "taskpack-inspect",
    "taskpack-validate", "taskpack-open", "taskpack-copy-path", "show-json",
    "full-json", "show-summary", "path-actions", "dirty-classifier",
    "live-registration-promote", "daily-ops", "next-action", "operator-board",
    "task-flow", "task-flow-smoke",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Imperial IDE controlled local shell")
    parser.add_argument("command", choices=COMMANDS)
    parser.add_argument("command_args", nargs="*")
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    args = build_parser().parse_args(argv)
    result = route(args.command, args.command_args)
    print(json.dumps(result, ensure_ascii=False, indent=None if args.compact else 2))
    status = result.get("receipt", {}).get("status")
    return 2 if status == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
