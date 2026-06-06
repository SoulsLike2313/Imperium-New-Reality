#!/usr/bin/env python3
"""Run bounded smoke checks for Organ Dialogue demo integration."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-ORGAN-DIALOGUE-DEMO-VM2-V0_1"
DEMO_TASK_ID = "TASK-DEMO-ORGAN-DIALOGUE-V0_1"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def relpath(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return data


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_report_dir = default_repo_root / (
        "IMPERIUM_NEW_GENERATION/REPORTS/"
        "TASK-20260523-NEWGEN-SANCTUM-ORGAN-DIALOGUE-DEMO-VM2-V0_1"
    )

    parser = argparse.ArgumentParser(description="Smoke check Organ Dialogue demo integration.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output", type=Path, default=default_report_dir / "ORGAN_DIALOGUE_DEMO_SMOKE_REPORT.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    report_dir = args.report_dir.resolve()
    output = args.output.resolve()

    checks: list[dict[str, str]] = []
    blockers: list[str] = []

    def add(check_id: str, ok: bool, ok_detail: str, fail_detail: str) -> None:
        checks.append({
            "check_id": check_id,
            "status": "PASS" if ok else "BLOCK",
            "details": ok_detail if ok else fail_detail,
        })
        if not ok:
            blockers.append(f"{check_id}:{fail_detail}")

    run_report = load_json(report_dir / "ORGAN_DIALOGUE_DEMO_RUN_REPORT.json")
    validator_report = load_json(report_dir / "VALIDATOR_REPORT.json")
    sanctum_state = load_json(repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json")

    add(
        "run_report_present",
        isinstance(run_report, dict) and run_report.get("verdict") == "PASS",
        "builder run report exists with PASS",
        "builder run report missing or not PASS",
    )

    add(
        "validator_report_present",
        isinstance(validator_report, dict) and str(validator_report.get("verdict", "")) in {"PASS", "WARN"},
        "validator report exists with PASS/WARN",
        "validator report missing or BLOCK",
    )

    demo_ok = False
    if isinstance(sanctum_state, dict):
        demo = sanctum_state.get("organ_dialogue_demo")
        if isinstance(demo, dict):
            demo_ok = (
                str(demo.get("task_id", "")) == DEMO_TASK_ID
                and int(demo.get("request_count", 0)) == 8
                and int(demo.get("response_count", 0)) == 8
                and str(demo.get("no_live_autonomy_label", "")) == "NO_LIVE_AUTONOMY"
            )

    add(
        "sanctum_state_demo_summary",
        demo_ok,
        "sanctum state includes Organ Dialogue demo summary",
        "sanctum state missing/invalid Organ Dialogue demo summary",
    )

    index_html = (repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/index.html").read_text(encoding="utf-8")
    app_js = (repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/app.js").read_text(encoding="utf-8")

    add(
        "ui_block_marker_exists",
        "organ-dialogue-demo" in index_html and "renderOrganDialogueDemo" in app_js,
        "UI block markers for Organ Dialogue demo exist",
        "UI block markers for Organ Dialogue demo missing",
    )

    verdict = "PASS" if not blockers else "BLOCK"
    payload = {
        "schema_id": "ORGAN_DIALOGUE_DEMO_SMOKE_REPORT_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "checks": checks,
        "blockers": blockers,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"smoke_verdict={verdict}")
    print(f"smoke_report={relpath(output, repo_root)}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
