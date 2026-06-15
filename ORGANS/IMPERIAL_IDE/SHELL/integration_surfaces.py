from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

STATUS_PATHS = {
    "workbench": "ORGANS/IMPERIAL_IDE/WORKBENCH/INTEGRATION_STATUS.json",
    "warp": "ORGANS/IMPERIAL_IDE/WARP/INTEGRATION_STATUS.json",
    "metaos": "ORGANS/IMPERIAL_IDE/METAOS/INTEGRATION_STATUS.json",
    "ops": "ORGANS/IMPERIAL_IDE/OPS/INTEGRATION_STATUS.json",
}

SMOKE_PATHS = {
    "workbench_tui": ["ORGANS/IMPERIAL_IDE/WORKBENCH/TUI/imperial_tui.py", "--smoke", "--no-color"],
    "workbench_gui": ["ORGANS/IMPERIAL_IDE/WORKBENCH/GUI/imperial_gui_workbench.py", "--smoke"],
    "warp": ["ORGANS/IMPERIAL_IDE/WARP/warp_smoke.py"],
    "metaos": ["ORGANS/IMPERIAL_IDE/METAOS/metaos_smoke.py"],
    "bundle_gate": ["ORGANS/ADMINISTRATUM/BUNDLE_GATES/administratum_bundle_gate_adapter.py", "--smoke"],
    "ops": ["ORGANS/IMPERIAL_IDE/OPS/CLI/imperial_ide_ops_cli.py", "smoke"],
    "ops_tui": ["ORGANS/IMPERIAL_IDE/OPS/TUI/imperial_ide_ops_tui.py", "--smoke"],
}


def load_status(repo_root: Path, component: str) -> dict[str, Any]:
    relative = STATUS_PATHS[component]
    with (repo_root / relative).open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    return {"component": component, "path": relative, **data}


def _run_fixed(repo_root: Path, key: str) -> dict[str, Any]:
    argv = [sys.executable, *SMOKE_PATHS[key]]
    completed = subprocess.run(
        argv,
        cwd=repo_root,
        env={**os.environ, "IMPERIUM_ROOT": str(repo_root)},
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
    )
    return {
        "status": "PASS_WITH_WARNINGS" if completed.returncode == 0 else "BLOCKED",
        "smoke": key,
        "exit_code": completed.returncode,
        "stdout": completed.stdout[-6000:].strip(),
        "stderr": completed.stderr[-2000:].strip(),
        "real_execution": False,
    }


def _launch_plan(component: str, surface: str, command: str) -> dict[str, Any]:
    return {
        "status": "PASS_WITH_WARNINGS",
        "component": component,
        "surface": surface,
        "launch_command": command,
        "executed": False,
        "reason": "interactive launch returned as an operator plan",
        "real_execution": False,
    }


def _run_ops_cli(repo_root: Path, args: list[str]) -> dict[str, Any]:
    argv = [sys.executable, "ORGANS/IMPERIAL_IDE/OPS/CLI/imperial_ide_ops_cli.py", *args]
    completed = subprocess.run(
        argv,
        cwd=repo_root,
        env={**os.environ, "IMPERIUM_ROOT": str(repo_root)},
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
    )
    stdout = completed.stdout.strip()
    payload: Any = stdout
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        pass
    return {
        "status": "PASS_WITH_WARNINGS" if completed.returncode == 0 else "BLOCKED",
        "component": "ops",
        "command": args[0] if args else "",
        "argv": argv,
        "exit_code": completed.returncode,
        "payload": payload,
        "stderr": completed.stderr[-2000:].strip(),
        "real_execution": False,
    }


def _sample_intent_args(title: str = "OPS task console shell sample") -> list[str]:
    return [
        "--title", title,
        "--goal", "Build an Astronomicon compatible task from inside Imperial IDE OPS",
        "--type", "integration",
        "--scope", "IMPERIAL_IDE",
        "--risk", "CONTROLLED_WRITE",
        "--push", "VALIDATED_PUSH",
    ]


def route_surface(repo_root: Path, command: str, args: list[str]) -> dict[str, Any]:
    if command in {"ops", "task-console"}:
        data = load_status(repo_root, "ops")
        data["launch_command"] = "python ORGANS/IMPERIAL_IDE/OPS/CLI/imperial_ide_ops_cli.py smoke"
        data["tui_command"] = "python ORGANS/IMPERIAL_IDE/OPS/TUI/imperial_ide_ops_tui.py"
        return data
    if command == "ops-smoke":
        return _run_fixed(repo_root, "ops")
    if command == "classify-task":
        return _run_ops_cli(repo_root, ["classify", *_sample_intent_args()])
    if command == "build-taskpack":
        return _run_ops_cli(repo_root, ["build-taskpack", *_sample_intent_args()])
    if command == "register-taskpack":
        return _run_ops_cli(repo_root, ["register", *_sample_intent_args()])
    if command == "launch-card":
        return _run_ops_cli(repo_root, ["launch-card", *_sample_intent_args()])
    if command == "lifecycle":
        return _run_ops_cli(repo_root, ["lifecycle", *_sample_intent_args()])
    if command == "lifecycle-smoke":
        return _run_fixed(repo_root, "ops")
    if command == "git-closure":
        return _run_ops_cli(repo_root, ["git-status", "--repo", str(repo_root)])
    if command == "task-templates":
        return _run_ops_cli(repo_root, ["task-templates"])

    if command in {"workbench", "workbench-status"}:
        return load_status(repo_root, "workbench")
    if command == "workbench-tui":
        return _launch_plan("workbench", "tui", "ORGANS/IMPERIAL_IDE/run_imperial_workbench.ps1 -Surface tui")
    if command == "workbench-gui":
        return _launch_plan("workbench", "gui_candidate", "ORGANS/IMPERIAL_IDE/run_imperial_workbench.ps1 -Surface gui")
    if command == "workbench-smoke":
        return {
            "status": "PASS_WITH_WARNINGS",
            "component": "workbench",
            "tui": _run_fixed(repo_root, "workbench_tui"),
            "gui_structural": _run_fixed(repo_root, "workbench_gui"),
            "windows_interactive_gui_smoke_proven": False,
        }

    if command in {"warp", "warp-status"}:
        return load_status(repo_root, "warp")
    if command == "warp-open":
        return _launch_plan("warp", "isolated_runtime", "ORGANS/IMPERIAL_IDE/run_warp_zone.ps1 -Command open -Task <task>")
    if command == "warp-list":
        runtime = repo_root / "ORGANS/IMPERIAL_IDE/WARP/runtime"
        sessions = sorted(item.name for item in runtime.iterdir() if item.is_dir()) if runtime.is_dir() else []
        return {"status": "PASS", "runtime_ignored": True, "sessions": sessions, "count": len(sessions)}
    if command == "warp-gate":
        return _launch_plan("warp", "release_manifest_gate", "ORGANS/IMPERIAL_IDE/run_warp_zone.ps1 -Command gate -Session <id>")
    if command == "warp-smoke":
        return _run_fixed(repo_root, "warp")

    if command == "metaos":
        return load_status(repo_root, "metaos")
    if command == "metaos-smoke":
        return _run_fixed(repo_root, "metaos")
    if command == "metaos-route":
        return _launch_plan("metaos", "deterministic_stub_route", "run MetaOS TaskContract through stub tiers")
    if command == "metaos-servitor":
        return _launch_plan("metaos", "one_shot_stub_servitor", "run thin servitor smoke without external backend")
    if command == "metaos-bundle-gate":
        return _run_fixed(repo_root, "bundle_gate")
    if command == "metaos-chronicle":
        return _launch_plan("metaos", "ignored_runtime_chronicle", "write chronicles only under METAOS/chronicles/runtime")
    return {"status": "BLOCKED", "reason": "unknown_integration_surface_command", "command": command}
