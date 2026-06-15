#!/usr/bin/env python3
"""Text UI for the Imperial IDE OPS task console.

The TUI is usable in a bare terminal and smoke-testable with --smoke. It keeps
all operational actions in dry-run mode by default.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ENGINE = os.path.normpath(os.path.join(_HERE, "..", "ENGINE"))
if _ENGINE not in sys.path:
    sys.path.insert(0, _ENGINE)

from imperium_ops import (  # noqa: E402
    astronomicon_register as astro,
    git_closure,
    launch_card as lc,
    lifecycle,
    safety_gate,
    task_console,
    taskpack_builder as tpb,
)

MENU = [
    ("1", "Task Console"),
    ("2", "Task Templates"),
    ("3", "Build Taskpack"),
    ("4", "Register Taskpack"),
    ("5", "Launch Card"),
    ("6", "Lifecycle Dry Run"),
    ("7", "Reports"),
    ("8", "Receipts"),
    ("9", "Git Closure"),
    ("10", "Safety"),
    ("q", "Quit"),
]

REQUIRED_MENU_LABELS = [
    "Task Console",
    "Task Templates",
    "Build Taskpack",
    "Register Taskpack",
    "Launch Card",
    "Lifecycle Dry Run",
    "Reports",
    "Receipts",
    "Git Closure",
    "Safety",
]


def _repo_root() -> str:
    return os.path.abspath(os.environ.get("IMPERIUM_ROOT", os.getcwd()))


def _out_root(repo: str) -> str:
    return os.path.join(repo, "ORGANS", "IMPERIAL_IDE", "OPS", "STAGING", "TASKPACKS")


def render_menu() -> str:
    lines = ["", "=== IMPERIAL IDE :: OPS TASK CONSOLE ==="]
    for key, label in MENU:
        lines.append(f"  [{key}] {label}")
    lines.append("========================================")
    return "\n".join(lines)


def dashboard(repo: str) -> str:
    gs = git_closure.git_status(repo)
    state = safety_gate.load_safety(repo)
    rep = safety_gate.safety_receipt_fields(repo, state)
    regs = astro.list_registered(repo)
    out = [
        "-- OPS DASHBOARD --",
        f"repo        : {repo}",
        f"git         : {gs}",
        f"registered  : {len(regs)} task(s), including dry-run staging",
        "safety      :",
    ]
    for k, v in rep.items():
        out.append(f"   {k}: {v}")
    return "\n".join(out)


def _intent_from_prompt() -> task_console.TaskIntent:
    title = input("Title: ").strip()
    goal = input("Goal: ").strip() or title
    ttype = input("Type (blank = auto): ").strip() or None
    scope = input("Scope [IMPERIAL_IDE]: ").strip() or "IMPERIAL_IDE"
    risk = input("Risk [CONTROLLED_WRITE]: ").strip() or "CONTROLLED_WRITE"
    push = input("Push policy [VALIDATED_PUSH]: ").strip() or "VALIDATED_PUSH"
    return task_console.new_task(
        title=title,
        goal=goal,
        task_type=ttype,
        scope=scope,
        risk=risk,
        push_policy=push,
    )


def task_console_flow(repo: str) -> str:
    intent = _intent_from_prompt()
    ok, problems = task_console.validate_intent(intent)
    if not ok:
        return json.dumps({"status": "BLOCKED", "problems": problems}, ensure_ascii=False, indent=2)
    if input("Run full lifecycle dry-run? [y/N]: ").strip().lower() == "y":
        state = safety_gate.load_safety(repo)
        result = lifecycle.run_lifecycle(repo, intent, _out_root(repo), state=state, dry_run=True)
        return lifecycle.render_progress(result) + f"\n\nVERDICT: {result.verdict}"
    extracted = tpb.write_taskpack(_out_root(repo), intent)
    reg = astro.register(repo, extracted, intent, dry_run=True)
    card = lc.build_launch_card(intent, reg.registered_path, reg.admitted, reg.sha256)
    return lc.render_launch_card_text(card)


def _static_panel(name: str) -> str:
    panels = {
        "Task Templates": "Template library: OPS/TEMPLATES/task_templates.json",
        "Build Taskpack": "Dry-run builder writes Astronomicon-compatible files under OPS/STAGING.",
        "Register Taskpack": "Dry-run registration writes under OPS/STAGING; live registration is gated.",
        "Launch Card": "Shows task id, route, sha256, admission status, and start message.",
        "Lifecycle Dry Run": "Runs intent -> builder -> registration -> launch card -> validation -> closure.",
        "Reports": "Dry-run lifecycle reports are under OPS/STAGING/REPORTS.",
        "Receipts": "Receipts validate evidence and fake-green risk.",
        "Git Closure": "Shows status/scope/secret checks; no push without validation gate.",
        "Safety": "Real servitor execution, live LLM, and unsafe shell remain blocked.",
    }
    return f"-- {name} --\n  {panels.get(name, 'panel ready')}"


def smoke(repo: str) -> int:
    labels = [label for _, label in MENU]
    missing = [label for label in REQUIRED_MENU_LABELS if label not in labels]
    payload = {
        "status": "PASS_WITH_WARNINGS" if not missing else "BLOCKED",
        "mode": "non_interactive_menu_validation",
        "repo_root": repo,
        "menu_entries": labels,
        "missing_required_entries": missing,
        "dry_run_default": True,
        "real_execution_enabled": False,
        "live_llm_backend_enabled": False,
        "unsafe_shell_available": False,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not missing else 2


def run(interactive: bool = True) -> int:
    repo = _repo_root()
    print(render_menu())
    if not interactive or not sys.stdin.isatty():
        print(dashboard(repo))
        return 0
    commands = dict(MENU)
    while True:
        choice = input("select> ").strip().lower()
        label = commands.get(choice)
        if label == "Quit":
            print("Exiting OPS task console.")
            return 0
        if label == "Task Console":
            print(task_console_flow(repo))
        elif label:
            print(_static_panel(label))
        else:
            print("Unknown option.")
        print(render_menu())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Imperial IDE OPS task console TUI")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--no-interactive", action="store_true")
    args = parser.parse_args(argv)
    repo = _repo_root()
    if args.smoke:
        return smoke(repo)
    return run(interactive=not args.no_interactive)


if __name__ == "__main__":
    raise SystemExit(main())
