#!/usr/bin/env python3
"""Validate stable/candidate cockpit artifacts for the visual observability task."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-COCKPIT-STABLE-CANDIDATE-VISUAL-OBSERVABILITY-PC-V0_1"
BASE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/OPERATOR_COCKPIT"
REQUIRED_ZONE_IDS = [
    "top-truth",
    "focus-gateway",
    "task-session",
    "transfer-routes",
    "evidence-diff",
    "owner-organ",
    "continuity-preview",
    "action-strip",
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "missing"
    except json.JSONDecodeError as exc:
        return None, f"json_decode_error:{exc}"
    if not isinstance(payload, dict):
        return None, "not_json_object"
    return payload, None


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


def add_check(
    checks: list[dict[str, str]],
    warnings: list[str],
    blockers: list[str],
    check_id: str,
    ok: bool,
    pass_detail: str,
    fail_detail: str,
    fail_level: str = "BLOCK",
) -> None:
    if ok:
        checks.append({"check_id": check_id, "status": "PASS", "details": pass_detail})
        return
    checks.append({"check_id": check_id, "status": fail_level, "details": fail_detail})
    if fail_level == "WARN":
        warnings.append(f"{check_id}:{fail_detail}")
    else:
        blockers.append(f"{check_id}:{fail_detail}")


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[4]
    default_report_dir = default_repo_root / f"{BASE_REL}/REPORTS/{TASK_ID_DEFAULT}"
    parser = argparse.ArgumentParser(description="Validate stable/candidate cockpit artifacts.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output", type=Path, default=default_report_dir / "operator_cockpit_sc_validator_report.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    report_dir = args.report_dir.resolve()
    output = args.output.resolve()

    checks: list[dict[str, str]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    stable_html = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.html"
    stable_css = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.css"
    candidate_html = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_candidate.html"
    candidate_css = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_candidate.css"
    shared_js = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.js"
    index_html = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/index.html"
    launch_helper = repo_root / f"{BASE_REL}/TOOLS/launch_operator_cockpit.ps1"
    promotion_contract = repo_root / f"{BASE_REL}/CONTRACTS/STABLE_CANDIDATE_PROMOTION_CONTRACT_V0_1.md"
    research_dossier = report_dir / "research_dossier.json"
    screenshot_matrix = report_dir / "screenshot_matrix.json"
    comparison_report = report_dir / "stable_candidate_comparison.json"

    core_files = [
        stable_html,
        stable_css,
        candidate_html,
        candidate_css,
        shared_js,
        index_html,
        launch_helper,
        promotion_contract,
    ]
    add_check(
        checks,
        warnings,
        blockers,
        "core_track_files_exist",
        all(path.exists() for path in core_files),
        "stable/candidate core files exist",
        "missing one or more stable/candidate core files",
    )

    stable_text = stable_html.read_text(encoding="utf-8") if stable_html.exists() else ""
    candidate_text = candidate_html.read_text(encoding="utf-8") if candidate_html.exists() else ""
    index_text = index_html.read_text(encoding="utf-8") if index_html.exists() else ""
    candidate_css_text = candidate_css.read_text(encoding="utf-8") if candidate_css.exists() else ""

    add_check(
        checks,
        warnings,
        blockers,
        "stable_has_candidate_link",
        "operator_cockpit_candidate.html" in stable_text,
        "stable entry links to candidate",
        "stable entry does not expose candidate launch path",
        fail_level="WARN",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "index_has_dual_launch_links",
        "operator_cockpit_l1.html" in index_text and "operator_cockpit_candidate.html" in index_text,
        "index exposes stable and candidate launch links",
        "index does not expose both launch links",
    )

    missing_ids = [item for item in REQUIRED_ZONE_IDS if f'id="{item}"' not in candidate_text]
    add_check(
        checks,
        warnings,
        blockers,
        "candidate_required_zones",
        not missing_ids,
        "candidate keeps required cockpit zones",
        f"candidate is missing required zone ids: {missing_ids}",
    )

    compression_markers = [
        "grid-template-columns: repeat(8",
        "max-height: 125px",
        "overflow: auto",
        "track-badge",
    ]
    missing_markers = [item for item in compression_markers if item not in candidate_css_text]
    add_check(
        checks,
        warnings,
        blockers,
        "candidate_compression_markers",
        not missing_markers,
        "candidate includes compression-oriented style markers",
        f"candidate compression markers missing: {missing_markers}",
        fail_level="WARN",
    )

    dossier_payload, dossier_err = load_json(research_dossier)
    source_count = 0
    if isinstance(dossier_payload, dict):
        sources = dossier_payload.get("sources")
        if isinstance(sources, list):
            source_count = len(sources)
    add_check(
        checks,
        warnings,
        blockers,
        "research_dossier_exists",
        dossier_payload is not None,
        "research dossier parses",
        f"research dossier missing/invalid ({dossier_err})",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "research_source_count",
        source_count >= 4,
        f"research source count={source_count}",
        f"insufficient research source count={source_count}",
        fail_level="WARN",
    )

    matrix_payload, matrix_err = load_json(screenshot_matrix)
    captures_count = 0
    if isinstance(matrix_payload, dict):
        captures = matrix_payload.get("captures")
        if isinstance(captures, list):
            captures_count = len(captures)
    add_check(
        checks,
        warnings,
        blockers,
        "screenshot_matrix_exists",
        matrix_payload is not None,
        "screenshot matrix parses",
        f"screenshot matrix missing/invalid ({matrix_err})",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "screenshot_capture_count",
        captures_count >= 4,
        f"screenshot captures={captures_count}",
        f"expected >=4 captures, got {captures_count}",
    )

    comparison_payload, comparison_err = load_json(comparison_report)
    has_delta = False
    if isinstance(comparison_payload, dict):
        has_delta = bool(comparison_payload.get("candidate_visual_delta_detected", False))
    add_check(
        checks,
        warnings,
        blockers,
        "comparison_report_exists",
        comparison_payload is not None,
        "stable/candidate comparison report parses",
        f"comparison report missing/invalid ({comparison_err})",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "candidate_visual_delta",
        has_delta,
        "candidate visual delta detected",
        "candidate visual delta not detected in comparison report",
    )

    l1_validator = repo_root / f"{BASE_REL}/TOOLS/operator_cockpit_l1_validator.py"
    l1_cmd = [
        "python",
        str(l1_validator),
        "--repo-root",
        str(repo_root),
        "--task-id",
        str(args.task_id),
        "--report-dir",
        str(report_dir),
        "--output",
        str(report_dir / "operator_cockpit_l1_validator_report.json"),
    ]
    rc, out, err = run_command(l1_cmd, repo_root)
    l1_report = report_dir / "operator_cockpit_l1_validator_report.json"
    l1_payload, _ = load_json(l1_report)
    l1_verdict = "UNKNOWN"
    if isinstance(l1_payload, dict):
        l1_verdict = str(l1_payload.get("verdict", "UNKNOWN")).upper()
    l1_ok = rc == 0 and l1_verdict in {"PASS", "WARN"}
    add_check(
        checks,
        warnings,
        blockers,
        "base_l1_validator",
        l1_ok,
        f"base l1 validator verdict={l1_verdict}",
        f"base l1 validator failed (rc={rc}, verdict={l1_verdict}, stderr={err})",
    )

    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"
    else:
        verdict = "PASS"

    report = {
        "schema_id": "OPERATOR_COCKPIT_STABLE_CANDIDATE_VALIDATOR_REPORT_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "l1_validator_stdout": out,
        "l1_validator_stderr": err,
        "claim_boundary": "IMPROVED_PC_OPERATOR_SHELL_ONLY",
    }
    write_json(output, report)

    print(f"operator_cockpit_sc_validator_verdict={verdict}")
    print(f"operator_cockpit_sc_validator_report={rel(output, repo_root)}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
