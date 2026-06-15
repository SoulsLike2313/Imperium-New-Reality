#!/usr/bin/env python3
"""Validate Sanctum NG file-backed action layer foundation artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260522-NEWGEN-SANCTUM-ACTION-LAYER-HARDENING-VM3-V0_1"

REQUIRED_ACTION_IDS = {
    "REFRESH_TRUTH_STATE",
    "VALIDATE_TRUTH_STATE",
    "READ_PHASE_REGISTRY",
    "READ_ACTION_REGISTRY",
    "READ_LATEST_REPORT_SUMMARY",
    "CHECK_CONTOUR_STATUS",
    "REGISTER_TASKPACK_SEND",
    "REGISTER_REPORT_BUNDLE_FETCH",
    "DRY_RUN_TASKPACK_SEND",
    "DRY_RUN_REPORT_FETCH",
    "REFRESH_TRANSFER_CONSOLE_VIEW",
    "SEND_TASKPACK_ZIP",
    "FETCH_REPORT_BUNDLE_ZIP",
    "REGISTER_TRANSFER_RESULT",
    "VALIDATE_TRANSFER_REQUEST",
    "DRY_RUN_TRANSFER",
}

REQUIRED_ACTION_FIELDS = {
    "action_id",
    "title",
    "description",
    "status",
    "safety_level",
    "allowed_commands",
    "allowed_paths",
    "forbidden_paths",
    "writes_files",
    "evidence_refs",
    "known_limitations",
}

STATUS_SET = {"WIRED", "PREVIEW_ONLY", "NOT_WIRED", "BLOCKED"}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "missing"
    except json.JSONDecodeError as exc:
        return None, f"json_decode_error:{exc}"
    if not isinstance(value, dict):
        return None, "not_json_object"
    return value, None


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
    default_repo_root = script_path.parents[3]
    default_report_dir = default_repo_root / (
        "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260522-NEWGEN-SANCTUM-ACTION-LAYER-HARDENING-VM3-V0_1"
    )
    default_output = default_report_dir / "ACTION_LAYER_VALIDATOR_REPORT.json"

    parser = argparse.ArgumentParser(description="Validate Sanctum NG action layer artifacts.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output", type=Path, default=default_output)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    report_dir = args.report_dir.resolve()
    output_path = args.output.resolve()

    checks: list[dict[str, str]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    required_impl_files = [
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/ARCHITECTURE/SANCTUM_NG_FILE_BACKED_ACTION_LAYER_V0_1.md",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/sanctum_ng_action_request.schema.json",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/sanctum_ng_action_result.schema.json",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/sanctum_ng_action_registry.schema.json",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/REGISTRY/SANCTUM_NG_ACTION_REGISTRY_V0_1.json",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TOOLS/sanctum_ng_action_server.py",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TOOLS/sanctum_ng_action_layer_validator.py",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TOOLS/sanctum_ng_action_layer_smoke.py",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/TOOLS/transfer_console_action_runner_v0_1.py",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/TOOLS/transfer_action_runner_v0_1.py",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/TOOLS/build_transfer_action_samples_v0_1.py",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/TOOLS/validate_transfer_action_runner_v0_1.py",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/TOOLS/smoke_transfer_action_runner_v0_1.py",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/CONTRACTS/transfer_action_request.schema.json",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/CONTRACTS/transfer_action_result.schema.json",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/CONTRACTS/transfer_action_runner_policy.schema.json",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/CONTRACTS/transfer_console_view_state_v0_1.schema.json",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/DATA/TRANSFER_CONSOLE_VIEW_STATE.generated.json",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/index.html",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/app.js",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/styles.css",
    ]

    required_report_files = [
        report_dir / "OFFICIO_ROLE_ACK_OR_WARN.json",
        report_dir / "DOCTRINARIUM_LAW_ACK_OR_WARN.json",
        report_dir / "SUPER_SKEPTICISM_ACK.json",
        report_dir / "CONTEXT_WINDOW_USAGE_NOTE.md",
        report_dir / "GATE_ACK.md",
        report_dir / "ACTION_LAYER_HARDENING_REPORT.md",
        report_dir / "ACTION_LAYER_HARDENING_REPORT.json",
        report_dir / "VALIDATOR_REPORT.json",
        report_dir / "SMOKE_REPORT.json",
        report_dir / "FINAL_OWNER_REPORT_RU.md",
        report_dir / "FINAL_RECEIPT.json",
        report_dir / "POST_COMMIT_CLOSURE_RECEIPT.json",
        report_dir / "NEXT_TASK_IMPROVEMENT_REPORT.md",
        report_dir / "NEXT_TASK_IMPROVEMENT_REPORT.json",
        report_dir / "KPD_SLICE.md",
        report_dir / "STEP_PROOF_RECORDS.jsonl",
    ]

    add_check(
        checks,
        warnings,
        blockers,
        "impl_files_exist",
        all(path.exists() for path in required_impl_files),
        "all required implementation files exist",
        "one or more required implementation files are missing",
    )

    req_schema_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/sanctum_ng_action_request.schema.json"
    res_schema_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/sanctum_ng_action_result.schema.json"
    reg_schema_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/sanctum_ng_action_registry.schema.json"
    reg_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/REGISTRY/SANCTUM_NG_ACTION_REGISTRY_V0_1.json"

    req_schema, req_schema_err = load_json(req_schema_path)
    add_check(
        checks,
        warnings,
        blockers,
        "request_schema_parse",
        req_schema is not None,
        "request schema parses",
        f"request schema parse failed ({req_schema_err})",
    )
    req_schema_text = json.dumps(req_schema, ensure_ascii=False) if req_schema is not None else ""
    add_check(
        checks,
        warnings,
        blockers,
        "request_schema_denies_arbitrary_shell_fields",
        all(
            token in req_schema_text
            for token in [
                "command",
                "shell",
                "exec",
                "powershell",
                "bash",
                "cmd",
                "arbitrary_command",
                "remote_command",
            ]
        ),
        "request schema includes deny-list for arbitrary shell/command fields",
        "request schema is missing deny-list tokens for arbitrary shell/command fields",
    )

    res_schema, res_schema_err = load_json(res_schema_path)
    add_check(
        checks,
        warnings,
        blockers,
        "result_schema_parse",
        res_schema is not None,
        "result schema parses",
        f"result schema parse failed ({res_schema_err})",
    )
    result_statuses: list[str] = []
    if res_schema is not None:
        properties = res_schema.get("properties", {})
        if isinstance(properties, dict):
            status_field = properties.get("status", {})
            if isinstance(status_field, dict):
                enum_values = status_field.get("enum", [])
                if isinstance(enum_values, list):
                    result_statuses = [str(item) for item in enum_values]

    add_check(
        checks,
        warnings,
        blockers,
        "result_schema_has_partial",
        "PARTIAL" in result_statuses,
        "result schema includes PARTIAL for explicit expected-partial outcomes",
        f"result schema missing PARTIAL in enum: {result_statuses}",
    )

    reg_schema, reg_schema_err = load_json(reg_schema_path)
    add_check(
        checks,
        warnings,
        blockers,
        "registry_schema_parse",
        reg_schema is not None,
        "registry schema parses",
        f"registry schema parse failed ({reg_schema_err})",
    )

    registry_obj, registry_err = load_json(reg_path)
    add_check(
        checks,
        warnings,
        blockers,
        "action_registry_parse",
        registry_obj is not None,
        "action registry parses",
        f"action registry parse failed ({registry_err})",
    )

    actions: list[dict[str, Any]] = []
    if registry_obj is not None:
        raw_actions = registry_obj.get("actions", [])
        if isinstance(raw_actions, list):
            actions = [item for item in raw_actions if isinstance(item, dict)]

        action_ids = {str(item.get("action_id", "")).strip() for item in actions if str(item.get("action_id", "")).strip()}

        add_check(
            checks,
            warnings,
            blockers,
            "required_actions_present",
            REQUIRED_ACTION_IDS.issubset(action_ids),
            "all required allowlisted actions are present",
            f"missing required action ids: {sorted(REQUIRED_ACTION_IDS - action_ids)}",
        )

        shape_ok = True
        shape_errors: list[str] = []
        status_errors: list[str] = []
        wired_without_command: list[str] = []

        for action in actions:
            aid = str(action.get("action_id", "UNKNOWN"))
            missing_fields = sorted(REQUIRED_ACTION_FIELDS - set(action.keys()))
            if missing_fields:
                shape_ok = False
                shape_errors.append(f"{aid}:missing_fields={missing_fields}")

            status = str(action.get("status", ""))
            if status not in STATUS_SET:
                status_errors.append(f"{aid}:{status}")

            if status == "WIRED":
                cmds = action.get("allowed_commands", [])
                if not isinstance(cmds, list) or not cmds:
                    wired_without_command.append(aid)

        add_check(
            checks,
            warnings,
            blockers,
            "action_field_shape",
            shape_ok,
            "all action entries contain required fields",
            "; ".join(shape_errors) if shape_errors else "shape error",
        )

        add_check(
            checks,
            warnings,
            blockers,
            "action_status_enum",
            not status_errors,
            "all action statuses are valid",
            f"invalid action statuses: {status_errors}",
        )

        add_check(
            checks,
            warnings,
            blockers,
            "wired_actions_have_commands",
            not wired_without_command,
            "all wired actions have non-empty allowed_commands",
            f"wired actions missing command descriptors: {wired_without_command}",
        )

    server_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TOOLS/sanctum_ng_action_server.py"
    server_text = server_path.read_text(encoding="utf-8") if server_path.exists() else ""

    add_check(
        checks,
        warnings,
        blockers,
        "server_routes_present",
        all(token in server_text for token in ["/api/state", "/api/actions", "do_POST", "do_GET"]),
        "server contains required API route handlers",
        "server route handlers are missing",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "localhost_only_default",
        "--host" in server_text and "127.0.0.1" in server_text and "localhost" in server_text,
        "server defaults and checks localhost-only behavior",
        "server localhost-only rule not found",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "no_arbitrary_shell_patterns",
        "shell=True" not in server_text and "os.system(" not in server_text,
        "no arbitrary shell execution pattern found",
        "forbidden shell execution pattern found",
    )

    app_js_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/app.js"
    app_js = app_js_path.read_text(encoding="utf-8") if app_js_path.exists() else ""

    add_check(
        checks,
        warnings,
        blockers,
        "ui_has_connection_states",
        all(token in app_js for token in ["CONNECTED", "NOT_CONNECTED", "UNKNOWN"]),
        "UI includes required connection states",
        "UI connection states are incomplete",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "ui_file_mode_honesty",
        "ACTION_SERVER_NOT_CONNECTED" in app_js,
        "UI includes file mode not-connected signal",
        "UI missing ACTION_SERVER_NOT_CONNECTED guard",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "ui_officio_gate_visible",
        "LIVE_LANGUAGE_COMPLIANCE" in app_js and "communication_gate" in app_js,
        "UI shows Officio live-language gate fields",
        "UI does not visibly bind Officio gate fields",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "ui_action_state_model_visible",
        all(
            token in app_js
            for token in [
                "ACTION_ALLOWED",
                "ACTION_DISABLED",
                "ACTION_RESULT_PASS",
                "ACTION_RESULT_WARN",
                "ACTION_RESULT_BLOCK",
                "ACTION_RESULT_PARTIAL",
            ]
        ),
        "UI includes required action/result state model tokens",
        "UI is missing one or more required action/result state model tokens",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "ui_transfer_console_visible",
        "renderTransferConsole" in app_js and "transferConsoleView" in app_js,
        "UI includes Transfer Console visibility and render wiring",
        "UI is missing Transfer Console visibility or render wiring",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "server_transfer_dispatch_mapped",
        all(
            token in server_text
            for token in [
                "CHECK_CONTOUR_STATUS",
                "REGISTER_TASKPACK_SEND",
                "REGISTER_REPORT_BUNDLE_FETCH",
                "DRY_RUN_TASKPACK_SEND",
                "DRY_RUN_REPORT_FETCH",
                "REFRESH_TRANSFER_CONSOLE_VIEW",
                "SEND_TASKPACK_ZIP",
                "FETCH_REPORT_BUNDLE_ZIP",
                "REGISTER_TRANSFER_RESULT",
                "VALIDATE_TRANSFER_REQUEST",
                "DRY_RUN_TRANSFER",
                "transfer_console_view",
            ]
        ),
        "Server dispatch includes transfer console + transfer action runner allowlisted actions",
        "Server dispatch is missing one or more transfer console/runner allowlisted actions",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "required_report_bundle_exists",
        all(path.exists() for path in required_report_files),
        "required report bundle files exist",
        "one or more required report files are missing",
        fail_level="WARN",
    )

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report = {
        "schema_version": "0.1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "registry_path": reg_path.relative_to(repo_root).as_posix() if reg_path.exists() else str(reg_path),
        "report_dir": report_dir.relative_to(repo_root).as_posix() if report_dir.exists() else str(report_dir),
        "no_fake_green_note": "PASS/WARN validates bounded foundation action layer only; no production/autonomy claim.",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"action_layer_validator_verdict={verdict}")
    print(f"action_layer_validator_report={output_path.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
