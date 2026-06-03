#!/usr/bin/env python3
"""Owner-facing Astronomicon launcher gated by bootstrap preflight."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent))

from astronomicon_bootstrap_preflight_v0_1 import (  # noqa: E402
    DEFAULT_TASK_ID,
    normalize_repo_root,
    run_preflight,
    write_json,
)
from astronomicon_task_entry_lib_v0_1 import build_context, register_taskpack, resolve_task_id  # noqa: E402


def _print_json_block(title: str, payload: dict[str, Any]) -> None:
    print(f"\n== {title} ==")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _print_current_expected(repo_root: Path) -> None:
    ctx = build_context(repo_root)
    current = ctx["current_expected"]
    if not current.exists():
        print("\n== CURRENT EXPECTED TASK ==\nNo current expected task registered.")
        return
    try:
        payload = json.loads(current.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"\n== CURRENT EXPECTED TASK ==\nCannot parse file: {exc}")
        return
    _print_json_block("CURRENT EXPECTED TASK", payload)


def _owner_repair_hint(repo_root: Path) -> str:
    script = "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TOOLS/astronomicon_bootstrap_repair_v0_1.py"
    return f"python {script} --repo-root \"{repo_root}\" --force"


def _run_tui(repo_root: Path) -> int:
    tui_script = Path(__file__).resolve().parent / "astronomicon_task_entry_tui_v0_1.py"
    cmd = [sys.executable, str(tui_script), "--repo-root", str(repo_root)]
    print("\nЗапуск интерактивного Astronomicon TUI (фиксчурные раннеры не выбираются автоматически).")
    return subprocess.run(cmd, check=False).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Owner launcher with mandatory bootstrap preflight gate.")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID, help="Task ID for preflight metadata.")
    parser.add_argument("--register-zip", default="", help="Register taskpack ZIP path.")
    parser.add_argument("--resolve-task-id", default="", help="Resolve explicit task_id.")
    parser.add_argument("--resolve-current", action="store_true", help="Resolve current expected task.")
    parser.add_argument("--show-current", action="store_true", help="Print current expected task.")
    parser.add_argument("--preflight-only", action="store_true", help="Run only preflight and exit.")
    parser.add_argument("--preflight-receipt-path", default="", help="Write preflight receipt to JSON path.")
    args = parser.parse_args()

    repo_root = normalize_repo_root(args.repo_root)
    preflight = run_preflight(repo_root=repo_root, task_id=args.task_id)
    if args.preflight_receipt_path:
        write_json((repo_root / args.preflight_receipt_path).resolve(), preflight)

    _print_json_block("BOOTSTRAP PREFLIGHT", preflight)
    if preflight.get("verdict") == "BLOCK":
        print("\n== OWNER ACTION REQUIRED (RU) ==")
        print("Bootstrap preflight вернул BLOCK. Intake/TUI запуск остановлен до исправления.")
        print("Команда repair:")
        print(_owner_repair_hint(repo_root))
        print("После repair снова запустите этот launcher.")
        return 1

    if args.preflight_only:
        return 0

    if args.show_current:
        _print_current_expected(repo_root)
        return 0

    if args.register_zip:
        result = register_taskpack(repo_root=repo_root, source_zip_path=args.register_zip)
        _print_json_block("TASKPACK ADMISSION RESULT", result)
        return 0 if result.get("admission_verdict") in {"ADMISSION_PASS", "ADMISSION_PASS_WITH_WARNINGS"} else 1

    if args.resolve_task_id:
        result = resolve_task_id(repo_root=repo_root, task_id=args.resolve_task_id, write_receipt=True)
        _print_json_block("TASK RESOLVER RESULT", result)
        return 0 if result.get("resolver_verdict") in {"PASS", "PASS_WITH_WARNINGS"} else 1

    if args.resolve_current:
        result = resolve_task_id(repo_root=repo_root, task_id=None, write_receipt=True)
        _print_json_block("TASK RESOLVER RESULT", result)
        return 0 if result.get("resolver_verdict") in {"PASS", "PASS_WITH_WARNINGS"} else 1

    return _run_tui(repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
