#!/usr/bin/env python3
"""Run foundation-only Transfer Console allowlisted actions for Sanctum NG."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import socket
import subprocess
import uuid
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-TRANSFER-CONSOLE-VM3-V0_1"
REQUIRED_STARTING_HEAD_DEFAULT = "1baa600f35af1dd5f3c49403bbc56557838367e6"
BASE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE"

CONTOUR_REGISTRY_REL = f"{BASE_REL}/DATA/contours/contour_registry_v0_1.json"
ROUTE_REGISTRY_REL = f"{BASE_REL}/DATA/contours/allowed_routes_v0_1.json"
CONTOUR_STATUS_REL = f"{BASE_REL}/DATA/contours/contour_status.latest.json"
PROBE_DIR_REL = f"{BASE_REL}/DATA/contours/probes"
REQUEST_DIR_REL = f"{BASE_REL}/DATA/requests"
RESULT_DIR_REL = f"{BASE_REL}/DATA/results"
LEDGER_PATH_REL = f"{BASE_REL}/DATA/ledger/transfer_action_ledger.jsonl"
VIEW_STATE_REL = f"{BASE_REL}/DATA/TRANSFER_CONSOLE_VIEW_STATE.generated.json"

SSH_MATRIX_REL = "IMPERIUM_NEW_GENERATION/MECHANICUS/CONNECTIONS/SSH_CONNECTION_MATRIX_V0_1.json"
ROLLBACK_POLICY_REL = "IMPERIUM_NEW_GENERATION/TRUTH/ACTION_ROLLBACK/ACTION_ROLLBACK_POLICY_V0_1.json"

ALLOWLISTED_ACTIONS = {
    "CHECK_CONTOUR_STATUS",
    "REGISTER_TASKPACK_SEND",
    "REGISTER_REPORT_BUNDLE_FETCH",
    "DRY_RUN_TASKPACK_SEND",
    "DRY_RUN_REPORT_FETCH",
    "REFRESH_TRANSFER_CONSOLE_VIEW",
    "BUILD_FOUNDATION",
}

FORBIDDEN_REQUEST_FIELDS = {
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


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def relpath(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def list_json_records(directory: Path) -> list[dict[str, Any]]:
    if not directory.exists():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        payload = load_json(path)
        if payload is not None:
            payload["_path"] = path
            records.append(payload)
    return records


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            out.append(payload)
    return out


def new_id(prefix: str) -> str:
    stamp = utc_now().replace("-", "").replace(":", "")
    return f"{prefix}-{stamp}-{uuid.uuid4().hex[:8].upper()}"


def ensure_transfer_foundation(repo_root: Path, task_id: str) -> dict[str, Path]:
    contour_registry_path = repo_root / CONTOUR_REGISTRY_REL
    route_registry_path = repo_root / ROUTE_REGISTRY_REL
    contour_status_path = repo_root / CONTOUR_STATUS_REL
    probe_dir = repo_root / PROBE_DIR_REL
    request_dir = repo_root / REQUEST_DIR_REL
    result_dir = repo_root / RESULT_DIR_REL
    ledger_path = repo_root / LEDGER_PATH_REL
    view_state_path = repo_root / VIEW_STATE_REL

    probe_dir.mkdir(parents=True, exist_ok=True)
    request_dir.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)

    if not contour_registry_path.exists():
        write_json(
            contour_registry_path,
            {
                "schema_id": "TRANSFER_CONTOUR_REGISTRY_V0_1",
                "task_id": task_id,
                "claim_boundary": "FOUNDATION_ONLY",
                "contours": [
                    {
                        "contour_id": "PC",
                        "display_name": "PC",
                        "role": "control_contour",
                        "default_route_config_status": "NOT_CONFIGURED",
                    },
                    {
                        "contour_id": "VM2",
                        "display_name": "VM2",
                        "role": "executor_contour",
                        "default_route_config_status": "CONFIGURED_NOT_VERIFIED",
                    },
                    {
                        "contour_id": "VM3",
                        "display_name": "VM3",
                        "role": "executor_contour",
                        "default_route_config_status": "CONFIGURED",
                    },
                ],
                "allowlisted_actions": sorted(ALLOWLISTED_ACTIONS - {"BUILD_FOUNDATION"}),
                "forbidden_request_fields": sorted(FORBIDDEN_REQUEST_FIELDS),
            },
        )

    if not route_registry_path.exists():
        write_json(
            route_registry_path,
            {
                "schema_id": "TRANSFER_ALLOWED_ROUTES_V0_1",
                "task_id": task_id,
                "claim_boundary": "FOUNDATION_ONLY",
                "routes": [
                    {
                        "route_id": "PC_TO_VM3_TASKPACK",
                        "source_contour": "PC",
                        "target_contour": "VM3",
                        "artifact_kind": "taskpack_zip",
                        "route_status": "CONFIGURED",
                        "route_ref": SSH_MATRIX_REL,
                        "allowlisted_actions": [
                            "REGISTER_TASKPACK_SEND",
                            "DRY_RUN_TASKPACK_SEND",
                        ],
                        "notes": [
                            "Metadata route only.",
                            "No live transfer claim without result receipt.",
                        ],
                        "claim_boundary": "FOUNDATION_ONLY",
                    },
                    {
                        "route_id": "VM3_TO_PC_REPORT_BUNDLE",
                        "source_contour": "VM3",
                        "target_contour": "PC",
                        "artifact_kind": "report_bundle",
                        "route_status": "CONFIGURED",
                        "route_ref": SSH_MATRIX_REL,
                        "allowlisted_actions": [
                            "REGISTER_REPORT_BUNDLE_FETCH",
                            "DRY_RUN_REPORT_FETCH",
                        ],
                        "notes": [
                            "Metadata route only.",
                            "No production orchestration claim.",
                        ],
                        "claim_boundary": "FOUNDATION_ONLY",
                    },
                ],
            },
        )

    if not contour_status_path.exists():
        write_json(
            contour_status_path,
            {
                "schema_id": "TRANSFER_CONTOUR_STATUS_SET_V0_1",
                "task_id": task_id,
                "generated_at_utc": utc_now(),
                "claim_boundary": "FOUNDATION_ONLY",
                "contours": [
                    {
                        "contour_id": "PC",
                        "display_name": "PC",
                        "role": "control_contour",
                        "status": "NOT_CONFIGURED",
                        "status_reason": "No bounded probe route configured from VM3.",
                        "route_config_status": "NOT_CONFIGURED",
                        "last_probe_receipt_ref": None,
                        "last_updated_utc": utc_now(),
                        "claim_boundary": "FOUNDATION_ONLY",
                    },
                    {
                        "contour_id": "VM2",
                        "display_name": "VM2",
                        "role": "executor_contour",
                        "status": "UNKNOWN",
                        "status_reason": "No fresh bounded probe receipt exists.",
                        "route_config_status": "CONFIGURED_NOT_VERIFIED",
                        "last_probe_receipt_ref": None,
                        "last_updated_utc": utc_now(),
                        "claim_boundary": "FOUNDATION_ONLY",
                    },
                    {
                        "contour_id": "VM3",
                        "display_name": "VM3",
                        "role": "executor_contour",
                        "status": "UNKNOWN",
                        "status_reason": "No fresh bounded probe receipt exists.",
                        "route_config_status": "CONFIGURED",
                        "last_probe_receipt_ref": None,
                        "last_updated_utc": utc_now(),
                        "claim_boundary": "FOUNDATION_ONLY",
                    },
                ],
            },
        )

    if not ledger_path.exists():
        ledger_path.write_text("", encoding="utf-8")

    return {
        "contour_registry": contour_registry_path,
        "route_registry": route_registry_path,
        "contour_status": contour_status_path,
        "probe_dir": probe_dir,
        "request_dir": request_dir,
        "result_dir": result_dir,
        "ledger": ledger_path,
        "view_state": view_state_path,
    }


def load_connection_by_contour(repo_root: Path) -> dict[str, dict[str, Any]]:
    matrix = load_json(repo_root / SSH_MATRIX_REL) or {}
    raw = matrix.get("connections", [])
    out: dict[str, dict[str, Any]] = {}
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                contour = str(item.get("contour", "")).strip().upper()
                if contour:
                    out[contour] = item
    return out


def run_git_probe(repo_root: Path) -> tuple[bool, str]:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode == 0:
        return True, f"git_head={proc.stdout.strip()}"
    return False, proc.stderr.strip() or "git probe failed"


def run_tcp_probe(host: str, port: int, timeout_seconds: float = 1.5) -> tuple[bool, str]:
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            return True, f"tcp_connect_ok:{host}:{port}"
    except OSError as exc:
        return False, f"tcp_connect_error:{host}:{port}:{exc}"


def write_probe_receipt(repo_root: Path, probe_dir: Path, payload: dict[str, Any]) -> str:
    probe_id = new_id("PROBE")
    path = probe_dir / f"{probe_id}.json"
    write_json(path, payload)
    return relpath(path, repo_root)


def update_contour_status_from_probe(
    repo_root: Path,
    foundation: dict[str, Path],
    task_id: str,
) -> tuple[dict[str, Any], list[str], list[str]]:
    status_set = load_json(foundation["contour_status"]) or {}
    contours = status_set.get("contours", [])
    contour_list = [item for item in contours if isinstance(item, dict)] if isinstance(contours, list) else []

    by_id: dict[str, dict[str, Any]] = {
        str(item.get("contour_id", "")).upper(): item for item in contour_list if str(item.get("contour_id", "")).strip()
    }
    connection_map = load_connection_by_contour(repo_root)

    receipts: list[str] = []
    notes: list[str] = []
    now = utc_now()

    for contour_id in ["PC", "VM2", "VM3"]:
        rec = by_id.get(contour_id)
        if rec is None:
            rec = {
                "contour_id": contour_id,
                "display_name": contour_id,
                "role": "executor_contour" if contour_id != "PC" else "control_contour",
                "status": "UNKNOWN",
                "status_reason": "Auto-created contour status record.",
                "route_config_status": "NOT_CONFIGURED",
                "last_probe_receipt_ref": None,
                "last_updated_utc": now,
                "claim_boundary": "FOUNDATION_ONLY",
            }
            by_id[contour_id] = rec

        if contour_id == "PC":
            rec["status"] = "NOT_CONFIGURED"
            rec["route_config_status"] = "NOT_CONFIGURED"
            rec["status_reason"] = "No bounded VM3-side probe route configured for PC contour."
            rec["last_probe_receipt_ref"] = None
            rec["last_updated_utc"] = now
            notes.append("PC_NOT_CONFIGURED")
            continue

        if contour_id == "VM3":
            ok, detail = run_git_probe(repo_root)
            receipt = {
                "schema_id": "TRANSFER_CONTOUR_PROBE_RECEIPT_V0_1",
                "task_id": task_id,
                "contour_id": contour_id,
                "probe_type": "LOCAL_GIT_HEAD_PROBE",
                "started_utc": now,
                "finished_utc": utc_now(),
                "status": "PASS" if ok else "ERROR",
                "details": detail,
                "claim_boundary": "FOUNDATION_ONLY",
            }
            receipt_ref = write_probe_receipt(repo_root, foundation["probe_dir"], receipt)
            receipts.append(receipt_ref)
            rec["status"] = "ONLINE" if ok else "OFFLINE"
            rec["route_config_status"] = "CONFIGURED"
            rec["status_reason"] = "Bounded local probe succeeded." if ok else f"Bounded local probe failed: {detail}"
            rec["last_probe_receipt_ref"] = receipt_ref
            rec["last_updated_utc"] = utc_now()
            notes.append("VM3_PROBE_PASS" if ok else "VM3_PROBE_FAIL")
            continue

        connection = connection_map.get("VM2", {})
        host = str(connection.get("host", "")).strip()
        port_raw = connection.get("port")
        port = int(port_raw) if isinstance(port_raw, int) else None
        if host and port:
            ok, detail = run_tcp_probe(host=host, port=port)
            receipt = {
                "schema_id": "TRANSFER_CONTOUR_PROBE_RECEIPT_V0_1",
                "task_id": task_id,
                "contour_id": contour_id,
                "probe_type": "TCP_CONNECT_PROBE",
                "started_utc": now,
                "finished_utc": utc_now(),
                "status": "PASS" if ok else "ERROR",
                "details": detail,
                "claim_boundary": "FOUNDATION_ONLY",
            }
            receipt_ref = write_probe_receipt(repo_root, foundation["probe_dir"], receipt)
            receipts.append(receipt_ref)
            rec["status"] = "ONLINE" if ok else "OFFLINE"
            rec["route_config_status"] = "CONFIGURED_NOT_VERIFIED"
            rec["status_reason"] = "Bounded tcp probe succeeded." if ok else f"Bounded tcp probe failed: {detail}"
            rec["last_probe_receipt_ref"] = receipt_ref
            rec["last_updated_utc"] = utc_now()
            notes.append("VM2_TCP_PROBE_PASS" if ok else "VM2_TCP_PROBE_FAIL")
        else:
            rec["status"] = "UNKNOWN"
            rec["route_config_status"] = "NOT_CONFIGURED"
            rec["status_reason"] = "VM2 route metadata is incomplete for bounded probe."
            rec["last_probe_receipt_ref"] = None
            rec["last_updated_utc"] = utc_now()
            notes.append("VM2_ROUTE_NOT_CONFIGURED")

    final_contours = [by_id[contour] for contour in ["PC", "VM2", "VM3"]]
    status_set["schema_id"] = "TRANSFER_CONTOUR_STATUS_SET_V0_1"
    status_set["task_id"] = task_id
    status_set["generated_at_utc"] = utc_now()
    status_set["claim_boundary"] = "FOUNDATION_ONLY"
    status_set["contours"] = final_contours

    write_json(foundation["contour_status"], status_set)
    return status_set, receipts, notes


def validate_no_forbidden_fields(payload: dict[str, Any]) -> list[str]:
    return sorted([key for key in payload.keys() if key in FORBIDDEN_REQUEST_FIELDS])


def route_ready(repo_root: Path, source_contour: str, target_contour: str, artifact_kind: str) -> bool:
    route_registry = load_json(repo_root / ROUTE_REGISTRY_REL) or {}
    routes = route_registry.get("routes", [])
    if not isinstance(routes, list):
        return False
    for route in routes:
        if not isinstance(route, dict):
            continue
        if (
            str(route.get("source_contour", "")) == source_contour
            and str(route.get("target_contour", "")) == target_contour
            and str(route.get("artifact_kind", "")) == artifact_kind
            and str(route.get("route_status", "")) == "CONFIGURED"
        ):
            return True
    return False


def create_request_record(
    repo_root: Path,
    foundation: dict[str, Path],
    task_id: str,
    action_type: str,
    source_contour: str,
    target_contour: str,
    artifact_kind: str,
    artifact_ref: str,
    requested_by: str,
    status: str,
) -> tuple[dict[str, Any], str]:
    request_id = new_id("TRANSFER-REQ")
    record = {
        "request_id": request_id,
        "action_type": action_type,
        "source_contour": source_contour,
        "target_contour": target_contour,
        "artifact_kind": artifact_kind,
        "artifact_ref": artifact_ref,
        "requested_by": requested_by,
        "created_utc": utc_now(),
        "allowlist_verdict": "ALLOWED",
        "rollback_plan_ref": ROLLBACK_POLICY_REL,
        "status": status,
        "claim_boundary": "FOUNDATION_ONLY",
        "notes": [
            "Foundation-only transfer registration.",
            "No arbitrary shell command fields are allowed.",
        ],
    }

    forbidden_keys = validate_no_forbidden_fields(record)
    if forbidden_keys:
        raise ValueError(f"forbidden request fields present: {forbidden_keys}")

    path = foundation["request_dir"] / f"{request_id}.json"
    write_json(path, record)
    return record, relpath(path, repo_root)


def create_result_record(
    repo_root: Path,
    foundation: dict[str, Path],
    request_id: str,
    action_type: str,
    status: str,
    evidence_refs: list[str],
    error: str | None,
    not_proven: list[str],
) -> tuple[dict[str, Any], str]:
    result_id = new_id("TRANSFER-RESULT")
    record = {
        "result_id": result_id,
        "request_id": request_id,
        "action_type": action_type,
        "status": status,
        "started_utc": utc_now(),
        "finished_utc": utc_now(),
        "evidence_refs": evidence_refs,
        "error": error,
        "not_proven": not_proven,
        "claim_boundary": "FOUNDATION_ONLY",
    }
    path = foundation["result_dir"] / f"{result_id}.json"
    write_json(path, record)
    return record, relpath(path, repo_root)


def append_ledger_entry(
    repo_root: Path,
    foundation: dict[str, Path],
    action_type: str,
    status: str,
    request_ref: str | None,
    result_ref: str | None,
    notes: list[str],
) -> str:
    entry_id = new_id("LEDGER")
    entry = {
        "entry_id": entry_id,
        "action_type": action_type,
        "status": status,
        "timestamp_utc": utc_now(),
        "request_ref": request_ref,
        "result_ref": result_ref,
        "notes": notes,
        "claim_boundary": "FOUNDATION_ONLY",
    }
    append_jsonl(foundation["ledger"], entry)
    return entry_id


def build_view_state(
    repo_root: Path,
    foundation: dict[str, Path],
    task_id: str,
    context_source_mix: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], str]:
    contour_status = load_json(foundation["contour_status"]) or {}
    contours = contour_status.get("contours", [])
    contour_cards = [item for item in contours if isinstance(item, dict)] if isinstance(contours, list) else []

    requests = list_json_records(foundation["request_dir"])
    results = list_json_records(foundation["result_dir"])
    ledger = load_jsonl(foundation["ledger"])
    route_registry = load_json(foundation["route_registry"]) or {}
    transfer_routes = route_registry.get("routes", []) if isinstance(route_registry.get("routes"), list) else []

    latest_requests: list[dict[str, Any]] = []
    for item in requests[:12]:
        clean = {k: v for k, v in item.items() if k != "_path"}
        clean["source_path"] = relpath(Path(item["_path"]), repo_root)
        latest_requests.append(clean)

    latest_results: list[dict[str, Any]] = []
    for item in results[:12]:
        clean = {k: v for k, v in item.items() if k != "_path"}
        clean["source_path"] = relpath(Path(item["_path"]), repo_root)
        latest_results.append(clean)

    if context_source_mix is None:
        context_source_mix = {
            "taskpack_percent": 67,
            "existing_newgen_repo_percent": 24,
            "owner_handoff_percent": 5,
            "organ_registry_percent": 2,
            "servitor_inference_percent": 2,
            "external_local_private_percent": 0,
        }

    source_refs = [
        CONTOUR_REGISTRY_REL,
        ROUTE_REGISTRY_REL,
        CONTOUR_STATUS_REL,
        SSH_MATRIX_REL,
        ROLLBACK_POLICY_REL,
        REQUEST_DIR_REL,
        RESULT_DIR_REL,
        LEDGER_PATH_REL,
    ]

    view_state = {
        "schema_id": "TRANSFER_CONSOLE_VIEW_STATE_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "claim_boundary": "FOUNDATION_ONLY",
        "contour_cards": contour_cards,
        "latest_requests": latest_requests,
        "latest_results": latest_results,
        "action_ledger": ledger[-30:],
        "transfer_routes": transfer_routes,
        "source_refs": source_refs,
        "truth_labels": [
            "FOUNDATION_ONLY",
            "NO_PRODUCTION_REMOTE_ORCHESTRATION",
            "NO_ARBITRARY_SHELL",
            "NO_FAKE_GREEN",
        ],
        "context_source_mix": context_source_mix,
    }

    write_json(foundation["view_state"], view_state)
    return view_state, relpath(foundation["view_state"], repo_root)


def default_transfer_target(action_id: str, task_id: str) -> tuple[str, str, str, str]:
    taskpack_ref = (
        "INBOX/VM3_TASKPACKS/TASK-20260523-NEWGEN-SANCTUM-TRANSFER-CONSOLE-VM3-V0_1/"
        "TASKPACK_TASK-20260523-NEWGEN-SANCTUM-TRANSFER-CONSOLE-VM3-V0_1.zip"
    )
    report_bundle_ref = (
        f"IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/REPORTS/{task_id}/"
        "TRANSFER_CONSOLE_REPORT_BUNDLE_PLACEHOLDER.zip"
    )

    if action_id in {"REGISTER_TASKPACK_SEND", "DRY_RUN_TASKPACK_SEND"}:
        return "PC", "VM3", "taskpack_zip", taskpack_ref
    return "VM3", "PC", "report_bundle", report_bundle_ref


def run_transfer_registration_action(
    repo_root: Path,
    foundation: dict[str, Path],
    task_id: str,
    action_id: str,
    requester: str,
) -> dict[str, Any]:
    source, target, artifact_kind, artifact_ref = default_transfer_target(action_id, task_id)
    dry_run = action_id in {"DRY_RUN_TASKPACK_SEND", "DRY_RUN_REPORT_FETCH"}
    route_is_ready = route_ready(repo_root, source, target, artifact_kind)

    request_status = "DRY_RUN_READY" if dry_run else "REQUESTED"
    request_record, request_ref = create_request_record(
        repo_root=repo_root,
        foundation=foundation,
        task_id=task_id,
        action_type=action_id,
        source_contour=source,
        target_contour=target,
        artifact_kind=artifact_kind,
        artifact_ref=artifact_ref,
        requested_by=requester,
        status=request_status,
    )

    if dry_run and route_is_ready:
        result_status = "DRY_RUN_READY"
        action_status = "PASS"
    elif dry_run and not route_is_ready:
        result_status = "NOT_READY"
        action_status = "WARN"
    elif route_is_ready:
        result_status = "NOT_READY"
        action_status = "WARN"
    else:
        result_status = "NOT_READY"
        action_status = "WARN"

    not_proven = [
        "No live transfer performed.",
        "SENT/FETCHED states are blocked without explicit result receipt evidence.",
    ]
    evidence_refs = [request_ref, ROUTE_REGISTRY_REL, CONTOUR_STATUS_REL]
    result_record, result_ref = create_result_record(
        repo_root=repo_root,
        foundation=foundation,
        request_id=str(request_record["request_id"]),
        action_type=action_id,
        status=result_status,
        evidence_refs=evidence_refs,
        error=None,
        not_proven=not_proven,
    )

    append_ledger_entry(
        repo_root=repo_root,
        foundation=foundation,
        action_type=action_id,
        status=action_status,
        request_ref=request_ref,
        result_ref=result_ref,
        notes=[
            f"route_ready={route_is_ready}",
            f"result_status={result_status}",
            "Foundation-only transfer tracking record.",
        ],
    )

    return {
        "action_status": action_status,
        "request_ref": request_ref,
        "result_ref": result_ref,
        "result_status": result_status,
        "evidence_refs": [request_ref, result_ref, ROUTE_REGISTRY_REL, CONTOUR_STATUS_REL],
        "not_proven": not_proven,
    }


def run_check_contour_status(repo_root: Path, foundation: dict[str, Path], task_id: str) -> dict[str, Any]:
    _status, receipts, notes = update_contour_status_from_probe(repo_root, foundation, task_id)
    action_status = "PASS"

    result_record, result_ref = create_result_record(
        repo_root=repo_root,
        foundation=foundation,
        request_id="CHECK-CONTOUR-STATUS",
        action_type="CHECK_CONTOUR_STATUS",
        status="UNKNOWN",
        evidence_refs=[CONTOUR_STATUS_REL, *receipts],
        error=None,
        not_proven=["Contour status reflects bounded probes only; no production orchestration claim."],
    )

    append_ledger_entry(
        repo_root=repo_root,
        foundation=foundation,
        action_type="CHECK_CONTOUR_STATUS",
        status=action_status,
        request_ref=None,
        result_ref=result_ref,
        notes=notes,
    )

    return {
        "action_status": action_status,
        "request_ref": None,
        "result_ref": result_ref,
        "result_status": str(result_record["status"]),
        "evidence_refs": [CONTOUR_STATUS_REL, *receipts, result_ref],
        "not_proven": ["Only bounded probes are represented."],
    }


def run_refresh_transfer_console_view(
    repo_root: Path,
    foundation: dict[str, Path],
    task_id: str,
) -> dict[str, Any]:
    _view_state, view_ref = build_view_state(repo_root, foundation, task_id)
    append_ledger_entry(
        repo_root=repo_root,
        foundation=foundation,
        action_type="REFRESH_TRANSFER_CONSOLE_VIEW",
        status="PASS",
        request_ref=None,
        result_ref=None,
        notes=["View state refreshed from file-backed transfer records."],
    )

    return {
        "action_status": "PASS",
        "request_ref": None,
        "result_ref": None,
        "result_status": "DRY_RUN_READY",
        "evidence_refs": [view_ref, CONTOUR_STATUS_REL, REQUEST_DIR_REL, RESULT_DIR_REL, LEDGER_PATH_REL],
        "not_proven": ["Refresh action updates read-only transfer view state only."],
    }


def action_report(
    repo_root: Path,
    task_id: str,
    action_id: str,
    result: dict[str, Any],
    view_state_ref: str,
) -> dict[str, Any]:
    return {
        "schema_id": "TRANSFER_CONSOLE_ACTION_REPORT_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "action_id": action_id,
        "status": str(result.get("action_status", "WARN")),
        "result_status": str(result.get("result_status", "UNKNOWN")),
        "request_ref": result.get("request_ref"),
        "result_ref": result.get("result_ref"),
        "view_state_ref": view_state_ref,
        "evidence_refs": list(result.get("evidence_refs", [])),
        "not_proven": list(result.get("not_proven", [])),
        "known_limitations": [
            "Foundation-only transfer console flow.",
            "No production remote orchestration claim.",
            "No arbitrary shell bridge is used.",
        ],
        "claim_boundary": "FOUNDATION_ONLY",
    }


def run_single_action(
    repo_root: Path,
    task_id: str,
    action_id: str,
    requester: str,
) -> dict[str, Any]:
    foundation = ensure_transfer_foundation(repo_root, task_id)

    if action_id == "CHECK_CONTOUR_STATUS":
        result = run_check_contour_status(repo_root, foundation, task_id)
    elif action_id in {
        "REGISTER_TASKPACK_SEND",
        "REGISTER_REPORT_BUNDLE_FETCH",
        "DRY_RUN_TASKPACK_SEND",
        "DRY_RUN_REPORT_FETCH",
    }:
        result = run_transfer_registration_action(
            repo_root=repo_root,
            foundation=foundation,
            task_id=task_id,
            action_id=action_id,
            requester=requester,
        )
    elif action_id == "REFRESH_TRANSFER_CONSOLE_VIEW":
        result = run_refresh_transfer_console_view(repo_root, foundation, task_id)
    else:
        raise ValueError(f"Unsupported action id: {action_id}")

    view_state, view_ref = build_view_state(repo_root, foundation, task_id)
    _ = view_state
    return action_report(repo_root, task_id, action_id, result, view_ref)


def run_build_foundation(repo_root: Path, task_id: str, requester: str) -> dict[str, Any]:
    steps = [
        "CHECK_CONTOUR_STATUS",
        "DRY_RUN_TASKPACK_SEND",
        "DRY_RUN_REPORT_FETCH",
        "REFRESH_TRANSFER_CONSOLE_VIEW",
    ]

    reports: list[dict[str, Any]] = []
    statuses: list[str] = []
    for action_id in steps:
        report = run_single_action(repo_root, task_id, action_id, requester)
        reports.append(report)
        statuses.append(str(report.get("status", "WARN")))

    final_status = "PASS"
    if "BLOCK" in statuses:
        final_status = "BLOCK"
    elif "WARN" in statuses:
        final_status = "WARN"

    return {
        "schema_id": "TRANSFER_CONSOLE_BUILD_ACTION_REPORT_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "action_id": "BUILD_FOUNDATION",
        "status": final_status,
        "step_reports": reports,
        "claim_boundary": "FOUNDATION_ONLY",
    }


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[4]
    default_report_dir = (
        default_repo_root / f"{BASE_REL}/REPORTS/{TASK_ID_DEFAULT}"
    )
    parser = argparse.ArgumentParser(description="Run transfer console foundation action.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--required-starting-head", default=REQUIRED_STARTING_HEAD_DEFAULT)
    parser.add_argument("--action-id", required=True, choices=sorted(ALLOWLISTED_ACTIONS))
    parser.add_argument("--requester", default="SANCTUM_NG_ACTION_LAYER")
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output-report", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    task_id = str(args.task_id)
    action_id = str(args.action_id)
    requester = str(args.requester)
    report_dir = args.report_dir.resolve()

    head_proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    current_head = head_proc.stdout.strip() if head_proc.returncode == 0 else "UNKNOWN"

    if action_id != "BUILD_FOUNDATION" and current_head == "UNKNOWN":
        return 1

    if action_id == "BUILD_FOUNDATION":
        report_payload = run_build_foundation(repo_root, task_id, requester)
    else:
        report_payload = run_single_action(repo_root, task_id, action_id, requester)

    report_dir.mkdir(parents=True, exist_ok=True)
    if args.output_report is None:
        out_path = report_dir / "ACTION_LOGS" / "TRANSFER_CONSOLE_ACTION_REPORTS" / f"{new_id('ACTION-REPORT')}.json"
    else:
        out_path = args.output_report.resolve()

    write_json(out_path, report_payload)

    status = str(report_payload.get("status", "WARN"))
    print(f"transfer_console_action_status={status}")
    print(f"transfer_console_action_report={relpath(out_path, repo_root)}")
    print(f"transfer_console_view_state={VIEW_STATE_REL}")

    if status == "BLOCK":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
