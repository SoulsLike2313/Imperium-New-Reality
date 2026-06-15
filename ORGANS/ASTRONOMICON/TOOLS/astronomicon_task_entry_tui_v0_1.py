#!/usr/bin/env python3
"""Minimal Stage2 Astronomicon owner-facing text UI."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent))

from astronomicon_task_entry_lib_v0_1 import build_context, register_taskpack, resolve_task_id  # noqa: E402


def print_current_expected(repo_root: str | Path) -> None:
    ctx = build_context(repo_root)
    current = ctx["current_expected"]
    print("\n== CURRENT EXPECTED TASK ==")
    if not current.exists():
        print("No current expected task registered.")
        return
    try:
        payload = json.loads(current.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Cannot parse current_expected_task.json: {exc}")
        return
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def print_result(result: dict[str, Any], verdict_key: str) -> None:
    verdict = result.get(verdict_key, "UNKNOWN")
    task_id = result.get("task_id", "")
    registered = result.get("registered_task_path", result.get("registered_path", ""))
    print("\n== RESULT ==")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if task_id and verdict in {"ADMISSION_PASS", "ADMISSION_PASS_WITH_WARNINGS", "PASS", "PASS_WITH_WARNINGS"}:
        print("\n== OWNER NEXT STEP ==")
        print(f"TASK_ID: {task_id}")
        if registered:
            print(f"REGISTERED_PATH: {registered}")
        print(f"Передай Servitor: TASK_ID: {task_id} и start task")


def register_flow(repo_root: str | Path, zip_path: str) -> int:
    result = register_taskpack(repo_root=repo_root, source_zip_path=zip_path)
    print_result(result, "admission_verdict")
    return 0 if result.get("admission_verdict") in {"ADMISSION_PASS", "ADMISSION_PASS_WITH_WARNINGS"} else 1


def resolve_flow(repo_root: str | Path, task_id: str | None = None) -> int:
    result = resolve_task_id(repo_root=repo_root, task_id=task_id, write_receipt=True)
    print_result(result, "resolver_verdict")
    return 0 if result.get("resolver_verdict") in {"PASS", "PASS_WITH_WARNINGS"} else 1


def registration_skill_flow(repo_root: str | Path) -> int:
    skill_script = (
        Path(__file__).resolve().parents[1]
        / "SKILLS/TASKPACK_REGISTRATION_SKILL/astronomicon_taskpack_registration_skill_v0_1.py"
    )
    if not skill_script.exists():
        print(f"Registration Skill script not found: {skill_script}")
        return 1
    cmd = [sys.executable, str(skill_script), "--repo-root", str(repo_root), "--interactive"]
    return subprocess.run(cmd, check=False).returncode


def interactive_loop(repo_root: str | Path) -> int:
    while True:
        print("\n== ASTRONOMICON TASK ENTRY TUI V0.1 ==")
        print("1) Show current expected task")
        print("2) Register taskpack ZIP path")
        print("3) Resolve task_id")
        print("4) Open Taskpack Registration Skill (PC/VM3/VM2)")
        print("5) Exit")
        choice = input("Select: ").strip()

        if choice == "1":
            print_current_expected(repo_root)
        elif choice == "2":
            zip_path = input("ZIP path: ").strip()
            register_flow(repo_root, zip_path)
        elif choice == "3":
            task_id = input("task_id (empty => current expected): ").strip()
            resolve_flow(repo_root, task_id if task_id else None)
        elif choice == "4":
            registration_skill_flow(repo_root)
        elif choice == "5":
            print("Exit.")
            return 0
        else:
            print("Unknown option.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal Astronomicon task entry text UI.")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--show-current", action="store_true", help="Print current expected task and exit.")
    parser.add_argument("--register-zip", default="", help="Register provided ZIP path and exit.")
    parser.add_argument("--resolve-task-id", default="", help="Resolve given task_id and exit.")
    parser.add_argument("--resolve-current", action="store_true", help="Resolve current expected task and exit.")
    parser.add_argument("--registration-skill", action="store_true", help="Open registration skill interactive flow.")
    args = parser.parse_args()

    repo_root = args.repo_root
    if args.show_current:
        print_current_expected(repo_root)
        return 0
    if args.register_zip:
        return register_flow(repo_root, args.register_zip)
    if args.resolve_task_id:
        return resolve_flow(repo_root, args.resolve_task_id)
    if args.resolve_current:
        return resolve_flow(repo_root, None)
    if args.registration_skill:
        return registration_skill_flow(repo_root)
    return interactive_loop(repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
