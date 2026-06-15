from __future__ import annotations

import argparse
import json

from shell_router import route

MENU = [
    ("1", "dashboard"),
    ("2", "current-task"),
    ("3", "reports"),
    ("4", "receipts"),
    ("5", "tools"),
    ("6", "capabilities"),
    ("7", "policy"),
    ("8", "extensions"),
    ("9", "workspace"),
    ("10", "validate"),
    ("11", "workbench-status"),
    ("12", "workbench-smoke"),
    ("13", "warp-status"),
    ("14", "warp-smoke"),
    ("15", "metaos"),
    ("16", "metaos-smoke"),
    ("17", "ops"),
    ("18", "task-console"),
    ("19", "build-taskpack"),
    ("20", "register-taskpack"),
    ("21", "launch-card"),
    ("22", "lifecycle-smoke"),
    ("23", "git-closure"),
    ("0", "exit"),
]


def smoke() -> dict:
    dashboard = route("dashboard")
    help_result = route("help")
    status = "PASS_WITH_WARNINGS"
    if dashboard["receipt"]["status"] == "BLOCKED" or help_result["receipt"]["status"] == "BLOCKED":
        status = "BLOCKED"
    return {
        "tui_mode": "non_interactive_smoke",
        "menu_count": len(MENU) - 1,
        "dashboard_status": dashboard["receipt"]["status"],
        "help_status": help_result["receipt"]["status"],
        "status": status,
        "full_gui_implemented": False,
    }


def interactive() -> int:
    commands = dict(MENU)
    while True:
        print("\nImperial IDE Control Shell")
        for key, command in MENU:
            print(f"{key}. {command}")
        choice = input("> ").strip()
        command = commands.get(choice)
        if command == "exit":
            return 0
        if command is None:
            print(json.dumps({"status": "BLOCKED", "reason": "unknown_menu_choice"}))
            continue
        print(json.dumps(route(command), ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Imperial IDE menu TUI")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--command")
    args = parser.parse_args(argv)
    if args.smoke:
        result = smoke()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result["status"] == "BLOCKED" else 0
    if args.command:
        result = route(args.command)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result["receipt"]["status"] == "BLOCKED" else 0
    return interactive()


if __name__ == "__main__":
    raise SystemExit(main())
