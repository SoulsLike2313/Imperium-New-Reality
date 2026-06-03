#!/usr/bin/env python3
"""Validate Sanctum NG Transfer Console foundation artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-TRANSFER-CONSOLE-VM3-V0_1"
BASE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE"

FORBIDDEN_FIELDS = {
    "command",
    "shell",
    "exec",
    "powershell",
    "bash",
    "cmd",
    "arbitrary_command",
    "remote_command",
}

REQUIRED_CONTOURS = {"PC", "VM2", "VM3"}


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


def list_json(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for item in sorted(path.glob("*.json")):
        payload, _err = load_json(item)
        if payload is not None:
            payload["_path"] = item
            out.append(payload)
    return out


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
    parser = argparse.ArgumentParser(description="Validate transfer console artifacts.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output", type=Path, default=default_report_dir / "transfer_console_validator_report.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    report_dir = args.report_dir.resolve()
    output = args.output.resolve()

    checks: list[dict[str, str]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    core_files = [
        repo_root / f"{BASE_REL}/TOOLS/transfer_console_action_runner_v0_1.py",
        repo_root / f"{BASE_REL}/TOOLS/validate_transfer_console_v0_1.py",
        repo_root / f"{BASE_REL}/TOOLS/smoke_transfer_console_v0_1.py",
        repo_root / f"{BASE_REL}/CONTRACTS/transfer_contour_record_v0_1.schema.json",
        repo_root / f"{BASE_REL}/CONTRACTS/transfer_route_definition_v0_1.schema.json",
        repo_root / f"{BASE_REL}/CONTRACTS/transfer_request_record_v0_1.schema.json",
        repo_root / f"{BASE_REL}/CONTRACTS/transfer_result_record_v0_1.schema.json",
        repo_root / f"{BASE_REL}/CONTRACTS/transfer_action_ledger_entry_v0_1.schema.json",
        repo_root / f"{BASE_REL}/CONTRACTS/transfer_console_view_state_v0_1.schema.json",
        repo_root / f"{BASE_REL}/DATA/contours/contour_registry_v0_1.json",
        repo_root / f"{BASE_REL}/DATA/contours/allowed_routes_v0_1.json",
        repo_root / f"{BASE_REL}/DATA/contours/contour_status.latest.json",
        repo_root / f"{BASE_REL}/DATA/TRANSFER_CONSOLE_VIEW_STATE.generated.json",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/index.html",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/app.js",
    ]

    add_check(
        checks,
        warnings,
        blockers,
        "core_files_exist",
        all(path.exists() for path in core_files),
        "all transfer console core files exist",
        "one or more transfer console core files are missing",
    )

    contour_status_path = repo_root / f"{BASE_REL}/DATA/contours/contour_status.latest.json"
    contour_status, contour_status_err = load_json(contour_status_path)
    add_check(
        checks,
        warnings,
        blockers,
        "contour_status_parse",
        contour_status is not None,
        "contour status parses",
        f"contour status parse failed ({contour_status_err})",
    )

    contours: list[dict[str, Any]] = []
    if contour_status is not None:
        raw_contours = contour_status.get("contours", [])
        if isinstance(raw_contours, list):
            contours = [item for item in raw_contours if isinstance(item, dict)]

    contour_ids = {str(item.get("contour_id", "")).upper() for item in contours}
    add_check(
        checks,
        warnings,
        blockers,
        "required_contours_present",
        REQUIRED_CONTOURS.issubset(contour_ids),
        "PC/VM2/VM3 contour cards are present",
        f"missing required contours: {sorted(REQUIRED_CONTOURS - contour_ids)}",
    )

    online_without_receipt: list[str] = []
    for contour in contours:
        status = str(contour.get("status", ""))
        receipt_ref = contour.get("last_probe_receipt_ref")
        contour_id = str(contour.get("contour_id", "UNKNOWN"))
        if status == "ONLINE":
            if not isinstance(receipt_ref, str) or not receipt_ref.strip() or not (repo_root / receipt_ref).exists():
                online_without_receipt.append(contour_id)

    add_check(
        checks,
        warnings,
        blockers,
        "online_requires_probe_receipt",
        not online_without_receipt,
        "ONLINE statuses have bounded probe receipts",
        f"ONLINE without receipt: {online_without_receipt}",
    )

    request_records = list_json(repo_root / f"{BASE_REL}/DATA/requests")
    result_records = list_json(repo_root / f"{BASE_REL}/DATA/results")

    add_check(
        checks,
        warnings,
        blockers,
        "request_records_exist",
        len(request_records) > 0,
        f"request records present ({len(request_records)})",
        "no transfer request records found",
        fail_level="WARN",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "result_records_exist",
        len(result_records) > 0,
        f"result records present ({len(result_records)})",
        "no transfer result records found",
        fail_level="WARN",
    )

    forbidden_hits: list[str] = []
    sent_without_result: list[str] = []

    results_by_request_id = {
        str(item.get("request_id", "")): item for item in result_records if str(item.get("request_id", "")).strip()
    }

    for request in request_records:
        req_id = str(request.get("request_id", "UNKNOWN"))
        bad_keys = sorted([key for key in request.keys() if key in FORBIDDEN_FIELDS])
        if bad_keys:
            forbidden_hits.append(f"{req_id}:{','.join(bad_keys)}")

        req_status = str(request.get("status", ""))
        if req_status in {"SENT", "FETCHED"}:
            result = results_by_request_id.get(req_id)
            if result is None:
                sent_without_result.append(req_id)

    add_check(
        checks,
        warnings,
        blockers,
        "no_forbidden_request_fields",
        not forbidden_hits,
        "no forbidden shell/exec request fields found",
        f"forbidden request fields detected: {forbidden_hits}",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "no_sent_fetched_without_result",
        not sent_without_result,
        "SENT/FETCHED request states are backed by result records",
        f"SENT/FETCHED request states missing result records: {sent_without_result}",
    )

    fake_green_hits: list[str] = []
    for result in result_records:
        status = str(result.get("status", ""))
        result_id = str(result.get("result_id", "UNKNOWN"))
        evidence = result.get("evidence_refs", [])
        if status in {"SENT", "FETCHED"} and (not isinstance(evidence, list) or len(evidence) == 0):
            fake_green_hits.append(result_id)

    add_check(
        checks,
        warnings,
        blockers,
        "sent_fetched_require_evidence_refs",
        not fake_green_hits,
        "SENT/FETCHED result states include evidence refs",
        f"SENT/FETCHED results missing evidence refs: {fake_green_hits}",
    )

    view_state_path = repo_root / f"{BASE_REL}/DATA/TRANSFER_CONSOLE_VIEW_STATE.generated.json"
    view_state, view_state_err = load_json(view_state_path)
    add_check(
        checks,
        warnings,
        blockers,
        "view_state_parse",
        view_state is not None,
        "view state parses",
        f"view state parse failed ({view_state_err})",
    )

    missing_refs: list[str] = []
    source_refs: list[str] = []
    truth_labels: list[str] = []
    if view_state is not None:
        refs_raw = view_state.get("source_refs", [])
        source_refs = [str(item) for item in refs_raw if isinstance(item, str)] if isinstance(refs_raw, list) else []
        for rel in source_refs:
            if not (repo_root / rel).exists():
                missing_refs.append(rel)

        labels_raw = view_state.get("truth_labels", [])
        truth_labels = [str(item) for item in labels_raw if isinstance(item, str)] if isinstance(labels_raw, list) else []

        mix = view_state.get("context_source_mix", {})
        mix_ok = (
            isinstance(mix, dict)
            and "taskpack_percent" in mix
            and "existing_newgen_repo_percent" in mix
            and "owner_handoff_percent" in mix
            and "organ_registry_percent" in mix
            and "servitor_inference_percent" in mix
            and "external_local_private_percent" in mix
        )
        add_check(
            checks,
            warnings,
            blockers,
            "context_source_mix_present",
            mix_ok,
            "context source mix block exists in view state",
            "context source mix block is missing in view state",
        )

    add_check(
        checks,
        warnings,
        blockers,
        "view_state_source_refs_exist",
        not missing_refs,
        "all view-state source refs exist",
        f"missing view-state source refs: {missing_refs}",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "foundation_boundary_labels_visible",
        "FOUNDATION_ONLY" in truth_labels and "NO_PRODUCTION_REMOTE_ORCHESTRATION" in truth_labels,
        "FOUNDATION_ONLY and no-production labels are visible",
        "missing FOUNDATION_ONLY or no-production label in view state",
    )

    index_html = (repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/index.html").read_text(encoding="utf-8")
    app_js = (repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/app.js").read_text(encoding="utf-8")

    add_check(
        checks,
        warnings,
        blockers,
        "ui_transfer_console_visible",
        "Transfer Console" in index_html and "transfer-console" in index_html,
        "Transfer Console panel is present in Sanctum NG UI",
        "Transfer Console panel is missing in Sanctum NG UI",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "ui_transfer_console_render_logic",
        "renderTransferConsole" in app_js and "transferConsoleView" in app_js,
        "Transfer Console render logic exists in app.js",
        "Transfer Console render logic is missing in app.js",
    )

    report_files = [
        report_dir / "start_state.json",
        report_dir / "implementation_manifest.json",
        report_dir / "transfer_console_build_report.json",
        report_dir / "transfer_console_smoke_report.json",
        report_dir / "context_source_mix.json",
        report_dir / "FINAL_REPORT.md",
        report_dir / "GATE_ACK.md",
    ]
    add_check(
        checks,
        warnings,
        blockers,
        "report_bundle_progress",
        all(path.exists() for path in report_files),
        "report bundle core files are present",
        "one or more report bundle core files are missing",
        fail_level="WARN",
    )

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report = {
        "schema_id": "TRANSFER_CONSOLE_VALIDATOR_REPORT_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "no_fake_green_note": "Validation is bounded to foundation-only transfer records and explicit evidence constraints.",
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"transfer_console_validator_verdict={verdict}")
    print(f"transfer_console_validator_report={output.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
