#!/usr/bin/env python3
"""Validate Operator Cockpit L1 artifacts and no-fake-green boundaries."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-OPERATOR-COCKPIT-L1-OWNER-POWER-PC-V0_1"
BASE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/OPERATOR_COCKPIT"

REQUIRED_ACTION_LABELS = {
    "Refresh Truth",
    "Validate Truth",
    "Build Continuity Pack",
    "Open Evidence",
    "Show Diff",
    "Open Dev Preview",
    "Send Taskpack to VM2/VM3",
    "Fetch Report Bundle",
    "Owner Decision / Answer Question",
}

ALLOWED_ACTION_STATUSES = {
    "WIRED",
    "DRY_RUN_ONLY",
    "STUB",
    "PREVIEW_ONLY",
    "BLOCKED",
    "NEEDS_ROUTE_PROOF",
    "NEEDS_OWNER_CONFIRMATION",
}

FORBIDDEN_UI_PATTERNS = [
    "bootstrap",
    "container-fluid",
    "navbar",
    "card card-body",
    "bg-light",
    "terminal_primary_view",
]

REQUIRED_UI_MARKERS = [
    "focus-core",
    "gateway-map",
    "warning-lamp",
    "evidence-stars",
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
    parser = argparse.ArgumentParser(description="Validate operator cockpit L1 artifacts.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument(
        "--state-path",
        type=Path,
        default=default_repo_root / f"{BASE_REL}/DATA/operator_cockpit_l1_state.generated.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=default_report_dir / "operator_cockpit_l1_validator_report.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    report_dir = args.report_dir.resolve()
    state_path = args.state_path.resolve()
    output = args.output.resolve()

    checks: list[dict[str, str]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    core_files = [
        state_path,
        repo_root / f"{BASE_REL}/CONTRACTS/operator_cockpit_l1_state.schema.json",
        repo_root / f"{BASE_REL}/TOOLS/operator_cockpit_l1_builder.py",
        repo_root / f"{BASE_REL}/TOOLS/operator_cockpit_l1_validator.py",
        repo_root / f"{BASE_REL}/TOOLS/operator_cockpit_l1_smoke.py",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.html",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.css",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.js",
    ]
    add_check(
        checks,
        warnings,
        blockers,
        "core_files_exist",
        all(path.exists() for path in core_files),
        "core cockpit files exist",
        "one or more core cockpit files are missing",
    )

    state, state_err = load_json(state_path)
    add_check(
        checks,
        warnings,
        blockers,
        "state_parse",
        state is not None,
        "state file parses",
        f"state parse failed ({state_err})",
    )
    if state is None:
        verdict = "BLOCK"
        report = {
            "schema_id": "OPERATOR_COCKPIT_L1_VALIDATOR_REPORT_V0_1",
            "task_id": str(args.task_id),
            "generated_at_utc": utc_now(),
            "verdict": verdict,
            "checks": checks,
            "warnings": warnings,
            "blockers": blockers,
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"operator_cockpit_validator_verdict={verdict}")
        print(f"operator_cockpit_validator_report={output.relative_to(repo_root).as_posix()}")
        return 1

    add_check(
        checks,
        warnings,
        blockers,
        "schema_id",
        str(state.get("schema_id")) == "OPERATOR_COCKPIT_L1_STATE_V0_1",
        "state schema_id is OPERATOR_COCKPIT_L1_STATE_V0_1",
        f"unexpected schema_id: {state.get('schema_id')}",
    )

    claim_boundary = str(state.get("claim_boundary", ""))
    add_check(
        checks,
        warnings,
        blockers,
        "claim_boundary",
        claim_boundary == "READ_ONLY_OWNER_COCKPIT_L1",
        "claim boundary is read-only L1",
        f"unexpected claim boundary: {claim_boundary}",
    )

    five_truth = state.get("five_second_truth", {})
    required_truth_fields = [
        "active_task",
        "who_is_working",
        "contour",
        "current_blocker",
        "next_action",
        "repo_clean",
        "evidence_confidence",
    ]
    truth_ok = isinstance(five_truth, dict) and all(str(five_truth.get(key, "")).strip() for key in required_truth_fields)
    add_check(
        checks,
        warnings,
        blockers,
        "five_second_truth_fields",
        truth_ok,
        "5-second truth fields are populated",
        "missing one or more 5-second truth fields",
    )

    repo_block = state.get("repo", {})
    repo_ok = isinstance(repo_block, dict) and "head" in repo_block and "branch" in repo_block and "worktree" in repo_block
    add_check(
        checks,
        warnings,
        blockers,
        "repo_truth_block_present",
        repo_ok,
        "repo truth block exists",
        "repo truth block is missing required fields",
    )

    transfer = state.get("transfer_routes", {})
    route_commit = str(transfer.get("route_proof_commit", ""))
    add_check(
        checks,
        warnings,
        blockers,
        "route_commit_reference",
        route_commit == "f00053012c5f4110a4a75423be8236fce1a5baa4",
        "route proof commit is referenced",
        f"route proof commit mismatch: {route_commit}",
        fail_level="WARN",
    )

    actions = state.get("actions", [])
    labels = {str(item.get("label", "")) for item in actions if isinstance(item, dict)}
    add_check(
        checks,
        warnings,
        blockers,
        "action_strip_labels",
        REQUIRED_ACTION_LABELS.issubset(labels),
        "all required action labels are present",
        f"missing action labels: {sorted(REQUIRED_ACTION_LABELS - labels)}",
    )

    invalid_statuses: list[str] = []
    active_without_backend: list[str] = []
    for item in actions:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label", "UNKNOWN"))
        status = str(item.get("status", "UNKNOWN"))
        if status not in ALLOWED_ACTION_STATUSES:
            invalid_statuses.append(f"{label}:{status}")
        if status in {"WIRED", "DRY_RUN_ONLY"}:
            backend_action_id = item.get("backend_action_id")
            receipt_mode = str(item.get("request_result_receipt_mode", ""))
            if not isinstance(backend_action_id, str) or not backend_action_id.strip() or "RECEIPT" not in receipt_mode:
                active_without_backend.append(label)

    add_check(
        checks,
        warnings,
        blockers,
        "action_status_values",
        not invalid_statuses,
        "action statuses use allowed label set",
        f"invalid action statuses: {invalid_statuses}",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "active_actions_have_receipt_mode",
        not active_without_backend,
        "active WIRED/DRY_RUN_ONLY actions include backend and receipt mode",
        f"active actions missing backend/receipt mode: {active_without_backend}",
    )

    continuity = state.get("continuity", {})
    dev_preview = state.get("development_preview", {})
    continuity_ok = isinstance(continuity, dict) and "small_mode" in continuity and "latest_pack_ref" in continuity
    preview_ok = isinstance(dev_preview, dict) and "status" in dev_preview and "reason" in dev_preview
    add_check(
        checks,
        warnings,
        blockers,
        "continuity_panel_present",
        continuity_ok,
        "continuity panel state is present",
        "continuity panel state is missing",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "development_preview_panel_present",
        preview_ok,
        "development preview panel state is present",
        "development preview panel state is missing",
    )

    evidence_diff = state.get("evidence_diff", {})
    changed_count = int(evidence_diff.get("changed_files_count", -1)) if isinstance(evidence_diff, dict) else -1
    add_check(
        checks,
        warnings,
        blockers,
        "evidence_diff_panel_present",
        isinstance(evidence_diff, dict) and changed_count >= 0,
        "evidence/diff panel state is present",
        "evidence/diff panel is missing",
    )

    html_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.html"
    css_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.css"
    js_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.js"
    html_text = html_path.read_text(encoding="utf-8") if html_path.exists() else ""
    css_text = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
    js_text = js_path.read_text(encoding="utf-8") if js_path.exists() else ""

    marker_missing = [marker for marker in REQUIRED_UI_MARKERS if marker not in html_text and marker not in css_text]
    add_check(
        checks,
        warnings,
        blockers,
        "visual_identity_markers",
        not marker_missing,
        "visual identity markers are present",
        f"missing visual markers: {marker_missing}",
        fail_level="WARN",
    )

    forbidden_hits = [pattern for pattern in FORBIDDEN_UI_PATTERNS if pattern in html_text.lower() or pattern in css_text.lower()]
    add_check(
        checks,
        warnings,
        blockers,
        "forbidden_dashboard_patterns_absent",
        not forbidden_hits,
        "no forbidden generic dashboard patterns found",
        f"forbidden patterns found: {forbidden_hits}",
    )

    dark_theme_ok = "background" in css_text and "#0" in css_text
    add_check(
        checks,
        warnings,
        blockers,
        "dark_cockpit_theme_present",
        dark_theme_ok,
        "dark cockpit theme markers are present",
        "dark cockpit markers are missing or too weak",
        fail_level="WARN",
    )

    bilingual_ok = "lang-toggle" in html_text and "I18N" in js_text
    add_check(
        checks,
        warnings,
        blockers,
        "bilingual_ui_switch_present",
        bilingual_ok,
        "RU/EN switch markers are present",
        "bilingual switch markers are missing",
    )

    screenshot_dir = report_dir / "SCREENSHOTS"
    screenshot_files = sorted(screenshot_dir.glob("*.png")) if screenshot_dir.exists() else []
    add_check(
        checks,
        warnings,
        blockers,
        "screenshot_evidence_present",
        len(screenshot_files) >= 4,
        f"screenshot evidence count={len(screenshot_files)}",
        f"screenshot evidence is insufficient (count={len(screenshot_files)})",
        fail_level="WARN",
    )

    not_proven = state.get("forbidden_claims", [])
    required_not_proven = {
        "live execution",
        "production orchestration",
        "final luxury visual quality",
        "full organ intelligence",
        "autonomous multi-contour operation",
    }
    not_proven_ok = isinstance(not_proven, list) and required_not_proven.issubset({str(item) for item in not_proven})
    add_check(
        checks,
        warnings,
        blockers,
        "not_proven_boundary_present",
        not_proven_ok,
        "required not_proven boundaries are present",
        "required not_proven boundaries are missing",
    )

    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"
    else:
        verdict = "PASS"

    report = {
        "schema_id": "OPERATOR_COCKPIT_L1_VALIDATOR_REPORT_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "claim_boundary": "READ_ONLY_OWNER_COCKPIT_L1",
        "no_fake_green_note": "Active actions require receipt mode and backend action binding.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"operator_cockpit_validator_verdict={verdict}")
    print(f"operator_cockpit_validator_report={output.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
