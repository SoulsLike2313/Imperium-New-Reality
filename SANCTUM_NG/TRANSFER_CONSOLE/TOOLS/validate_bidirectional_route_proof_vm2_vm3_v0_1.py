#!/usr/bin/env python3
"""Validate bidirectional VM2<->VM3 bounded route-proof artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-TRANSFER-BIDIRECTIONAL-ROUTE-PROOF-VM2-V0_1"
BASE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE"
REPORT_DIR_REL = f"{BASE_REL}/REPORTS/{TASK_ID_DEFAULT}"
SUMMARY_REL = f"{REPORT_DIR_REL}/bidirectional_route_probe_report.json"
OUTPUT_REL = f"{REPORT_DIR_REL}/bidirectional_route_proof_validator_report.json"
VIEW_STATE_REL = f"{BASE_REL}/DATA/TRANSFER_CONSOLE_VIEW_STATE.generated.json"
RUNNER_LEDGER_REL = f"{BASE_REL}/DATA/ledgers/transfer_action_runner_ledger.jsonl"
MATRIX_REL = "IMPERIUM_NEW_GENERATION/MECHANICUS/CONNECTIONS/SSH_CONNECTION_MATRIX_V0_1.json"
MECHANICUS_ROUTE_PROOF_REL = (
    "IMPERIUM_NEW_GENERATION/MECHANICUS/CONNECTIONS/VM2_VM3_BIDIRECTIONAL_ROUTE_PROOF_V0_1.json"
)

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

REQUIRED_ROUTES = ["VM2_TO_VM3", "VM3_TO_VM2"]
REQUIRED_MATRIX_IDS = ["VM2_TO_VM3_ALIAS_BOUNDED_ROUTE", "VM3_TO_VM2_ALIAS_BOUNDED_ROUTE"]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "missing"
    except json.JSONDecodeError as exc:
        return None, f"json_decode_error:{exc}"
    return (payload, None) if isinstance(payload, dict) else (None, "not_json_object")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


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


def resolve_path(repo_root: Path, ref: str) -> Path:
    path = Path(ref)
    if path.is_absolute():
        return path
    return (repo_root / ref).resolve()


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[4]

    parser = argparse.ArgumentParser(description="Validate bidirectional VM2/VM3 route-proof artifacts.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--summary", type=Path, default=default_repo_root / SUMMARY_REL)
    parser.add_argument("--output", type=Path, default=default_repo_root / OUTPUT_REL)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    summary_path = args.summary.resolve()
    output_path = args.output.resolve()

    checks: list[dict[str, str]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    summary, summary_err = load_json(summary_path)
    add_check(
        checks,
        warnings,
        blockers,
        "summary_exists",
        summary is not None,
        "bidirectional route probe report exists and parses",
        f"summary missing or invalid ({summary_err})",
    )

    if summary is None:
        report = {
            "schema_id": "BIDIRECTIONAL_ROUTE_PROOF_VALIDATOR_REPORT_V0_1",
            "task_id": str(args.task_id),
            "generated_at_utc": utc_now(),
            "verdict": "BLOCK",
            "allowed_final_verdict": "BLOCK_ROUTE_PROOF_FAILED",
            "checks": checks,
            "warnings": warnings,
            "blockers": blockers,
            "claim_boundary": "FOUNDATION_ONLY",
            "not_proven": [
                "production orchestration",
                "arbitrary remote shell",
            ],
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("bidirectional_route_proof_validator_verdict=BLOCK")
        print(f"bidirectional_route_proof_validator_report={output_path.relative_to(repo_root).as_posix()}")
        return 1

    routes = summary.get("routes", [])
    route_map: dict[str, dict[str, Any]] = {}
    if isinstance(routes, list):
        for item in routes:
            if isinstance(item, dict):
                route_map[str(item.get("route", ""))] = item

    missing_routes = [route for route in REQUIRED_ROUTES if route not in route_map]
    add_check(
        checks,
        warnings,
        blockers,
        "required_routes_present",
        not missing_routes,
        "required VM2<->VM3 route entries are present",
        f"missing routes: {missing_routes}",
    )

    proved_count = 0
    for route in REQUIRED_ROUTES:
        status = str(route_map.get(route, {}).get("status", ""))
        if status == "PROVED":
            proved_count += 1
        add_check(
            checks,
            warnings,
            blockers,
            f"route_{route.lower()}_proved",
            status == "PROVED",
            f"{route} status is PROVED",
            f"{route} status is {status}",
            fail_level="WARN" if status else "BLOCK",
        )

    add_check(
        checks,
        warnings,
        blockers,
        "both_routes_proved_for_full_pass",
        proved_count == 2,
        "both routes are proved",
        f"proved routes count is {proved_count} of 2",
        fail_level="WARN" if proved_count == 1 else "BLOCK",
    )

    # Probe refs parse and hash/size match
    probe_refs = summary.get("probe_result_refs", [])
    probe_list = [str(item) for item in probe_refs] if isinstance(probe_refs, list) else []
    add_check(
        checks,
        warnings,
        blockers,
        "probe_refs_count",
        len(probe_list) >= 2,
        "probe refs include both routes",
        f"probe refs count is {len(probe_list)}",
    )

    probe_payloads: list[dict[str, Any]] = []
    for ref in probe_list:
        payload, _ = load_json(resolve_path(repo_root, ref))
        if payload is not None:
            probe_payloads.append(payload)

    add_check(
        checks,
        warnings,
        blockers,
        "probe_payloads_parse",
        len(probe_payloads) == len(probe_list),
        "all probe refs parse as JSON objects",
        f"parsed probes {len(probe_payloads)} of {len(probe_list)}",
    )

    for payload in probe_payloads:
        route = str(payload.get("route", "UNKNOWN"))
        hash_size_match = payload.get("hash_size_match") is True
        status_ok = str(payload.get("status", "")) == "PROVED"
        add_check(
            checks,
            warnings,
            blockers,
            f"probe_{route.lower()}_hash_size_match",
            hash_size_match,
            f"{route} hash/size match is true",
            f"{route} hash/size match is false",
            fail_level="WARN",
        )
        add_check(
            checks,
            warnings,
            blockers,
            f"probe_{route.lower()}_status_proved",
            status_ok,
            f"{route} probe status is PROVED",
            f"{route} probe status is {payload.get('status')}",
            fail_level="WARN",
        )

    # Auth checks
    auth_checks = summary.get("auth_checks", {})
    auth_map = auth_checks if isinstance(auth_checks, dict) else {}
    for route in REQUIRED_ROUTES:
        row = auth_map.get(route, {}) if isinstance(auth_map.get(route, {}), dict) else {}
        status = str(row.get("status", ""))
        path_ref = str(row.get("path", ""))
        path_obj = resolve_path(repo_root, path_ref) if path_ref else Path("")
        add_check(
            checks,
            warnings,
            blockers,
            f"auth_{route.lower()}_status",
            status == "PASS",
            f"{route} auth log status is PASS",
            f"{route} auth log status is {status}",
        )
        add_check(
            checks,
            warnings,
            blockers,
            f"auth_{route.lower()}_path_exists",
            bool(path_ref) and path_obj.exists(),
            f"{route} auth log path exists",
            f"{route} auth log path missing: {path_ref}",
        )

    # Request/result refs parse and include no forbidden fields.
    req_refs = summary.get("request_refs", [])
    res_refs = summary.get("result_refs", [])
    req_list = [str(item) for item in req_refs] if isinstance(req_refs, list) else []
    res_list = [str(item) for item in res_refs] if isinstance(res_refs, list) else []
    add_check(
        checks,
        warnings,
        blockers,
        "request_refs_count",
        len(req_list) >= 2,
        "request refs include two route entries",
        f"request refs count is {len(req_list)}",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "result_refs_count",
        len(res_list) >= 2,
        "result refs include two route entries",
        f"result refs count is {len(res_list)}",
    )

    request_payloads: list[dict[str, Any]] = []
    result_payloads: list[dict[str, Any]] = []
    for ref in req_list:
        payload, _ = load_json(resolve_path(repo_root, ref))
        if payload is not None:
            request_payloads.append(payload)
    for ref in res_list:
        payload, _ = load_json(resolve_path(repo_root, ref))
        if payload is not None:
            result_payloads.append(payload)

    add_check(
        checks,
        warnings,
        blockers,
        "request_payloads_parse",
        len(request_payloads) == len(req_list),
        "all request refs parse as JSON",
        f"parsed request payloads {len(request_payloads)} of {len(req_list)}",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "result_payloads_parse",
        len(result_payloads) == len(res_list),
        "all result refs parse as JSON",
        f"parsed result payloads {len(result_payloads)} of {len(res_list)}",
    )

    req_forbidden = sorted({field for payload in request_payloads for field in payload if field in FORBIDDEN_FIELDS})
    res_forbidden = sorted({field for payload in result_payloads for field in payload if field in FORBIDDEN_FIELDS})
    add_check(
        checks,
        warnings,
        blockers,
        "request_no_forbidden_fields",
        not req_forbidden,
        "request payloads contain no forbidden shell fields",
        f"forbidden request fields detected: {req_forbidden}",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "result_no_forbidden_fields",
        not res_forbidden,
        "result payloads contain no forbidden shell fields",
        f"forbidden result fields detected: {res_forbidden}",
    )

    # Runner ledger contains both route entries linked by summary request refs.
    ledger_rows = load_jsonl(repo_root / RUNNER_LEDGER_REL)
    summary_request_ref_set = set(req_list)
    task_rows = [row for row in ledger_rows if str(row.get("request_ref", "")) in summary_request_ref_set]
    route_seen: set[str] = set()
    for row in task_rows:
        route_seen.add(str(row.get("route", "")))

    add_check(
        checks,
        warnings,
        blockers,
        "runner_ledger_routes_present",
        all(route in route_seen for route in REQUIRED_ROUTES),
        "runner ledger contains both route entries for current task",
        f"runner ledger missing route entries: {[route for route in REQUIRED_ROUTES if route not in route_seen]}",
    )

    # View state routes match summary routes.
    view_payload, view_err = load_json(repo_root / VIEW_STATE_REL)
    add_check(
        checks,
        warnings,
        blockers,
        "view_state_exists",
        view_payload is not None,
        "transfer console view state exists",
        f"view state missing/invalid ({view_err})",
    )
    if view_payload is not None:
        transfer_routes = view_payload.get("transfer_routes", [])
        view_route_map: dict[str, str] = {}
        if isinstance(transfer_routes, list):
            for row in transfer_routes:
                if isinstance(row, dict):
                    view_route_map[str(row.get("route_id", ""))] = str(row.get("route_status", ""))

        for route in REQUIRED_ROUTES:
            expected = str(route_map.get(route, {}).get("status", ""))
            actual = view_route_map.get(route)
            add_check(
                checks,
                warnings,
                blockers,
                f"view_state_{route.lower()}_matches",
                actual == expected,
                f"view state {route} matches summary status",
                f"view state {route} status mismatch actual={actual} expected={expected}",
            )

    # Mechanicus matrix and dedicated route proof record.
    matrix_payload, matrix_err = load_json(repo_root / MATRIX_REL)
    add_check(
        checks,
        warnings,
        blockers,
        "mechanicus_matrix_exists",
        matrix_payload is not None,
        "mechanicus matrix exists and parses",
        f"mechanicus matrix missing/invalid ({matrix_err})",
    )
    if matrix_payload is not None:
        connection_rows = matrix_payload.get("connections", [])
        by_id = {
            str(row.get("connection_id", "")): row
            for row in connection_rows
            if isinstance(row, dict)
        }
        missing_ids = [cid for cid in REQUIRED_MATRIX_IDS if cid not in by_id]
        add_check(
            checks,
            warnings,
            blockers,
            "matrix_route_ids_present",
            not missing_ids,
            "matrix includes bidirectional route connection ids",
            f"matrix missing route ids: {missing_ids}",
        )
        for cid in REQUIRED_MATRIX_IDS:
            row = by_id.get(cid, {})
            add_check(
                checks,
                warnings,
                blockers,
                f"matrix_{cid.lower()}_live_verified",
                bool(row.get("live_verified") is True),
                f"{cid} is marked live_verified=true",
                f"{cid} live_verified is {row.get('live_verified')}",
                fail_level="WARN",
            )

    route_proof_payload, route_proof_err = load_json(repo_root / MECHANICUS_ROUTE_PROOF_REL)
    add_check(
        checks,
        warnings,
        blockers,
        "mechanicus_route_proof_record_exists",
        route_proof_payload is not None,
        "mechanicus bidirectional route proof record exists",
        f"mechanicus route proof record missing/invalid ({route_proof_err})",
    )

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report = {
        "schema_id": "BIDIRECTIONAL_ROUTE_PROOF_VALIDATOR_REPORT_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "allowed_final_verdict": str(summary.get("verdict_claim", "BLOCK_ROUTE_PROOF_FAILED")),
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "refs": {
            "summary_ref": summary_path.as_posix(),
            "view_state_ref": VIEW_STATE_REL,
            "runner_ledger_ref": RUNNER_LEDGER_REL,
            "mechanicus_matrix_ref": MATRIX_REL,
            "mechanicus_route_proof_ref": MECHANICUS_ROUTE_PROOF_REL,
        },
        "claim_boundary": "FOUNDATION_ONLY",
        "not_proven": [
            "production orchestration",
            "arbitrary remote shell",
            "global all-contour transfer readiness",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"bidirectional_route_proof_validator_verdict={verdict}")
    print(f"bidirectional_route_proof_validator_report={output_path.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
