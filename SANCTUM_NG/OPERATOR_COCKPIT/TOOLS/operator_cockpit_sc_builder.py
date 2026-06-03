#!/usr/bin/env python3
"""Build stable/candidate cockpit package metadata for task-local reporting."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-COCKPIT-STABLE-CANDIDATE-VISUAL-OBSERVABILITY-PC-V0_1"
BASE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/OPERATOR_COCKPIT"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def rel(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def run_command(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[4]
    default_report_dir = default_repo_root / f"{BASE_REL}/REPORTS/{TASK_ID_DEFAULT}"
    parser = argparse.ArgumentParser(description="Build stable/candidate cockpit task metadata.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output", type=Path, default=default_report_dir / "operator_cockpit_sc_report.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    report_dir = args.report_dir.resolve()
    output = args.output.resolve()

    report_dir.mkdir(parents=True, exist_ok=True)

    stable_html = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.html"
    candidate_html = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_candidate.html"
    stable_css = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.css"
    candidate_css = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_candidate.css"
    shared_js = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.js"

    launch_helper = repo_root / f"{BASE_REL}/TOOLS/launch_operator_cockpit.ps1"
    promotion_contract = repo_root / f"{BASE_REL}/CONTRACTS/STABLE_CANDIDATE_PROMOTION_CONTRACT_V0_1.md"

    l1_builder = repo_root / f"{BASE_REL}/TOOLS/operator_cockpit_l1_builder.py"
    l1_build_cmd = [
        "python",
        str(l1_builder),
        "--repo-root",
        str(repo_root),
        "--task-id",
        str(args.task_id),
        "--report-dir",
        str(report_dir),
        "--output-report",
        str(report_dir / "operator_cockpit_l1_report.json"),
        "--build-small-continuity-pack",
    ]
    rc, out, err = run_command(l1_build_cmd, repo_root)

    state_path = repo_root / f"{BASE_REL}/DATA/operator_cockpit_l1_state.generated.json"
    state_ref = rel(state_path, repo_root)

    report = {
        "schema_id": "OPERATOR_COCKPIT_STABLE_CANDIDATE_BUILD_REPORT_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "verdict": "PASS" if rc == 0 else "BLOCK",
        "build_command": l1_build_cmd,
        "build_returncode": rc,
        "build_stdout": out,
        "build_stderr": err,
        "launch_points": {
            "stable": {
                "path": rel(stable_html, repo_root),
                "url": "http://127.0.0.1:8765/IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.html",
            },
            "candidate": {
                "path": rel(candidate_html, repo_root),
                "url": "http://127.0.0.1:8765/IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_candidate.html",
            },
        },
        "entry_assets": {
            "stable_html": rel(stable_html, repo_root),
            "stable_css": rel(stable_css, repo_root),
            "candidate_html": rel(candidate_html, repo_root),
            "candidate_css": rel(candidate_css, repo_root),
            "shared_js": rel(shared_js, repo_root),
        },
        "contracts": {
            "promotion_contract": rel(promotion_contract, repo_root),
            "launch_helper": rel(launch_helper, repo_root),
            "generated_state": state_ref,
        },
        "claim_boundary": "IMPROVED_PC_OPERATOR_SHELL_ONLY",
        "forbidden_claims": [
            "production orchestration",
            "live autonomous multi-contour operations",
            "fake-ready green without evidence",
        ],
    }

    write_json(output, report)
    print(f"operator_cockpit_sc_report={rel(output, repo_root)}")
    print(f"operator_cockpit_sc_verdict={report['verdict']}")
    return 0 if rc == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
