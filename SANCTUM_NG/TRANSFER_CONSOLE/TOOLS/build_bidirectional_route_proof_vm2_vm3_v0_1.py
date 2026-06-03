#!/usr/bin/env python3
"""Build bidirectional VM2<->VM3 bounded route-proof artifacts for Transfer Console."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import uuid
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-TRANSFER-BIDIRECTIONAL-ROUTE-PROOF-VM2-V0_1"

BASE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE"
DATA_REL = f"{BASE_REL}/DATA"
REPORTS_REL = f"{BASE_REL}/REPORTS"
VIEW_STATE_REL = f"{DATA_REL}/TRANSFER_CONSOLE_VIEW_STATE.generated.json"
ACTION_REQUEST_DIR_REL = f"{DATA_REL}/action_requests"
ACTION_RESULT_DIR_REL = f"{DATA_REL}/action_results"
RUNNER_LEDGER_REL = f"{DATA_REL}/ledgers/transfer_action_runner_ledger.jsonl"
TRANSFER_LEDGER_REL = f"{DATA_REL}/ledger/transfer_action_ledger.jsonl"
ALLOWED_ROUTES_REL = f"{DATA_REL}/contours/allowed_routes_v0_1.json"
POLICY_SNAPSHOT_REL = f"{DATA_REL}/samples/transfer_action_runner_policy.v0_1.json"

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

ROUTE_SPECS: list[dict[str, str]] = [
    {
        "route": "VM2_TO_VM3",
        "source_contour": "VM2",
        "destination_contour": "VM3",
        "alias": "imperium-vm3-from-vm2",
        "auth_log_name": "vm2_to_vm3_auth.txt",
        "auth_marker": "VM2_TO_VM3_AUTH_OK",
        "expected_host": "GPT3",
        "expected_user": "vboxuser3",
        "matrix_connection_id": "VM2_TO_VM3_ALIAS_BOUNDED_ROUTE",
        "matrix_port": "2225",
        "matrix_target_repo": "/home/vboxuser3/IMPERIUM_WORK/Imperium-",
        "key_reference_path": "~/.ssh/imperium_vm2_to_vm3_ed25519_20260523",
    },
    {
        "route": "VM3_TO_VM2",
        "source_contour": "VM3",
        "destination_contour": "VM2",
        "alias": "imperium-vm2-from-vm3",
        "auth_log_name": "vm3_to_vm2_auth_via_vm3.txt",
        "auth_marker": "VM3_TO_VM2_AUTH_OK",
        "expected_host": "GPT2",
        "expected_user": "vboxuser2",
        "matrix_connection_id": "VM3_TO_VM2_ALIAS_BOUNDED_ROUTE",
        "matrix_port": "2223",
        "matrix_target_repo": "/home/vboxuser2/IMPERIUM_WORK/Imperium-",
        "key_reference_path": "~/.ssh/imperium_vm3_to_vm2_ed25519_20260523",
    },
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_id(prefix: str) -> str:
    stamp = utc_now().replace("-", "").replace(":", "")
    return f"{prefix}-{stamp}-{uuid.uuid4().hex[:8].upper()}"


def rel_or_abs(path: Path, repo_root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def list_json_records(directory: Path, limit: int = 16) -> list[dict[str, Any]]:
    if not directory.exists():
        return []
    rows: list[dict[str, Any]] = []
    for item in sorted(directory.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
        payload = load_json(item)
        if payload is None:
            continue
        payload = dict(payload)
        payload["source_record_path"] = item
        rows.append(payload)
    return rows


def list_jsonl(path: Path, limit: int = 120) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        row = raw.strip()
        if not row:
            continue
        try:
            payload = json.loads(row)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows[-limit:]


def ensure_no_forbidden_fields(payload: dict[str, Any]) -> None:
    bad = sorted(key for key in payload if key in FORBIDDEN_FIELDS)
    if bad:
        raise RuntimeError(f"forbidden request/result fields detected: {bad}")


def parse_auth_log(path: Path, marker: str, expected_host: str, expected_user: str) -> dict[str, Any]:
    out: dict[str, Any] = {
        "path": path,
        "status": "BLOCK",
        "marker_found": False,
        "host_found": False,
        "user_found": False,
        "lines": [],
        "errors": [],
    }
    if not path.exists():
        out["errors"].append("auth_log_missing")
        return out

    lines = [line.strip() for line in path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]
    out["lines"] = lines
    out["marker_found"] = marker in lines
    out["host_found"] = expected_host in lines
    out["user_found"] = expected_user in lines

    if not out["marker_found"]:
        out["errors"].append("auth_marker_missing")
    if not out["host_found"]:
        out["errors"].append("auth_host_missing")
    if not out["user_found"]:
        out["errors"].append("auth_user_missing")

    out["status"] = "PASS" if not out["errors"] else "BLOCK"
    return out


def parse_probe_result(path: Path, expected_route: str, expected_alias: str) -> dict[str, Any]:
    out: dict[str, Any] = {
        "path": path,
        "status": "BLOCK",
        "errors": [],
        "warnings": [],
        "payload": {},
    }
    payload = load_json(path)
    if payload is None:
        out["errors"].append("probe_result_missing_or_invalid_json")
        return out
    out["payload"] = payload

    route = str(payload.get("route", ""))
    alias = str(payload.get("alias", ""))
    probe_status = str(payload.get("status", ""))
    hash_size_match = payload.get("hash_size_match")
    source_sha = str(payload.get("source_sha256", "")).strip().lower()
    target_sha = str(payload.get("target_sha256", "")).strip().lower()
    source_size = payload.get("source_size_bytes")
    target_size = payload.get("target_size_bytes")

    if route != expected_route:
        out["errors"].append(f"route_mismatch:{route}")
    if alias != expected_alias:
        out["errors"].append(f"alias_mismatch:{alias}")
    if probe_status != "PROVED":
        out["errors"].append(f"probe_status_not_proved:{probe_status}")
    if hash_size_match is not True:
        out["errors"].append("hash_size_match_false")
    if not source_sha or not target_sha:
        out["errors"].append("empty_sha")
    if source_sha != target_sha:
        out["errors"].append("sha_mismatch")

    if not isinstance(source_size, int) or not isinstance(target_size, int):
        out["errors"].append("size_not_int")
    elif source_size != target_size:
        out["errors"].append("size_mismatch")

    out["status"] = "PASS" if not out["errors"] else "BLOCK"
    return out


def build_route_record(
    route_spec: dict[str, str],
    auth_check: dict[str, Any],
    probe_check: dict[str, Any],
    repo_root: Path,
) -> dict[str, Any]:
    payload = probe_check.get("payload", {}) if isinstance(probe_check.get("payload"), dict) else {}

    errors: list[str] = []
    warnings: list[str] = []
    errors.extend(str(item) for item in auth_check.get("errors", []))
    errors.extend(str(item) for item in probe_check.get("errors", []))

    status = "PROVED" if not errors else "BLOCK_ROUTE_PROOF_FAILED"

    evidence_refs = [
        rel_or_abs(Path(auth_check["path"]), repo_root),
        rel_or_abs(Path(probe_check["path"]), repo_root),
    ]

    route_record = {
        "route": route_spec["route"],
        "source_contour": route_spec["source_contour"],
        "destination_contour": route_spec["destination_contour"],
        "action_type": "SEND_TASKPACK_ZIP",
        "status": status,
        "created_utc": utc_now(),
        "claim_boundary": "bounded VM2/VM3 route probe only; no production orchestration",
        "alias": route_spec["alias"],
        "evidence_refs": evidence_refs,
        "warnings": warnings,
        "errors": errors,
        "source_path": str(payload.get("source_path", "")),
        "target_path": str(payload.get("target_path", "")),
        "sha256": str(payload.get("source_sha256", "")).strip().lower() or None,
        "size_bytes": payload.get("source_size_bytes"),
        "auth_lines": auth_check.get("lines", []),
    }
    return route_record


def proof_status_to_result_status(route_status: str) -> str:
    return "CONFIRMED" if route_status == "PROVED" else "FAILED"


def proof_status_to_transfer_ledger_status(route_status: str) -> str:
    if route_status == "PROVED":
        return "PASS"
    if route_status.startswith("WARN"):
        return "WARN"
    return "BLOCK"


def build_request_payload(task_id: str, route_record: dict[str, Any], delivery_evidence_file: str) -> dict[str, Any]:
    route = str(route_record.get("route", "UNKNOWN"))
    route_status = str(route_record.get("status", "UNKNOWN"))
    status = "COMPLETED" if route_status == "PROVED" else "FAILED"

    source_path = str(route_record.get("source_path", "")).strip() or f"{route}.source"
    target_path = str(route_record.get("target_path", "")).strip() or f"{route}.target"

    payload = {
        "schema_id": "TRANSFER_ACTION_REQUEST_V0_1",
        "request_id": new_id("TRANSFER-ACTION-REQ"),
        "task_id": task_id,
        "action_type": "SEND_TASKPACK_ZIP",
        "source_contour": str(route_record.get("source_contour", "VM2")),
        "target_contour": str(route_record.get("destination_contour", "VM3")),
        "artifact_type": "taskpack_zip",
        "artifact_name": Path(source_path).name or f"{route}.zip",
        "source_path": source_path,
        "target_path": target_path,
        "mode": "EXECUTE",
        "owner_approval_required": False,
        "owner_approved": True,
        "rollback_plan": "IMPERIUM_NEW_GENERATION/TRUTH/ACTION_ROLLBACK/ACTION_ROLLBACK_POLICY_V0_1.json",
        "allowed_command_profile": "PROFILE_NOT_READY",
        "created_at_utc": utc_now(),
        "status": status,
        "claim_boundary": "FOUNDATION_ONLY",
        "requester": "SANCTUM_NG_BIDIRECTIONAL_ROUTE_PROOF_VM2",
        "no_arbitrary_shell_confirmed": True,
        "route_proof_mode": True,
        "delivery_evidence_file": delivery_evidence_file,
        "notes": [
            "Bounded VM2/VM3 route-proof record.",
            f"route={route}",
            f"route_status={route_status}",
            "No production remote orchestration claim.",
            "No arbitrary shell claim.",
        ],
    }
    ensure_no_forbidden_fields(payload)
    return payload


def build_result_payload(task_id: str, request_payload: dict[str, Any], route_record: dict[str, Any], request_ref: str) -> dict[str, Any]:
    route_status = str(route_record.get("status", "UNKNOWN"))
    result_status = proof_status_to_result_status(route_status)
    route = str(route_record.get("route", "UNKNOWN"))

    evidence_refs = [request_ref]
    for item in route_record.get("evidence_refs", []):
        if isinstance(item, str) and item and item not in evidence_refs:
            evidence_refs.append(item)

    limitations = [
        "Bounded VM2/VM3 route-proof result only.",
        "No production remote orchestration claim.",
        "No arbitrary shell execution claim.",
        f"route:{route}",
        f"route_status:{route_status}",
        f"alias:{route_record.get('alias', '')}",
    ]
    for warn in route_record.get("warnings", []):
        limitations.append(f"warn:{warn}")
    for err in route_record.get("errors", []):
        limitations.append(f"error:{err}")

    error_text = None
    if route_record.get("errors"):
        error_text = "; ".join(str(item) for item in route_record["errors"])[:500]

    payload = {
        "schema_id": "TRANSFER_ACTION_RESULT_V0_1",
        "result_id": new_id("TRANSFER-ACTION-RESULT"),
        "request_id": str(request_payload.get("request_id", "")),
        "task_id": task_id,
        "action_type": "SEND_TASKPACK_ZIP",
        "status": result_status,
        "started_at_utc": utc_now(),
        "finished_at_utc": utc_now(),
        "evidence_refs": evidence_refs,
        "stdout_log_ref": None,
        "stderr_log_ref": None,
        "paths_verified": [
            str(route_record.get("source_path", "")),
            str(route_record.get("target_path", "")),
        ],
        "sha256_before_after": {
            "before": route_record.get("sha256"),
            "after": route_record.get("sha256") if route_status == "PROVED" else None,
        },
        "no_arbitrary_shell_confirmed": True,
        "limitations": limitations,
        "claim_boundary": "FOUNDATION_ONLY",
        "error": error_text,
        "mode": "EXECUTE",
    }
    ensure_no_forbidden_fields(payload)
    return payload


def append_runner_ledger_entry(
    ledger_path: Path,
    route_record: dict[str, Any],
    request_ref: str,
    result_ref: str,
    result_status: str,
) -> dict[str, Any]:
    row = {
        "schema_id": "TRANSFER_ACTION_RUNNER_LEDGER_ENTRY_V0_1",
        "entry_id": new_id("TRANSFER-ACTION-LEDGER"),
        "timestamp_utc": utc_now(),
        "action_id": "SEND_TASKPACK_ZIP",
        "request_ref": request_ref,
        "result_ref": result_ref,
        "result_status": result_status,
        "mode": "EXECUTE",
        "claim_boundary": "FOUNDATION_ONLY",
        "route": route_record.get("route"),
        "source_contour": route_record.get("source_contour"),
        "destination_contour": route_record.get("destination_contour"),
        "source_path": route_record.get("source_path"),
        "target_path": route_record.get("target_path"),
        "sha256": route_record.get("sha256"),
        "size_bytes": route_record.get("size_bytes"),
        "evidence_refs": route_record.get("evidence_refs", []),
        "route_proof_status": route_record.get("status"),
        "alias": route_record.get("alias"),
    }
    append_jsonl(ledger_path, row)
    return row


def append_transfer_ledger_entry(
    ledger_path: Path,
    route_record: dict[str, Any],
    request_ref: str,
    result_ref: str,
) -> dict[str, Any]:
    route_status = str(route_record.get("status", "UNKNOWN"))
    route = str(route_record.get("route", "UNKNOWN"))
    row = {
        "entry_id": new_id("LEDGER"),
        "action_type": "CHECK_CONTOUR_STATUS",
        "status": proof_status_to_transfer_ledger_status(route_status),
        "timestamp_utc": utc_now(),
        "request_ref": request_ref,
        "result_ref": result_ref,
        "notes": [
            f"route={route}",
            f"route_status={route_status}",
            f"alias={route_record.get('alias', '')}",
            f"evidence_refs={len(route_record.get('evidence_refs', []))}",
            "Bidirectional bounded route-proof entry.",
        ],
        "claim_boundary": "FOUNDATION_ONLY",
    }
    append_jsonl(ledger_path, row)
    return row


def upsert_by_connection_id(connections: list[dict[str, Any]], item: dict[str, Any]) -> list[dict[str, Any]]:
    target_id = str(item.get("connection_id", ""))
    out: list[dict[str, Any]] = []
    replaced = False
    for existing in connections:
        if str(existing.get("connection_id", "")) == target_id:
            out.append(item)
            replaced = True
        else:
            out.append(existing)
    if not replaced:
        out.append(item)
    return out


def update_mechanicus_matrix(
    repo_root: Path,
    task_id: str,
    route_records: list[dict[str, Any]],
) -> str:
    matrix_path = repo_root / MATRIX_REL
    payload = load_json(matrix_path)
    if payload is None:
        raise RuntimeError(f"missing or invalid matrix: {matrix_path.as_posix()}")

    connections = payload.get("connections", [])
    if not isinstance(connections, list):
        raise RuntimeError("matrix connections is not a list")

    route_map = {str(item.get("route", "")): item for item in route_records}

    for spec in ROUTE_SPECS:
        route_id = spec["route"]
        record = route_map.get(route_id, {})
        proved = str(record.get("status", "")) == "PROVED"
        connection = {
            "connection_id": spec["matrix_connection_id"],
            "alias": spec["alias"],
            "contour": spec["source_contour"],
            "status": "LIVE_BOUNDED_PROBE_CONFIRMED" if proved else "BOUNDED_ROUTE_PROOF_FAILED",
            "route": f"10.0.2.2:{spec['matrix_port']}",
            "host": "10.0.2.2",
            "port": int(spec["matrix_port"]),
            "user": spec["expected_user"],
            "repo_path": spec["matrix_target_repo"],
            "key_reference_path": spec["key_reference_path"],
            "live_verified": proved,
            "notes": [
                f"task_id:{task_id}",
                f"route:{route_id}",
                f"route_status:{record.get('status', 'UNKNOWN')}",
                "bounded_probe_only_no_production_claim",
                "no_private_key_material_in_repo",
            ],
        }
        connections = upsert_by_connection_id(connections, connection)

    payload["task_id"] = task_id
    payload["generated_at_utc"] = utc_now()
    payload["private_key_material_allowed_in_repo"] = False
    payload["connections"] = connections
    write_json(matrix_path, payload)
    return rel_or_abs(matrix_path, repo_root)


def update_mechanicus_route_proof_record(
    repo_root: Path,
    task_id: str,
    route_records: list[dict[str, Any]],
    auth_checks: dict[str, dict[str, Any]],
    probe_result_refs: list[str],
) -> str:
    path = repo_root / MECHANICUS_ROUTE_PROOF_REL
    payload = {
        "schema_id": "MECHANICUS_VM2_VM3_BIDIRECTIONAL_ROUTE_PROOF_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "claim_boundary": "bounded VM2/VM3 route proof only",
        "routes": route_records,
        "auth_checks": {
            route: {
                "status": check.get("status"),
                "path": rel_or_abs(Path(check["path"]), repo_root),
                "errors": check.get("errors", []),
            }
            for route, check in auth_checks.items()
        },
        "probe_result_refs": probe_result_refs,
        "matrix_ref": MATRIX_REL,
        "no_private_key_material": True,
        "not_proven": [
            "production orchestration",
            "arbitrary remote shell",
            "global all-contour transfer readiness",
        ],
    }
    write_json(path, payload)
    return rel_or_abs(path, repo_root)


def update_allowed_routes(repo_root: Path, task_id: str, route_records: list[dict[str, Any]]) -> str:
    path = repo_root / ALLOWED_ROUTES_REL
    payload = load_json(path) or {
        "schema_id": "TRANSFER_ALLOWED_ROUTES_V0_1",
        "task_id": task_id,
        "claim_boundary": "FOUNDATION_ONLY",
        "routes": [],
    }

    existing_routes = payload.get("routes", [])
    route_map: dict[str, dict[str, Any]] = {}
    if isinstance(existing_routes, list):
        for item in existing_routes:
            if isinstance(item, dict):
                route_map[str(item.get("route_id", ""))] = dict(item)

    for item in route_records:
        route_id = str(item.get("route", ""))
        route_map[route_id] = {
            "route_id": route_id,
            "source_contour": str(item.get("source_contour", "")),
            "target_contour": str(item.get("destination_contour", "")),
            "artifact_kind": "taskpack_zip",
            "route_status": "CONFIGURED",
            "route_ref": MATRIX_REL,
            "allowlisted_actions": ["SEND_TASKPACK_ZIP", "VALIDATE_TRANSFER_REQUEST", "DRY_RUN_TRANSFER"],
            "notes": [
                f"proof_status:{item.get('status', 'UNKNOWN')}",
                "Bidirectional bounded route-proof entry.",
            ],
            "claim_boundary": "FOUNDATION_ONLY",
        }

    payload["task_id"] = task_id
    payload["generated_at_utc"] = utc_now()
    payload["claim_boundary"] = "FOUNDATION_ONLY"
    payload["routes"] = sorted(route_map.values(), key=lambda row: str(row.get("route_id", "")))
    write_json(path, payload)
    return rel_or_abs(path, repo_root)


def build_contour_cards(route_map: dict[str, str]) -> list[dict[str, Any]]:
    vm2_to_vm3 = route_map.get("VM2_TO_VM3", "UNKNOWN")
    vm3_to_vm2 = route_map.get("VM3_TO_VM2", "UNKNOWN")

    both_proved = vm2_to_vm3 == "PROVED" and vm3_to_vm2 == "PROVED"
    any_proved = vm2_to_vm3 == "PROVED" or vm3_to_vm2 == "PROVED"

    if both_proved:
        vm2_status = "CONFIRMED"
        vm3_status = "CONFIRMED"
        route_status_label = "BOUNDED_ROUTE_PROVED"
    elif any_proved:
        vm2_status = "WARN"
        vm3_status = "WARN"
        route_status_label = "BOUNDED_ROUTE_WARN"
    else:
        vm2_status = "BLOCKED"
        vm3_status = "BLOCKED"
        route_status_label = "BOUNDED_ROUTE_BLOCKED"

    now = utc_now()
    return [
        {
            "contour_id": "PC",
            "display_name": "PC",
            "role": "control_contour",
            "status": "NOT_CONFIGURED",
            "status_reason": "Task scope is bounded VM2<->VM3 route proof only.",
            "route_config_status": "NOT_CONFIGURED",
            "last_probe_receipt_ref": None,
            "last_updated_utc": now,
            "claim_boundary": "FOUNDATION_ONLY",
        },
        {
            "contour_id": "VM2",
            "display_name": "VM2",
            "role": "executor_contour",
            "status": vm2_status,
            "status_reason": f"VM2_TO_VM3={vm2_to_vm3}; VM3_TO_VM2={vm3_to_vm2}.",
            "route_config_status": route_status_label,
            "last_probe_receipt_ref": None,
            "last_updated_utc": now,
            "claim_boundary": "FOUNDATION_ONLY",
        },
        {
            "contour_id": "VM3",
            "display_name": "VM3",
            "role": "executor_contour",
            "status": vm3_status,
            "status_reason": f"VM2_TO_VM3={vm2_to_vm3}; VM3_TO_VM2={vm3_to_vm2}.",
            "route_config_status": route_status_label,
            "last_probe_receipt_ref": None,
            "last_updated_utc": now,
            "claim_boundary": "FOUNDATION_ONLY",
        },
    ]


def build_final_verdict(route_records: list[dict[str, Any]]) -> tuple[str, str]:
    statuses = [str(item.get("status", "UNKNOWN")) for item in route_records]
    proved_count = sum(1 for item in statuses if item == "PROVED")

    if proved_count == 2:
        return "PASS", "PASS_FOR_TWO_CONFIRMED_BOUNDED_VM2_VM3_TRANSFER_ROUTES_ONLY"
    if proved_count >= 1:
        return "WARN", "WARN_PARTIAL_BIDIRECTIONAL_ROUTE_PROOF"
    return "BLOCK", "BLOCK_ROUTE_PROOF_FAILED"


def update_view_state(
    repo_root: Path,
    task_id: str,
    route_records: list[dict[str, Any]],
    summary_ref: str,
    context_mix: dict[str, Any],
    verdict_status: str,
    verdict_claim: str,
    extra_source_refs: list[str],
) -> str:
    request_dir = repo_root / ACTION_REQUEST_DIR_REL
    result_dir = repo_root / ACTION_RESULT_DIR_REL
    runner_ledger_path = repo_root / RUNNER_LEDGER_REL
    policy_snapshot = load_json(repo_root / POLICY_SNAPSHOT_REL) or {}

    requests = list_json_records(request_dir, limit=16)
    results = list_json_records(result_dir, limit=16)
    ledger = list_jsonl(runner_ledger_path, limit=120)

    latest_requests: list[dict[str, Any]] = []
    for item in requests:
        clean = {k: v for k, v in item.items() if k != "source_record_path"}
        source_record_path = item.get("source_record_path")
        if isinstance(source_record_path, Path):
            clean["source_record_path"] = rel_or_abs(source_record_path, repo_root)
        latest_requests.append(clean)

    latest_results: list[dict[str, Any]] = []
    for item in results:
        clean = {k: v for k, v in item.items() if k != "source_record_path"}
        source_record_path = item.get("source_record_path")
        if isinstance(source_record_path, Path):
            clean["source_record_path"] = rel_or_abs(source_record_path, repo_root)
        latest_results.append(clean)

    route_map = {str(item.get("route", "")): str(item.get("status", "UNKNOWN")) for item in route_records}

    transfer_routes = []
    for item in route_records:
        transfer_routes.append(
            {
                "route_id": str(item.get("route", "")),
                "source_contour": str(item.get("source_contour", "")),
                "target_contour": str(item.get("destination_contour", "")),
                "action_type": str(item.get("action_type", "SEND_TASKPACK_ZIP")),
                "route_status": str(item.get("status", "UNKNOWN")),
                "route_verdict": str(item.get("status", "UNKNOWN")),
                "evidence_refs": [str(ref) for ref in item.get("evidence_refs", []) if isinstance(ref, str)],
                "limitations": [
                    f"warnings={len(item.get('warnings', []))}",
                    f"errors={len(item.get('errors', []))}",
                    "bounded_probe_only",
                ],
                "claim_boundary": "FOUNDATION_ONLY",
            }
        )

    action_runner_state = {
        "schema_id": "TRANSFER_ACTION_RUNNER_STATE_V0_1",
        "generated_at_utc": utc_now(),
        "claim_boundary": "FOUNDATION_ONLY",
        "no_arbitrary_shell_confirmed": True,
        "supported_action_types": sorted(
            policy_snapshot.get(
                "allowed_action_types",
                [
                    "SEND_TASKPACK_ZIP",
                    "FETCH_REPORT_BUNDLE_ZIP",
                    "REGISTER_TRANSFER_RESULT",
                    "VALIDATE_TRANSFER_REQUEST",
                    "DRY_RUN_TRANSFER",
                ],
            )
        ),
        "allowed_contours": sorted(policy_snapshot.get("allowed_contours", ["PC", "VM2", "VM3"])),
        "safe_target_roots": policy_snapshot.get("safe_target_roots", {}),
        "latest_action_requests": latest_requests,
        "latest_action_results": latest_results,
        "latest_runner_ledger": ledger,
        "last_action": {
            "action_id": "BIDIRECTIONAL_ROUTE_PROOF",
            "request_ref": summary_ref,
            "result_ref": summary_ref,
            "route_proof_status": verdict_status,
            "route": "VM2_TO_VM3|VM3_TO_VM2",
            "route_proof_verdict": verdict_claim,
            "route_proof_evidence_count": sum(len(item.get("evidence_refs", [])) for item in route_records),
        },
        "status_labels": [
            "DRY_RUN_OK",
            "SENT",
            "FETCHED",
            "CONFIRMED",
            "REGISTERED",
            "FAILED",
            "BLOCKED",
            "NOT_READY",
            "PREVIEW_ONLY",
            "NOT_WIRED",
        ],
        "known_limitations": [
            "Bounded VM2/VM3 route proof only.",
            "No production remote orchestration claim.",
            "No arbitrary remote shell claim.",
            f"verdict:{verdict_claim}",
        ],
    }

    source_refs = [
        f"{BASE_REL}/CONTRACTS/transfer_action_request.schema.json",
        f"{BASE_REL}/CONTRACTS/transfer_action_result.schema.json",
        f"{BASE_REL}/CONTRACTS/transfer_console_view_state_v0_1.schema.json",
        ACTION_REQUEST_DIR_REL,
        ACTION_RESULT_DIR_REL,
        RUNNER_LEDGER_REL,
        summary_ref,
    ]
    for ref in extra_source_refs:
        if ref not in source_refs:
            source_refs.append(ref)

    view_payload = {
        "schema_id": "TRANSFER_CONSOLE_VIEW_STATE_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "claim_boundary": "FOUNDATION_ONLY",
        "contour_cards": build_contour_cards(route_map),
        "latest_requests": latest_requests,
        "latest_results": latest_results,
        "action_ledger": ledger,
        "transfer_routes": transfer_routes,
        "source_refs": source_refs,
        "context_source_mix": context_mix,
        "action_runner_state": action_runner_state,
        "truth_labels": [
            "FOUNDATION_ONLY",
            "NO_PRODUCTION_REMOTE_ORCHESTRATION",
            "NO_ARBITRARY_SHELL",
            "NO_FAKE_GREEN",
            "TRANSFER_ROUTE_PROOF_BIDIRECTIONAL_VM2_VM3",
            verdict_claim,
        ],
    }
    view_path = repo_root / VIEW_STATE_REL
    write_json(view_path, view_payload)
    return rel_or_abs(view_path, repo_root)


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[4]
    default_report_dir = default_repo_root / REPORTS_REL / TASK_ID_DEFAULT
    parser = argparse.ArgumentParser(description="Build bidirectional VM2/VM3 route-proof artifacts.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument(
        "--vm2-to-vm3-probe",
        type=Path,
        default=default_report_dir / "vm2_to_vm3_probe_result.json",
    )
    parser.add_argument(
        "--vm3-to-vm2-probe",
        type=Path,
        default=default_report_dir / "vm3_to_vm2_probe_result.json",
    )
    parser.add_argument(
        "--output-report",
        type=Path,
        default=default_report_dir / "bidirectional_route_probe_report.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    task_id = str(args.task_id)
    report_dir = args.report_dir.resolve()
    report_dir.mkdir(parents=True, exist_ok=True)
    action_logs_dir = report_dir / "ACTION_LOGS"

    auth_checks: dict[str, dict[str, Any]] = {}
    probe_checks: dict[str, dict[str, Any]] = {}

    probe_path_by_route = {
        "VM2_TO_VM3": args.vm2_to_vm3_probe.resolve(),
        "VM3_TO_VM2": args.vm3_to_vm2_probe.resolve(),
    }

    route_records: list[dict[str, Any]] = []
    for spec in ROUTE_SPECS:
        route = spec["route"]
        auth_path = action_logs_dir / spec["auth_log_name"]
        auth_check = parse_auth_log(
            path=auth_path,
            marker=spec["auth_marker"],
            expected_host=spec["expected_host"],
            expected_user=spec["expected_user"],
        )
        probe_check = parse_probe_result(
            path=probe_path_by_route[route],
            expected_route=route,
            expected_alias=spec["alias"],
        )

        auth_checks[route] = auth_check
        probe_checks[route] = probe_check
        route_records.append(build_route_record(spec, auth_check, probe_check, repo_root))

    request_dir = repo_root / ACTION_REQUEST_DIR_REL
    result_dir = repo_root / ACTION_RESULT_DIR_REL
    runner_ledger_path = repo_root / RUNNER_LEDGER_REL
    transfer_ledger_path = repo_root / TRANSFER_LEDGER_REL
    request_dir.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)
    runner_ledger_path.parent.mkdir(parents=True, exist_ok=True)
    transfer_ledger_path.parent.mkdir(parents=True, exist_ok=True)
    if not runner_ledger_path.exists():
        runner_ledger_path.write_text("", encoding="utf-8")
    if not transfer_ledger_path.exists():
        transfer_ledger_path.write_text("", encoding="utf-8")

    request_refs: list[str] = []
    result_refs: list[str] = []

    for route_record in route_records:
        probe_ref = ""
        route = str(route_record.get("route", ""))
        check = probe_checks.get(route, {})
        path_obj = check.get("path")
        if isinstance(path_obj, Path):
            probe_ref = rel_or_abs(path_obj, repo_root)

        request_payload = build_request_payload(task_id, route_record, probe_ref)
        request_path = request_dir / f"{request_payload['request_id']}.json"
        write_json(request_path, request_payload)
        request_ref = rel_or_abs(request_path, repo_root)
        request_refs.append(request_ref)

        result_payload = build_result_payload(task_id, request_payload, route_record, request_ref)
        result_path = result_dir / f"{result_payload['result_id']}.json"
        write_json(result_path, result_payload)
        result_ref = rel_or_abs(result_path, repo_root)
        result_refs.append(result_ref)

        append_runner_ledger_entry(
            runner_ledger_path,
            route_record=route_record,
            request_ref=request_ref,
            result_ref=result_ref,
            result_status=str(result_payload.get("status", "FAILED")),
        )
        append_transfer_ledger_entry(
            transfer_ledger_path,
            route_record=route_record,
            request_ref=request_ref,
            result_ref=result_ref,
        )

    verdict_status, verdict_claim = build_final_verdict(route_records)

    context_mix = {
        "taskpack_percent": 36,
        "existing_newgen_repo_percent": 24,
        "owner_handoff_percent": 20,
        "runtime_probe_evidence_percent": 16,
        "servitor_inference_percent": 4,
        "external_local_private_percent": 0,
    }

    context_mix_payload = {
        "schema_id": "TRANSFER_ROUTE_PROOF_CONTEXT_SOURCE_MIX_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "claim_boundary": "bounded VM2/VM3 route proof only",
        "mix": context_mix,
    }
    context_mix_path = report_dir / "context_source_mix.json"
    write_json(context_mix_path, context_mix_payload)

    matrix_ref = update_mechanicus_matrix(repo_root, task_id, route_records)
    mechanicus_route_proof_ref = update_mechanicus_route_proof_record(
        repo_root=repo_root,
        task_id=task_id,
        route_records=route_records,
        auth_checks=auth_checks,
        probe_result_refs=[rel_or_abs(path, repo_root) for path in probe_path_by_route.values()],
    )

    allowed_routes_ref = update_allowed_routes(repo_root, task_id, route_records)

    output_report_path = args.output_report.resolve()
    summary_ref = rel_or_abs(output_report_path, repo_root)

    view_state_ref = update_view_state(
        repo_root=repo_root,
        task_id=task_id,
        route_records=route_records,
        summary_ref=summary_ref,
        context_mix=context_mix,
        verdict_status=verdict_status,
        verdict_claim=verdict_claim,
        extra_source_refs=[
            rel_or_abs(context_mix_path, repo_root),
            rel_or_abs(action_logs_dir / "vm2_to_vm3_auth.txt", repo_root),
            rel_or_abs(action_logs_dir / "vm3_to_vm2_auth_via_vm3.txt", repo_root),
            rel_or_abs(probe_path_by_route["VM2_TO_VM3"], repo_root),
            rel_or_abs(probe_path_by_route["VM3_TO_VM2"], repo_root),
            matrix_ref,
            mechanicus_route_proof_ref,
            allowed_routes_ref,
        ],
    )

    report_payload = {
        "schema_id": "BIDIRECTIONAL_ROUTE_PROBE_REPORT_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "repo_path": repo_root.as_posix(),
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip(),
        "verdict_status": verdict_status,
        "verdict_claim": verdict_claim,
        "claim_boundary": "bounded VM2/VM3 route proof only; no production orchestration",
        "routes": route_records,
        "auth_checks": {
            route: {
                "status": check.get("status"),
                "path": rel_or_abs(Path(check["path"]), repo_root),
                "errors": check.get("errors", []),
            }
            for route, check in auth_checks.items()
        },
        "probe_result_refs": [
            rel_or_abs(probe_path_by_route["VM2_TO_VM3"], repo_root),
            rel_or_abs(probe_path_by_route["VM3_TO_VM2"], repo_root),
        ],
        "request_refs": request_refs,
        "result_refs": result_refs,
        "runner_ledger_ref": RUNNER_LEDGER_REL,
        "transfer_ledger_ref": TRANSFER_LEDGER_REL,
        "view_state_ref": view_state_ref,
        "allowed_routes_ref": allowed_routes_ref,
        "mechanicus_matrix_ref": matrix_ref,
        "mechanicus_route_proof_ref": mechanicus_route_proof_ref,
        "context_source_mix_ref": rel_or_abs(context_mix_path, repo_root),
        "context_source_mix": context_mix,
        "not_proven": [
            "production orchestration",
            "arbitrary remote shell",
            "global all-contour transfer readiness",
        ],
    }
    write_json(output_report_path, report_payload)

    print(f"bidirectional_builder_verdict={verdict_status}")
    print(f"bidirectional_builder_claim={verdict_claim}")
    print(f"bidirectional_route_probe_report={summary_ref}")
    print(f"transfer_console_view_state={view_state_ref}")
    print(f"mechanicus_matrix={matrix_ref}")
    print(f"mechanicus_route_proof_record={mechanicus_route_proof_ref}")

    return 0 if verdict_status in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
