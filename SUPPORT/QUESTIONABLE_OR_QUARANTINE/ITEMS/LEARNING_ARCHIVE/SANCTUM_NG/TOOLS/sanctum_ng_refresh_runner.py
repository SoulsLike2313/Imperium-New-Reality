#!/usr/bin/env python3
"""Run Sanctum NG state builder and validator in one bounded refresh flow."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260522-NEWGEN-SANCTUM-ACTION-LAYER-HARDENING-VM3-V0_1"
REQUIRED_STARTING_HEAD_DEFAULT = "573169b9830ecb0322202e33a3e12ca2fc5e3556"


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


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]

    parser = argparse.ArgumentParser(description="Refresh Sanctum NG state and validation.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--required-starting-head", default=REQUIRED_STARTING_HEAD_DEFAULT)
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=None,
        help="Optional custom report dir. Default: IMPERIUM_NEW_GENERATION/REPORTS/<task-id>",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(value, dict):
        return None
    return value


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    task_id = str(args.task_id)

    report_dir = args.report_dir
    if report_dir is None:
        report_dir = repo_root / f"IMPERIUM_NEW_GENERATION/REPORTS/{task_id}"
    else:
        report_dir = report_dir.resolve()

    state_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json"
    schema_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/sanctum_ng_state.schema.json"
    builder_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TOOLS/sanctum_ng_state_builder.py"
    validator_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TOOLS/sanctum_ng_validator.py"
    runner_report_path = report_dir / "SANCTUM_NG_REFRESH_RUNNER_REPORT.json"
    validator_report_path = report_dir / "VALIDATOR_REPORT.json"

    report_dir.mkdir(parents=True, exist_ok=True)
    runner_report_path.write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "task_id": task_id,
                "status": "PENDING",
                "note": "Placeholder written before validator run."
            },
            indent=2,
            ensure_ascii=False
        ) + "\n",
        encoding="utf-8",
    )

    builder_cmd = [
        "python3",
        str(builder_path),
        "--repo-root",
        str(repo_root),
        "--output",
        str(state_path),
        "--task-id",
        task_id,
        "--required-starting-head",
        str(args.required_starting_head),
    ]

    validator_cmd = [
        "python3",
        str(validator_path),
        "--repo-root",
        str(repo_root),
        "--state",
        str(state_path),
        "--schema",
        str(schema_path),
        "--report-dir",
        str(report_dir),
        "--output",
        str(validator_report_path),
        "--task-id",
        task_id,
    ]

    builder_result = run_command(builder_cmd, repo_root)
    validator_result = run_command(validator_cmd, repo_root)

    validator_payload = load_json(validator_report_path) or {}
    validator_verdict = str(validator_payload.get("verdict", "UNKNOWN"))

    state_payload = load_json(state_path) or {}
    communication_gate = state_payload.get("communication_gate", {})
    communication_status = "UNKNOWN"
    if isinstance(communication_gate, dict):
        communication_status = str(communication_gate.get("STATUS", "UNKNOWN"))

    if builder_result["returncode"] != 0 or validator_result["returncode"] != 0:
        verdict = "BLOCK"
    elif validator_verdict == "PASS":
        verdict = "PASS"
    elif validator_verdict == "WARN":
        verdict = "WARN"
    else:
        verdict = "WARN"

    runner_report = {
        "schema_version": "0.1",
        "task_id": task_id,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "verdict": verdict,
        "builder_result": builder_result,
        "validator_result": validator_result,
        "validator_verdict": validator_verdict,
        "communication_gate_status": communication_status,
        "state_path": state_path.relative_to(repo_root).as_posix(),
        "validator_report_path": validator_report_path.relative_to(repo_root).as_posix(),
        "notes": [
            "Runner executes bounded build -> validate flow.",
            "No external dependency install is required.",
            "PASS means builder succeeded and validator returned PASS."
        ]
    }

    runner_report_path.write_text(json.dumps(runner_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"runner_verdict={verdict}")
    print(f"runner_report={runner_report_path.relative_to(repo_root).as_posix()}")

    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
