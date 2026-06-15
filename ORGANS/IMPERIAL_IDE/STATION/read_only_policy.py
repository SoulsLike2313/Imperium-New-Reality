from __future__ import annotations

from typing import Any

TASK_ID = "TASK-NEWREALITY-IMPERIAL-IDE-OPERATIONAL-STATION-TRUTH-FIX-DAILY-OPS-SHELL-PC-V0_1"

READ_ONLY_COMMANDS = [
    "help",
    "station",
    "agents",
    "agent-status",
    "taskpack-manager",
    "taskpacks",
    "taskpack-list",
    "taskpack-inspect",
    "taskpack-open",
    "taskpack-copy-path",
    "dirty-classifier",
    "safety",
    "git-closure",
    "reports-latest",
    "receipts-latest",
    "show-summary",
    "show-json",
    "full-json",
    "launch-card",
    "handoff-card",
    "daily-ops",
    "next-action",
    "operator-board",
    "task-flow",
    "lifecycle",
]

DRY_RUN_COMMANDS = [
    "new-task",
    "task-console",
    "build-taskpack",
    "register-taskpack",
    "validate-taskpack",
    "taskpack-validate",
]

SMOKE_COMMANDS = [
    "station-smoke",
    "station-ux-smoke",
    "task-flow-smoke",
    "workbench-smoke",
    "lifecycle-smoke",
]

REPORT_WRITING_COMMANDS = [
    "station-ux-smoke",
]


def command_mutation_profile(command: str) -> dict[str, Any]:
    mutates_repo = command in DRY_RUN_COMMANDS or command in SMOKE_COMMANDS
    return {
        "command": command,
        "mutates_repo": mutates_repo,
        "read_only": command in READ_ONLY_COMMANDS,
        "dry_run": command in DRY_RUN_COMMANDS,
        "smoke": command in SMOKE_COMMANDS,
        "may_write_runtime_receipt": command in DRY_RUN_COMMANDS or command in SMOKE_COMMANDS,
        "may_write_report_receipt": command in REPORT_WRITING_COMMANDS,
        "tracked_report_write_allowed": command in REPORT_WRITING_COMMANDS,
        "risk_class": "LOW_READ_ONLY" if command in READ_ONLY_COMMANDS else "LOW_DRY_RUN",
    }


def policy_summary() -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "status": "PASS_WITH_WARNINGS",
        "read_only_commands": READ_ONLY_COMMANDS,
        "dry_run_commands": DRY_RUN_COMMANDS,
        "smoke_commands": SMOKE_COMMANDS,
        "rules": [
            "read-only commands must not modify tracked repository files",
            "read-only commands may print receipts to stdout",
            "optional runtime receipts must stay under ignored runtime paths",
            "tracked report receipts are written only by explicit smoke or report finalization commands",
            "post-push inspection must not rewrite committed report receipts",
            "command receipts must include mutates_repo",
        ],
    }
