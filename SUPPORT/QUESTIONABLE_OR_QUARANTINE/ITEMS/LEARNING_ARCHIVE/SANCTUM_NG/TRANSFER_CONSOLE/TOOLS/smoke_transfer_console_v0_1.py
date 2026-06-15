#!/usr/bin/env python3
"""Smoke checks for Sanctum NG Transfer Console foundation."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-TRANSFER-CONSOLE-VM3-V0_1"
BASE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_command(cmd: list[str], cwd: Path) -> dict[str, Any]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def add_step(steps: list[dict[str, Any]], warnings: list[str], blockers: list[str], step: str, status: str, details: Any) -> None:
    steps.append({"step": step, "status": status, "details": details})
    if status == "WARN":
        warnings.append(step)
    if status == "BLOCK":
        blockers.append(step)


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[4]
    default_report_dir = default_repo_root / f"{BASE_REL}/REPORTS/{TASK_ID_DEFAULT}"
    parser = argparse.ArgumentParser(description="Run transfer console smoke checks.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output", type=Path, default=default_report_dir / "transfer_console_smoke_report.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    report_dir = args.report_dir.resolve()
    output = args.output.resolve()

    runner = repo_root / f"{BASE_REL}/TOOLS/transfer_console_action_runner_v0_1.py"
    validator = repo_root / f"{BASE_REL}/TOOLS/validate_transfer_console_v0_1.py"
    view_state_path = repo_root / f"{BASE_REL}/DATA/TRANSFER_CONSOLE_VIEW_STATE.generated.json"

    steps: list[dict[str, Any]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    report_dir.mkdir(parents=True, exist_ok=True)

    action_sequence = [
        "CHECK_CONTOUR_STATUS",
        "DRY_RUN_TASKPACK_SEND",
        "DRY_RUN_REPORT_FETCH",
        "REFRESH_TRANSFER_CONSOLE_VIEW",
    ]

    for action_id in action_sequence:
        cmd = [
            "python3",
            str(runner),
            "--repo-root",
            str(repo_root),
            "--task-id",
            str(args.task_id),
            "--action-id",
            action_id,
            "--requester",
            "TRANSFER_CONSOLE_SMOKE",
            "--report-dir",
            str(report_dir),
        ]
        result = run_command(cmd, repo_root)
        status = "PASS" if result["returncode"] == 0 else "BLOCK"
        add_step(steps, warnings, blockers, f"action_{action_id}", status, result)

    validator_cmd = [
        "python3",
        str(validator),
        "--repo-root",
        str(repo_root),
        "--task-id",
        str(args.task_id),
        "--report-dir",
        str(report_dir),
        "--output",
        str(report_dir / "transfer_console_validator_report.json"),
    ]
    validator_result = run_command(validator_cmd, repo_root)
    add_step(
        steps,
        warnings,
        blockers,
        "validator_run",
        "PASS" if validator_result["returncode"] == 0 else "BLOCK",
        validator_result,
    )

    view_state = load_json(view_state_path)
    if view_state is None:
        add_step(steps, warnings, blockers, "view_state_exists", "BLOCK", "missing or invalid view state")
    else:
        contours = view_state.get("contour_cards", [])
        contour_ids = set()
        if isinstance(contours, list):
            for item in contours:
                if isinstance(item, dict):
                    contour_ids.add(str(item.get("contour_id", "")))
        add_step(
            steps,
            warnings,
            blockers,
            "contour_cards_visible",
            "PASS" if {"PC", "VM2", "VM3"}.issubset(contour_ids) else "BLOCK",
            {"contour_ids": sorted(contour_ids)},
        )

        mix = view_state.get("context_source_mix", {})
        mix_ok = isinstance(mix, dict) and mix.get("external_local_private_percent") == 0
        add_step(
            steps,
            warnings,
            blockers,
            "context_source_mix_zero_external",
            "PASS" if mix_ok else "WARN",
            mix,
        )

    index_html = (repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/index.html").read_text(encoding="utf-8")
    app_js = (repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/app.js").read_text(encoding="utf-8")

    add_step(
        steps,
        warnings,
        blockers,
        "ui_transfer_panel_visible",
        "PASS" if "id=\"transfer-console\"" in index_html else "BLOCK",
        "transfer console panel id check",
    )

    add_step(
        steps,
        warnings,
        blockers,
        "ui_render_wiring",
        "PASS" if "renderTransferConsole" in app_js else "BLOCK",
        "renderTransferConsole function presence",
    )

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report = {
        "schema_id": "TRANSFER_CONSOLE_SMOKE_REPORT_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "steps": steps,
        "warnings": warnings,
        "blockers": blockers,
        "no_fake_green_note": "Smoke report is foundation-only and blocks green-only claims without receipts.",
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"transfer_console_smoke_verdict={verdict}")
    print(f"transfer_console_smoke_report={output.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
