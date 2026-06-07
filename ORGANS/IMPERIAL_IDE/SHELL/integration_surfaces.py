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
}

SMOKE_PATHS = {
    "workbench_tui": ["ORGANS/IMPERIAL_IDE/WORKBENCH/TUI/imperial_tui.py", "--smoke", "--no-color"],
    "workbench_gui": ["ORGANS/IMPERIAL_IDE/WORKBENCH/GUI/imperial_gui_workbench.py", "--smoke"],
    "warp": ["ORGANS/IMPERIAL_IDE/WARP/warp_smoke.py"],
    "metaos": ["ORGANS/IMPERIAL_IDE/METAOS/metaos_smoke.py"],
    "bundle_gate": ["ORGANS/ADMINISTRATUM/BUNDLE_GATES/administratum_bundle_gate_adapter.py", "--smoke"],
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


def route_surface(repo_root: Path, command: str, args: list[str]) -> dict[str, Any]:
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
