#!/usr/bin/env python3
"""Smoke-test Sanctum NG file-backed action layer via localhost server."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260522-NEWGEN-SANCTUM-ACTION-LAYER-HARDENING-VM3-V0_1"
REQUIRED_ACTIONS = {
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
SUMMARY_STATE_SET = {"FOUND", "MISSING", "PARTIAL", "NOT_READY", "STALE", "ERROR"}


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


def http_get_json(url: str, timeout: int = 10) -> tuple[int, dict[str, Any] | None, str | None]:
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            code = int(response.status)
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        try:
            raw = exc.read().decode("utf-8")
        except Exception:
            raw = ""
        return int(exc.code), None, raw or str(exc)
    except Exception as exc:
        return 0, None, str(exc)

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return code, None, "invalid_json"
    if not isinstance(payload, dict):
        return code, None, "not_json_object"
    return code, payload, None


def http_post_json(url: str, body: dict[str, Any], timeout: int = 20) -> tuple[int, dict[str, Any] | None, str | None]:
    raw_body = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=raw_body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            code = int(response.status)
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        try:
            raw = exc.read().decode("utf-8")
        except Exception:
            raw = ""
        try:
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                payload = None
        except Exception:
            payload = None
        return int(exc.code), payload, raw or str(exc)
    except Exception as exc:
        return 0, None, str(exc)

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return code, None, "invalid_json"
    if not isinstance(payload, dict):
        return code, None, "not_json_object"
    return code, payload, None


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_report_dir = default_repo_root / (
        "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260522-NEWGEN-SANCTUM-ACTION-LAYER-HARDENING-VM3-V0_1"
    )
    default_output = default_report_dir / "SMOKE_REPORT.json"

    parser = argparse.ArgumentParser(description="Smoke-test Sanctum NG action layer server.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output", type=Path, default=default_output)
    parser.add_argument("--startup-timeout-seconds", type=int, default=30)
    return parser.parse_args()


def run_action(base_url: str, action_id: str) -> tuple[str, dict[str, Any]]:
    body = {
        "requester": "ACTION_LAYER_SMOKE",
        "dry_run": False,
        "input": {"smoke": True},
    }
    code, payload, err = http_post_json(base_url + f"/api/actions/{action_id}", body=body, timeout=240)
    status = str((payload or {}).get("status", "UNKNOWN"))
    result = {
        "action_id": action_id,
        "http_status": code,
        "status": status,
        "result_record_path": (payload or {}).get("result_record_path", "N/A"),
        "output_summary": (payload or {}).get("output_summary", err or ""),
        "payload": payload,
        "error": err,
    }
    return status, result


def add_step(
    steps: list[dict[str, Any]],
    warnings: list[str],
    blockers: list[str],
    step: str,
    status: str,
    details: Any,
    warning_id: str | None = None,
    blocker_id: str | None = None,
) -> None:
    steps.append(
        {
            "step": step,
            "status": status,
            "details": details,
        }
    )
    if status == "WARN" and warning_id:
        warnings.append(warning_id)
    if status == "BLOCK" and blocker_id:
        blockers.append(blocker_id)


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    report_dir = args.report_dir.resolve()
    output_path = args.output.resolve()

    server_script = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TOOLS/sanctum_ng_action_server.py"
    request_schema_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/sanctum_ng_action_request.schema.json"
    result_schema_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/sanctum_ng_action_result.schema.json"
    server_source_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TOOLS/sanctum_ng_action_server.py"
    base_url = f"http://{args.host}:{args.port}"

    smoke_steps: list[dict[str, Any]] = []
    action_results: list[dict[str, Any]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    # Write an initial placeholder so READ_LATEST_REPORT_SUMMARY can classify in-flight smoke honestly.
    report_dir.mkdir(parents=True, exist_ok=True)
    placeholder = {
        "schema_version": "0.1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "verdict": "PENDING",
        "status": "IN_PROGRESS",
        "note": "Placeholder created before smoke execution to avoid false missing-file classification.",
    }
    placeholder_json = json.dumps(placeholder, indent=2, ensure_ascii=False) + "\n"
    output_path.write_text(placeholder_json, encoding="utf-8")
    legacy_output = report_dir / "ACTION_LAYER_SMOKE_REPORT.json"
    if legacy_output.resolve() != output_path.resolve():
        legacy_output.write_text(placeholder_json, encoding="utf-8")

    req_schema, req_schema_err = load_json(request_schema_path)
    req_schema_ok = bool(
        req_schema
        and req_schema.get("title") == "SANCTUM_NG_ACTION_REQUEST_V0_1"
        and "required" in req_schema
    )
    add_step(
        smoke_steps,
        warnings,
        blockers,
        "action_request_schema_valid",
        "PASS" if req_schema_ok else "BLOCK",
        "request schema shape validated" if req_schema_ok else f"request schema invalid ({req_schema_err})",
        blocker_id="request_schema_invalid",
    )

    res_schema, res_schema_err = load_json(result_schema_path)
    result_statuses = []
    if res_schema and isinstance(res_schema.get("properties"), dict):
        status_prop = (res_schema.get("properties") or {}).get("status", {})
        if isinstance(status_prop, dict):
            enum_values = status_prop.get("enum", [])
            if isinstance(enum_values, list):
                result_statuses = [str(item) for item in enum_values]

    res_schema_ok = bool(
        res_schema
        and res_schema.get("title") == "SANCTUM_NG_ACTION_RESULT_V0_1"
        and "PARTIAL" in result_statuses
    )
    add_step(
        smoke_steps,
        warnings,
        blockers,
        "action_result_schema_valid",
        "PASS" if res_schema_ok else "BLOCK",
        (
            "result schema shape validated and PARTIAL status admitted"
            if res_schema_ok
            else f"result schema invalid ({res_schema_err}); enum={result_statuses}"
        ),
        blocker_id="result_schema_invalid",
    )

    server_cmd = [
        "python3",
        str(server_script),
        "--repo-root",
        str(repo_root),
        "--host",
        str(args.host),
        "--port",
        str(args.port),
        "--task-id",
        str(args.task_id),
        "--report-dir",
        str(report_dir),
    ]

    proc = subprocess.Popen(
        server_cmd,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    health_ok = False
    health_payload: dict[str, Any] | None = None
    actions_payload: dict[str, Any] | None = None
    state_payload: dict[str, Any] | None = None

    try:
        start_time = time.time()
        while time.time() - start_time < max(1, args.startup_timeout_seconds):
            code, payload, _err = http_get_json(base_url + "/api/health", timeout=3)
            if code == 200 and payload is not None:
                health_ok = True
                health_payload = payload
                break
            time.sleep(0.5)

        add_step(
            smoke_steps,
            warnings,
            blockers,
            "health_check",
            "PASS" if health_ok else "BLOCK",
            health_payload if health_ok else "server did not become healthy in time",
            blocker_id="server_health_failed",
        )

        if health_ok:
            actions_code, actions_payload, actions_err = http_get_json(base_url + "/api/actions", timeout=10)
            state_code, state_payload, state_err = http_get_json(base_url + "/api/state", timeout=10)

            actions_ok = actions_code == 200 and actions_payload is not None
            state_ok = state_code == 200 and state_payload is not None

            add_step(
                smoke_steps,
                warnings,
                blockers,
                "registry_loads",
                "PASS" if actions_ok else "BLOCK",
                actions_payload if actions_ok else actions_err,
                blocker_id="actions_endpoint_failed",
            )
            add_step(
                smoke_steps,
                warnings,
                blockers,
                "state_endpoint",
                "PASS" if state_ok else "BLOCK",
                state_payload if state_ok else state_err,
                blocker_id="state_endpoint_failed",
            )

            if actions_ok:
                raw_actions = actions_payload.get("actions", [])
                actions = [item for item in raw_actions if isinstance(item, dict)] if isinstance(raw_actions, list) else []
                action_ids = {str(item.get("action_id", "")).strip() for item in actions if str(item.get("action_id", "")).strip()}
                missing_actions = sorted(REQUIRED_ACTIONS - action_ids)
                add_step(
                    smoke_steps,
                    warnings,
                    blockers,
                    "required_actions_present",
                    "PASS" if not missing_actions else "BLOCK",
                    {"missing_actions": missing_actions},
                    blocker_id="required_actions_missing",
                )

            if state_ok:
                truth_flags = (state_payload or {}).get("state", {}).get("truth_flags", {})
                no_prod_claim_ok = (
                    isinstance(truth_flags, dict)
                    and truth_flags.get("production_ready") is False
                    and truth_flags.get("live_backend") is False
                    and truth_flags.get("autonomous_execution") is False
                )
                add_step(
                    smoke_steps,
                    warnings,
                    blockers,
                    "no_production_autonomy_claim",
                    "PASS" if no_prod_claim_ok else "BLOCK",
                    truth_flags if isinstance(truth_flags, dict) else "truth_flags_missing",
                    blocker_id="forbidden_claim_violation",
                )

            for action_id, step_name in [
                ("REFRESH_TRUTH_STATE", "refresh_truth_state"),
                ("VALIDATE_TRUTH_STATE", "validate_truth_state"),
                ("CHECK_CONTOUR_STATUS", "check_contour_status"),
                ("DRY_RUN_TASKPACK_SEND", "dry_run_taskpack_send"),
                ("DRY_RUN_REPORT_FETCH", "dry_run_report_fetch"),
                ("REFRESH_TRANSFER_CONSOLE_VIEW", "refresh_transfer_console_view"),
                ("VALIDATE_TRANSFER_REQUEST", "validate_transfer_request"),
                ("DRY_RUN_TRANSFER", "dry_run_transfer"),
                ("SEND_TASKPACK_ZIP", "send_taskpack_zip"),
                ("FETCH_REPORT_BUNDLE_ZIP", "fetch_report_bundle_zip"),
                ("REGISTER_TRANSFER_RESULT", "register_transfer_result"),
            ]:
                status, result = run_action(base_url, action_id)
                action_results.append(result)
                ok = result["http_status"] == 200 and status in {"PASS", "WARN", "PARTIAL"}
                step_status = "PASS" if ok else "BLOCK"
                add_step(
                    smoke_steps,
                    warnings,
                    blockers,
                    step_name,
                    step_status,
                    {
                        "status": status,
                        "http_status": result["http_status"],
                        "summary": result["output_summary"],
                    },
                    blocker_id=f"{step_name}_failed",
                )

            summary_status, summary_result = run_action(base_url, "READ_LATEST_REPORT_SUMMARY")
            action_results.append(summary_result)
            summary_payload = (summary_result.get("payload") or {}).get("payload", {})
            summary_state = str(summary_payload.get("summary_state", "UNKNOWN"))
            summary_reason = str(summary_payload.get("reason", "UNKNOWN"))

            if summary_result["http_status"] != 200:
                add_step(
                    smoke_steps,
                    warnings,
                    blockers,
                    "read_latest_report_summary",
                    "BLOCK",
                    {
                        "http_status": summary_result["http_status"],
                        "status": summary_status,
                        "summary_state": summary_state,
                        "reason": summary_reason,
                    },
                    blocker_id="read_latest_report_summary_http_failed",
                )
            elif summary_state not in SUMMARY_STATE_SET:
                add_step(
                    smoke_steps,
                    warnings,
                    blockers,
                    "read_latest_report_summary",
                    "BLOCK",
                    {
                        "status": summary_status,
                        "summary_state": summary_state,
                        "reason": "unknown_summary_state",
                    },
                    blocker_id="read_latest_report_summary_unknown_state",
                )
            elif summary_state == "FOUND":
                add_step(
                    smoke_steps,
                    warnings,
                    blockers,
                    "read_latest_report_summary",
                    "PASS",
                    {
                        "status": summary_status,
                        "summary_state": summary_state,
                        "reason": summary_reason,
                    },
                )
            elif summary_state in {"PARTIAL", "NOT_READY", "MISSING", "STALE"}:
                add_step(
                    smoke_steps,
                    warnings,
                    blockers,
                    "read_latest_report_summary",
                    "WARN",
                    {
                        "status": summary_status,
                        "summary_state": summary_state,
                        "reason": summary_reason,
                    },
                    warning_id=f"expected_partial_report_summary:{summary_state}:{summary_reason}",
                )
            else:
                add_step(
                    smoke_steps,
                    warnings,
                    blockers,
                    "read_latest_report_summary",
                    "BLOCK",
                    {
                        "status": summary_status,
                        "summary_state": summary_state,
                        "reason": summary_reason,
                    },
                    blocker_id="read_latest_report_summary_error_state",
                )

            code, _, err = http_post_json(
                base_url + "/api/actions/UNALLOWLISTED_EXEC_TEST",
                {
                    "requester": "ACTION_LAYER_SMOKE",
                    "dry_run": False,
                    "input": {"test": "unallowlisted"},
                },
                timeout=10,
            )
            unallowlisted_blocked = code == 400
            add_step(
                smoke_steps,
                warnings,
                blockers,
                "no_arbitrary_shell_execution",
                "PASS" if unallowlisted_blocked else "BLOCK",
                {
                    "http_status": code,
                    "error": err,
                },
                blocker_id="unallowlisted_action_not_blocked",
            )

            server_source = server_source_path.read_text(encoding="utf-8")
            shell_patterns_safe = "shell=True" not in server_source and "os.system(" not in server_source
            add_step(
                smoke_steps,
                warnings,
                blockers,
                "server_source_shell_safety",
                "PASS" if shell_patterns_safe else "BLOCK",
                "no shell=True and no os.system patterns" if shell_patterns_safe else "forbidden shell pattern found",
                blocker_id="forbidden_shell_pattern_found",
            )

    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=8)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)

    disconn_code, _disconn_payload, disconn_err = http_get_json(
        f"http://{args.host}:{args.port + 59}/api/health",
        timeout=2,
    )
    disconnected_behavior_ok = disconn_code == 0
    add_step(
        smoke_steps,
        warnings,
        blockers,
        "server_disconnected_behavior",
        "PASS" if disconnected_behavior_ok else "WARN",
        (
            "disconnected path detected as unreachable"
            if disconnected_behavior_ok
            else f"unexpected response code from disconnected probe: {disconn_code} ({disconn_err})"
        ),
        warning_id="disconnected_probe_unexpected_response",
    )

    stdout_text = ""
    stderr_text = ""
    if proc.stdout is not None:
        stdout_text = proc.stdout.read().strip()
    if proc.stderr is not None:
        stderr_text = proc.stderr.read().strip()

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        expected_only = all(item.startswith("expected_partial_report_summary:") for item in warnings)
        verdict = "PASS_WITH_EXPECTED_PARTIAL" if expected_only else "WARN"

    report = {
        "schema_version": "0.1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "server": {
            "base_url": base_url,
            "command": server_cmd,
            "returncode": proc.returncode,
        },
        "steps": smoke_steps,
        "action_results": action_results,
        "warnings": warnings,
        "blockers": blockers,
        "server_stdout_tail": stdout_text[-4000:],
        "server_stderr_tail": stderr_text[-4000:],
        "no_fake_green_note": "Smoke validates bounded localhost action layer only; no production/autonomy claim.",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_json = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    output_path.write_text(report_json, encoding="utf-8")

    # Keep legacy filename for compatibility with prior validators/history tooling.
    if legacy_output.resolve() != output_path.resolve():
        legacy_output.write_text(report_json, encoding="utf-8")

    print(f"action_layer_smoke_verdict={verdict}")
    print(f"action_layer_smoke_report={output_path.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "PASS_WITH_EXPECTED_PARTIAL", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
