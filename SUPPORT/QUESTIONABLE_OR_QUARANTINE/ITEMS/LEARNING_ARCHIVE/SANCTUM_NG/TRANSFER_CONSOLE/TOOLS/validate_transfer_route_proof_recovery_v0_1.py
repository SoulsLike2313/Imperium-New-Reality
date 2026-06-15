#!/usr/bin/env python3
"""Validate scoped transfer route-proof recovery artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-RECOVERY-VM2-V0_1"
BASE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE"
REPORT_DIR_REL = f"{BASE_REL}/REPORTS/{TASK_ID_DEFAULT}"
SUMMARY_REL = f"{REPORT_DIR_REL}/route_proof_recovery_summary.json"
OUTPUT_REL = f"{REPORT_DIR_REL}/transfer_route_proof_validator_report.json"
VIEW_STATE_REL = f"{BASE_REL}/DATA/TRANSFER_CONSOLE_VIEW_STATE.generated.json"
RUNNER_LEDGER_REL = f"{BASE_REL}/DATA/ledgers/transfer_action_runner_ledger.jsonl"

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
    out: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        row = raw.strip()
        if not row:
            continue
        try:
            payload = json.loads(row)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
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
    parser = argparse.ArgumentParser(description="Validate transfer route-proof recovery artifacts.")
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
        "route proof recovery summary exists and parses",
        f"route proof recovery summary missing/invalid ({summary_err})",
    )
    if summary is None:
        report = {
            "schema_id": "TRANSFER_ROUTE_PROOF_VALIDATOR_REPORT_V0_1",
            "task_id": str(args.task_id),
            "generated_at_utc": utc_now(),
            "verdict": "BLOCK",
            "allowed_final_verdict": "BLOCK_PC_TO_VM2_NOT_PROVED",
            "checks": checks,
            "warnings": warnings,
            "blockers": blockers,
            "claim_boundary": "FOUNDATION_ONLY",
            "not_proven": [
                "all routes",
                "production orchestration",
            ],
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("transfer_route_proof_validator_verdict=BLOCK")
        print(f"transfer_route_proof_validator_report={output_path.relative_to(repo_root).as_posix()}")
        return 1

    routes = summary.get("routes", [])
    route_map: dict[str, dict[str, Any]] = {}
    if isinstance(routes, list):
        for item in routes:
            if isinstance(item, dict):
                route_map[str(item.get("route", ""))] = item
    required_route_ids = ["PC_TO_VM2", "PC_TO_VM3", "VM2_TO_VM3"]
    missing_routes = [item for item in required_route_ids if item not in route_map]
    add_check(
        checks,
        warnings,
        blockers,
        "required_routes_present",
        len(missing_routes) == 0,
        "all required route entries are present",
        f"missing required routes: {missing_routes}",
    )

    pc_to_vm2 = route_map.get("PC_TO_VM2", {})
    pc_to_vm3 = route_map.get("PC_TO_VM3", {})
    vm2_to_vm3 = route_map.get("VM2_TO_VM3", {})

    pc_to_vm2_status = str(pc_to_vm2.get("status", ""))
    pc_to_vm3_status = str(pc_to_vm3.get("status", ""))
    vm2_to_vm3_status = str(vm2_to_vm3.get("status", ""))

    add_check(
        checks,
        warnings,
        blockers,
        "pc_to_vm2_proved",
        pc_to_vm2_status == "PROVED",
        "PC_TO_VM2 route is PROVED",
        f"PC_TO_VM2 route is {pc_to_vm2_status}",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "pc_to_vm3_recovered_or_warn",
        pc_to_vm3_status in {"PROVED", "RECOVERED_PROVED", "WARN_PARTIAL"},
        "PC_TO_VM3 route is recovered/proved or warn-partial",
        f"PC_TO_VM3 route status is {pc_to_vm3_status}",
        fail_level="WARN",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "vm2_to_vm3_proved_or_blocked_unavailable",
        vm2_to_vm3_status in {"PROVED", "BLOCKED_ROUTE_UNAVAILABLE"},
        "VM2_TO_VM3 route is proved or blocked-unavailable",
        f"VM2_TO_VM3 route status is {vm2_to_vm3_status}",
        fail_level="WARN",
    )

    # Honest partial-state surfacing: blocked/unavailable route must degrade final verdict to WARN.
    if pc_to_vm3_status == "WARN_PARTIAL":
        warnings.append("pc_to_vm3_warn_partial_requires_warn_verdict")
    if vm2_to_vm3_status == "BLOCKED_ROUTE_UNAVAILABLE":
        warnings.append("vm2_to_vm3_blocked_unavailable_requires_warn_verdict")

    # Evidence refs should point to at least one existing path for each route.
    for route_id, level in [("PC_TO_VM2", "BLOCK"), ("PC_TO_VM3", "WARN"), ("VM2_TO_VM3", "WARN")]:
        route_item = route_map.get(route_id, {})
        refs = route_item.get("evidence_refs", [])
        ref_list = [str(item) for item in refs] if isinstance(refs, list) else []
        any_exists = False
        for ref in ref_list:
            candidate = Path(ref)
            if not candidate.is_absolute():
                candidate = (repo_root / ref).resolve()
            if candidate.exists():
                any_exists = True
                break
        add_check(
            checks,
            warnings,
            blockers,
            f"{route_id.lower()}_has_existing_evidence_ref",
            any_exists,
            f"{route_id} has at least one existing evidence path",
            f"{route_id} has no existing evidence path",
            fail_level=level,
        )

    # Request/result refs from summary must exist and contain no forbidden fields.
    req_refs = summary.get("request_refs", [])
    res_refs = summary.get("result_refs", [])
    req_list = [str(item) for item in req_refs] if isinstance(req_refs, list) else []
    res_list = [str(item) for item in res_refs] if isinstance(res_refs, list) else []
    add_check(
        checks,
        warnings,
        blockers,
        "request_refs_count",
        len(req_list) >= 3,
        "request refs include route recovery entries",
        f"request refs count is {len(req_list)}",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "result_refs_count",
        len(res_list) >= 3,
        "result refs include route recovery entries",
        f"result refs count is {len(res_list)}",
    )

    request_payloads: list[dict[str, Any]] = []
    result_payloads: list[dict[str, Any]] = []
    for ref in req_list:
        req_path = (repo_root / ref).resolve()
        payload, _ = load_json(req_path)
        if payload is not None:
            request_payloads.append(payload)
    for ref in res_list:
        res_path = (repo_root / ref).resolve()
        payload, _ = load_json(res_path)
        if payload is not None:
            result_payloads.append(payload)

    add_check(
        checks,
        warnings,
        blockers,
        "request_payloads_parse",
        len(request_payloads) == len(req_list),
        "all request refs parse as JSON objects",
        f"parsed request payloads {len(request_payloads)} of {len(req_list)}",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "result_payloads_parse",
        len(result_payloads) == len(res_list),
        "all result refs parse as JSON objects",
        f"parsed result payloads {len(result_payloads)} of {len(res_list)}",
    )

    request_forbidden = sorted(
        field
        for payload in request_payloads
        for field in payload
        if field in FORBIDDEN_FIELDS
    )
    result_forbidden = sorted(
        field
        for payload in result_payloads
        for field in payload
        if field in FORBIDDEN_FIELDS
    )
    add_check(
        checks,
        warnings,
        blockers,
        "request_no_forbidden_fields",
        len(request_forbidden) == 0,
        "request payloads contain no forbidden shell fields",
        f"forbidden request fields detected: {request_forbidden}",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "result_no_forbidden_fields",
        len(result_forbidden) == 0,
        "result payloads contain no forbidden shell fields",
        f"forbidden result fields detected: {result_forbidden}",
    )

    # Ledger must include route/status/evidence for each route.
    ledger_rows = load_jsonl(repo_root / RUNNER_LEDGER_REL)
    route_seen: dict[str, bool] = {}
    required_ledger_fields = [
        "route",
        "source_contour",
        "destination_contour",
        "source_path",
        "target_path",
        "sha256",
        "size_bytes",
        "evidence_refs",
        "result_status",
        "timestamp_utc",
        "claim_boundary",
    ]
    for row in ledger_rows:
        route = str(row.get("route", ""))
        if route in required_route_ids:
            route_seen[route] = True
            for field in required_ledger_fields:
                if field not in row:
                    blockers.append(f"ledger_missing_field:{route}:{field}")
    add_check(
        checks,
        warnings,
        blockers,
        "runner_ledger_routes_present",
        all(route_seen.get(route, False) for route in required_route_ids),
        "runner ledger contains all three route entries",
        f"runner ledger missing route entries: {[route for route in required_route_ids if not route_seen.get(route, False)]}",
    )

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
        route_status_map: dict[str, str] = {}
        if isinstance(transfer_routes, list):
            for item in transfer_routes:
                if isinstance(item, dict):
                    route_status_map[str(item.get("route_id", ""))] = str(item.get("route_status", ""))
        for route in required_route_ids:
            expected_status = str(route_map.get(route, {}).get("status", ""))
            actual_status = route_status_map.get(route)
            add_check(
                checks,
                warnings,
                blockers,
                f"view_state_route_{route.lower()}",
                actual_status == expected_status,
                f"view state route {route} matches summary status",
                f"view state route {route} mismatch actual={actual_status} expected={expected_status}",
            )

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report = {
        "schema_id": "TRANSFER_ROUTE_PROOF_VALIDATOR_REPORT_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "allowed_final_verdict": str(summary.get("verdict_claim", "WARN_PARTIAL_ROUTE_PROOF_WITH_VM2_TO_VM3_BLOCKED")),
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "refs": {
            "summary_ref": summary_path.as_posix(),
            "view_state_ref": VIEW_STATE_REL,
            "runner_ledger_ref": RUNNER_LEDGER_REL,
        },
        "claim_boundary": "FOUNDATION_ONLY",
        "not_proven": [
            "production orchestration",
            "global autonomous remote execution",
            "all routes live without bounded proof",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"transfer_route_proof_validator_verdict={verdict}")
    print(f"transfer_route_proof_validator_report={output_path.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
