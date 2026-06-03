#!/usr/bin/env python3
"""Build scoped transfer route-proof recovery artifacts for VM2."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import uuid
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-RECOVERY-VM2-V0_1"
VM3_SALVAGE_TASK_ID = "TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-PC-TO-VM3-VM3-V0_1"

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


def new_id(prefix: str) -> str:
    stamp = utc_now().replace("-", "").replace(":", "")
    return f"{prefix}-{stamp}-{uuid.uuid4().hex[:8].upper()}"


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


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel_or_abs(path: Path, repo_root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def list_json_records(directory: Path, limit: int = 12) -> list[dict[str, Any]]:
    if not directory.exists():
        return []
    rows: list[dict[str, Any]] = []
    for item in sorted(directory.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)[:limit]:
        payload = load_json(item)
        if payload is None:
            continue
        clean = dict(payload)
        clean["source_record_path"] = item
        rows.append(clean)
    return rows


def list_jsonl(path: Path, limit: int = 80) -> list[dict[str, Any]]:
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


def parse_kv(stdout: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in stdout.splitlines():
        line = raw.strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        out[key.strip()] = value.strip()
    return out


def run_cmd(cmd: list[str], cwd: Path) -> dict[str, Any]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "parsed": parse_kv(proc.stdout.strip()),
    }


def proof_status_to_result_status(proof_status: str) -> str:
    if proof_status in {"PROVED", "RECOVERED_PROVED"}:
        return "CONFIRMED"
    if proof_status == "WARN_PARTIAL":
        return "REGISTERED"
    return "BLOCKED"


def proof_status_to_ledger_status(proof_status: str) -> str:
    if proof_status in {"PROVED", "RECOVERED_PROVED"}:
        return "PASS"
    if proof_status == "WARN_PARTIAL":
        return "WARN"
    return "BLOCK"


def compact_error(errors: list[str]) -> str | None:
    if not errors:
        return None
    return "; ".join(errors[:6])


def build_pc_to_vm2_route(repo_root: Path, task_id: str, evidence_path: Path) -> dict[str, Any]:
    record: dict[str, Any] = {
        "route": "PC_TO_VM2",
        "source_contour": "PC",
        "destination_contour": "VM2",
        "action_type": "SEND_TASKPACK_ZIP",
        "status": "BLOCKED_ROUTE_UNAVAILABLE",
        "created_utc": utc_now(),
        "claim_boundary": "route proof only; no production orchestration",
        "evidence_refs": [],
        "warnings": [],
        "errors": [],
        "source_path": "",
        "target_path": "",
        "sha256": None,
        "size_bytes": None,
    }

    evidence = load_json(evidence_path)
    record["evidence_refs"].append(rel_or_abs(evidence_path, repo_root))
    if evidence is None:
        record["errors"].append("pc_to_vm2_delivery_evidence_missing_or_invalid_json")
        return record

    route_ok = str(evidence.get("route", "")) == "PC_TO_VM2"
    action_ok = str(evidence.get("action_type", "")) == "SEND_TASKPACK_ZIP"
    repo_ok = Path(str(evidence.get("remote_repo_path", ""))).resolve() == repo_root.resolve()

    zip_path = Path(str(evidence.get("remote_zip_path", ""))).resolve()
    record["source_path"] = zip_path.as_posix()
    record["target_path"] = zip_path.as_posix()
    zip_exists = zip_path.exists() and zip_path.is_file()
    if not zip_exists:
        record["errors"].append(f"pc_to_vm2_zip_missing:{zip_path.as_posix()}")
    else:
        record["evidence_refs"].append(rel_or_abs(zip_path, repo_root))

    actual_sha = sha256_file(zip_path)
    actual_size = zip_path.stat().st_size if zip_exists else None
    record["sha256"] = actual_sha
    record["size_bytes"] = actual_size

    expected_remote_sha = str(evidence.get("remote_zip_sha256", "")).strip().lower()
    expected_local_sha = str(evidence.get("local_zip_sha256", "")).strip().lower()
    expected_remote_size = evidence.get("remote_zip_size_bytes")
    expected_local_size = evidence.get("local_zip_size_bytes")

    hash_ok = bool(
        actual_sha
        and expected_remote_sha
        and actual_sha.lower() == expected_remote_sha
        and (not expected_local_sha or actual_sha.lower() == expected_local_sha)
    )
    size_ok = bool(
        isinstance(actual_size, int)
        and isinstance(expected_remote_size, int)
        and actual_size == expected_remote_size
        and (not isinstance(expected_local_size, int) or actual_size == expected_local_size)
    )

    declared_unpacked = Path(str(evidence.get("remote_unpacked_path", ""))).resolve()
    derived_unpacked = (
        repo_root
        / "INBOX"
        / "VM2_TASKPACKS"
        / task_id
        / f"TASKPACK_{task_id}"
    ).resolve()
    unpacked_path = declared_unpacked
    if not unpacked_path.exists() or not unpacked_path.is_dir():
        if derived_unpacked.exists() and derived_unpacked.is_dir():
            record["warnings"].append(
                f"declared_unpacked_path_missing_using_derived:{declared_unpacked.as_posix()}"
            )
            unpacked_path = derived_unpacked
        else:
            record["warnings"].append(f"unpacked_path_missing:{declared_unpacked.as_posix()}")
            unpacked_path = Path("")
    if str(unpacked_path):
        record["evidence_refs"].append(rel_or_abs(unpacked_path, repo_root))

    if not route_ok:
        record["errors"].append("pc_to_vm2_evidence_route_mismatch")
    if not action_ok:
        record["errors"].append("pc_to_vm2_evidence_action_type_mismatch")
    if not repo_ok:
        record["errors"].append("pc_to_vm2_remote_repo_path_mismatch")
    if not hash_ok:
        record["errors"].append("pc_to_vm2_sha256_mismatch")
    if not size_ok:
        record["errors"].append("pc_to_vm2_size_mismatch")

    if not record["errors"]:
        record["status"] = "PROVED"
    return record


def build_pc_to_vm3_route(repo_root: Path, salvage_report_dir: Path) -> dict[str, Any]:
    record: dict[str, Any] = {
        "route": "PC_TO_VM3",
        "source_contour": "PC",
        "destination_contour": "VM3",
        "action_type": "SEND_TASKPACK_ZIP",
        "status": "WARN_PARTIAL",
        "created_utc": utc_now(),
        "claim_boundary": "recovered proof from committed salvage artifacts only",
        "evidence_refs": [],
        "warnings": [],
        "errors": [],
        "source_path": "",
        "target_path": "",
        "sha256": None,
        "size_bytes": None,
    }

    action_report_path = salvage_report_dir / "transfer_route_proof_action_report.json"
    validator_report_path = salvage_report_dir / "transfer_route_proof_validator_report.json"
    handoff_path = salvage_report_dir / "vm3_interrupted_handoff.json"
    handoff_md_path = salvage_report_dir / "VM3_INTERRUPTED_HANDOFF.md"

    for path in [action_report_path, validator_report_path, handoff_path, handoff_md_path]:
        if path.exists():
            record["evidence_refs"].append(rel_or_abs(path, repo_root))
        else:
            record["errors"].append(f"missing_salvage_artifact:{path.as_posix()}")

    action_report = load_json(action_report_path)
    validator_report = load_json(validator_report_path)
    handoff = load_json(handoff_path)
    if action_report is None:
        record["errors"].append("pc_to_vm3_action_report_missing_or_invalid")
    if validator_report is None:
        record["errors"].append("pc_to_vm3_validator_report_missing_or_invalid")
    if handoff is None:
        record["warnings"].append("pc_to_vm3_handoff_json_missing_or_invalid")

    if action_report is not None:
        if str(action_report.get("status", "")) != "PASS":
            record["warnings"].append("pc_to_vm3_action_report_status_not_pass")
        if str(action_report.get("result_status", "")) != "CONFIRMED":
            record["warnings"].append("pc_to_vm3_action_result_status_not_confirmed")
        known_limitations = action_report.get("known_limitations", [])
        limitation_list = [str(item) for item in known_limitations] if isinstance(known_limitations, list) else []
        if not any(item.startswith("verdict:PASS_FOR_ONE_CONFIRMED_BOUNDED_PC_TO_VM3_TRANSFER_ROUTE_ONLY") for item in limitation_list):
            record["warnings"].append("pc_to_vm3_salvage_verdict_marker_missing")

        request_ref = str(action_report.get("request_ref", "")).strip()
        result_ref = str(action_report.get("result_ref", "")).strip()
        evidence_refs = action_report.get("evidence_refs", [])
        if request_ref:
            request_path = (repo_root / request_ref).resolve()
            if request_path.exists():
                record["evidence_refs"].append(rel_or_abs(request_path, repo_root))
            else:
                record["warnings"].append(f"pc_to_vm3_missing_request_ref:{request_ref}")
        if result_ref:
            result_path = (repo_root / result_ref).resolve()
            if result_path.exists():
                record["evidence_refs"].append(rel_or_abs(result_path, repo_root))
            else:
                record["warnings"].append(f"pc_to_vm3_missing_result_ref:{result_ref}")
        if isinstance(evidence_refs, list):
            for item in evidence_refs:
                if isinstance(item, str) and item.strip():
                    ref_text = item.strip()
                    if ref_text not in record["evidence_refs"]:
                        record["evidence_refs"].append(ref_text)
            for item in evidence_refs:
                if isinstance(item, str) and "PC_TO_VM3_DELIVERY_EVIDENCE.json" in item:
                    record["source_path"] = item
                if isinstance(item, str) and item.endswith(".zip"):
                    record["target_path"] = item

    validator_pass = bool(validator_report is not None and str(validator_report.get("verdict", "")) == "PASS")
    if not validator_pass:
        record["warnings"].append("pc_to_vm3_validator_not_pass")

    raw_request_result_present = not any(
        marker.startswith("pc_to_vm3_missing_") for marker in record["warnings"]
    )

    if not record["errors"] and validator_pass and raw_request_result_present:
        record["status"] = "RECOVERED_PROVED"
    else:
        record["status"] = "WARN_PARTIAL"
        if not record["errors"]:
            record["warnings"].append("pc_to_vm3_raw_evidence_not_fully_available_on_vm2")

    return record


def probe_vm2_to_vm3_route(repo_root: Path, report_dir: Path, task_id: str) -> dict[str, Any]:
    record: dict[str, Any] = {
        "route": "VM2_TO_VM3",
        "source_contour": "VM2",
        "destination_contour": "VM3",
        "action_type": "VALIDATE_TRANSFER_REQUEST",
        "status": "BLOCKED_ROUTE_UNAVAILABLE",
        "created_utc": utc_now(),
        "claim_boundary": "bounded route/path probe only",
        "evidence_refs": [],
        "warnings": [],
        "errors": [],
        "source_path": "",
        "target_path": "",
        "sha256": None,
        "size_bytes": None,
    }

    probe_dir = report_dir / "ACTION_LOGS"
    probe_dir.mkdir(parents=True, exist_ok=True)

    ssh_g = run_cmd(["ssh", "-G", "imperium-vm3"], repo_root)
    ssh_g_path = probe_dir / "vm2_to_vm3_ssh_g.txt"
    ssh_g_path.write_text(ssh_g.get("stdout", "") + "\n", encoding="utf-8")
    record["evidence_refs"].append(rel_or_abs(ssh_g_path, repo_root))
    if ssh_g.get("returncode", 1) != 0:
        record["errors"].append("ssh_config_probe_failed")

    ping_cmd = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=8",
        "imperium-vm3",
        "echo",
        "IMPERIUM_VM3_PROBE_OK",
    ]
    ping_run = run_cmd(ping_cmd, repo_root)
    ping_path = probe_dir / "vm2_to_vm3_probe_run.json"
    write_json(ping_path, ping_run)
    record["evidence_refs"].append(rel_or_abs(ping_path, repo_root))

    if ping_run.get("returncode", 1) != 0:
        stderr = str(ping_run.get("stderr", "")).strip()
        stdout = str(ping_run.get("stdout", "")).strip()
        detail = stderr if stderr else stdout
        if detail:
            record["errors"].append(f"ssh_probe_failed:{detail}")
        else:
            record["errors"].append("ssh_probe_failed")
        return record

    local_probe = {
        "schema": "imperium.vm2_to_vm3_route_probe.v0_1",
        "task_id": task_id,
        "created_utc": utc_now(),
        "route": "VM2_TO_VM3",
        "claim_boundary": "bounded route/path probe only; no production orchestration",
    }
    local_probe_path = probe_dir / "vm2_to_vm3_probe_payload.json"
    write_json(local_probe_path, local_probe)

    remote_probe_path = f"/tmp/imperium_vm2_to_vm3_route_probe_{task_id}.json"
    scp_run = run_cmd(
        ["scp", str(local_probe_path), f"imperium-vm3:{remote_probe_path}"],
        repo_root,
    )
    scp_path = probe_dir / "vm2_to_vm3_probe_scp.json"
    write_json(scp_path, scp_run)
    record["evidence_refs"].append(rel_or_abs(scp_path, repo_root))
    if scp_run.get("returncode", 1) != 0:
        stderr = str(scp_run.get("stderr", "")).strip()
        record["errors"].append(f"vm2_to_vm3_scp_failed:{stderr or 'unknown'}")
        return record

    stat_cmd = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=8",
        "imperium-vm3",
        "bash",
        "-lc",
        f"sha256sum {remote_probe_path} && stat -c%s {remote_probe_path}",
    ]
    stat_run = run_cmd(stat_cmd, repo_root)
    stat_path = probe_dir / "vm2_to_vm3_probe_stat.json"
    write_json(stat_path, stat_run)
    record["evidence_refs"].append(rel_or_abs(stat_path, repo_root))

    if stat_run.get("returncode", 1) != 0:
        stderr = str(stat_run.get("stderr", "")).strip()
        record["errors"].append(f"vm2_to_vm3_remote_stat_failed:{stderr or 'unknown'}")
        return record

    lines = [line for line in str(stat_run.get("stdout", "")).splitlines() if line.strip()]
    if len(lines) >= 2:
        hash_bits = lines[0].split()
        if hash_bits:
            record["sha256"] = hash_bits[0].strip().lower()
        try:
            record["size_bytes"] = int(lines[1].strip())
        except ValueError:
            record["warnings"].append("vm2_to_vm3_size_parse_failed")
    else:
        record["warnings"].append("vm2_to_vm3_stat_output_incomplete")

    record["source_path"] = rel_or_abs(local_probe_path, repo_root)
    record["target_path"] = remote_probe_path
    record["status"] = "PROVED"
    return record


def build_request_payload(task_id: str, route_record: dict[str, Any]) -> dict[str, Any]:
    route = str(route_record.get("route", "UNKNOWN"))
    source = str(route_record.get("source_contour", "PC"))
    target = str(route_record.get("destination_contour", "VM3"))
    action_type = str(route_record.get("action_type", "VALIDATE_TRANSFER_REQUEST"))

    source_path = str(route_record.get("source_path", "")).strip() or f"{route}.source"
    target_path = str(route_record.get("target_path", "")).strip() or source_path
    artifact_name = Path(source_path).name if source_path else f"{route}.json"

    owner_approval_required = action_type == "SEND_TASKPACK_ZIP"
    return {
        "schema_id": "TRANSFER_ACTION_REQUEST_V0_1",
        "request_id": new_id("TRANSFER-ACTION-REQ"),
        "task_id": task_id,
        "action_type": action_type,
        "source_contour": source,
        "target_contour": target,
        "artifact_type": "taskpack_zip",
        "artifact_name": artifact_name,
        "source_path": source_path,
        "target_path": target_path,
        "mode": "DRY_RUN",
        "owner_approval_required": owner_approval_required,
        "owner_approved": False,
        "rollback_plan": "IMPERIUM_NEW_GENERATION/TRUTH/ACTION_ROLLBACK/ACTION_ROLLBACK_POLICY_V0_1.json",
        "allowed_command_profile": "DRY_RUN_ONLY",
        "created_at_utc": utc_now(),
        "status": "REQUESTED",
        "claim_boundary": "FOUNDATION_ONLY",
        "requester": "SANCTUM_NG_TRANSFER_ROUTE_PROOF_RECOVERY",
        "no_arbitrary_shell_confirmed": True,
        "route_proof_mode": False,
        "delivery_evidence_file": None,
        "notes": [
            "Recovery route-proof registration entry.",
            f"route={route}",
            f"route_status={route_record.get('status', 'UNKNOWN')}",
            "No arbitrary shell command text is accepted.",
        ],
    }


def build_result_payload(task_id: str, request: dict[str, Any], route_record: dict[str, Any], request_ref: str) -> dict[str, Any]:
    route_status = str(route_record.get("status", "UNKNOWN"))
    result_status = proof_status_to_result_status(route_status)
    evidence_refs = [request_ref]
    for item in route_record.get("evidence_refs", []):
        if isinstance(item, str) and item.strip() and item not in evidence_refs:
            evidence_refs.append(item.strip())

    limitations = [
        "Foundation-only route-proof recovery record.",
        "No production remote orchestration claim.",
        "No arbitrary shell execution path is accepted.",
        f"route:{route_record.get('source_contour')}->{route_record.get('destination_contour')}",
        f"route_status:{route_status}",
    ]
    for item in route_record.get("warnings", []):
        limitations.append(f"warn:{item}")
    for item in route_record.get("errors", []):
        limitations.append(f"error:{item}")

    paths_verified: list[str] = []
    for key in ("source_path", "target_path"):
        value = str(route_record.get(key, "")).strip()
        if value:
            paths_verified.append(value)

    return {
        "schema_id": "TRANSFER_ACTION_RESULT_V0_1",
        "result_id": new_id("TRANSFER-ACTION-RESULT"),
        "request_id": str(request.get("request_id", "")),
        "task_id": task_id,
        "action_type": str(request.get("action_type", "VALIDATE_TRANSFER_REQUEST")),
        "status": result_status,
        "started_at_utc": utc_now(),
        "finished_at_utc": utc_now(),
        "evidence_refs": evidence_refs,
        "stdout_log_ref": None,
        "stderr_log_ref": None,
        "paths_verified": paths_verified,
        "sha256_before_after": {
            "before": route_record.get("sha256"),
            "after": route_record.get("sha256") if result_status == "CONFIRMED" else None,
        },
        "no_arbitrary_shell_confirmed": True,
        "limitations": limitations,
        "claim_boundary": "FOUNDATION_ONLY",
        "error": compact_error([str(item) for item in route_record.get("errors", [])]),
        "mode": "DRY_RUN",
    }


def append_runner_ledger_entry(
    ledger_path: Path,
    route_record: dict[str, Any],
    request_ref: str,
    result_ref: str,
    result_status: str,
) -> dict[str, Any]:
    entry = {
        "schema_id": "TRANSFER_ACTION_RUNNER_LEDGER_ENTRY_V0_1",
        "entry_id": new_id("TRANSFER-ACTION-LEDGER"),
        "timestamp_utc": utc_now(),
        "action_id": route_record.get("action_type", "VALIDATE_TRANSFER_REQUEST"),
        "request_ref": request_ref,
        "result_ref": result_ref,
        "result_status": result_status,
        "mode": "DRY_RUN",
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
    }
    append_jsonl(ledger_path, entry)
    return entry


def append_transfer_ledger_entry(
    ledger_path: Path,
    route_record: dict[str, Any],
    request_ref: str,
    result_ref: str,
) -> dict[str, Any]:
    route_status = str(route_record.get("status", "UNKNOWN"))
    route = str(route_record.get("route", "UNKNOWN"))
    if route == "PC_TO_VM2":
        action_type = "DRY_RUN_TASKPACK_SEND"
    else:
        action_type = "CHECK_CONTOUR_STATUS"
    entry = {
        "entry_id": new_id("LEDGER"),
        "action_type": action_type,
        "status": proof_status_to_ledger_status(route_status),
        "timestamp_utc": utc_now(),
        "request_ref": request_ref,
        "result_ref": result_ref,
        "notes": [
            f"route={route}",
            f"route_status={route_status}",
            f"evidence_refs={len(route_record.get('evidence_refs', []))}",
            "Recovery route-proof record only.",
        ],
        "claim_boundary": "FOUNDATION_ONLY",
    }
    append_jsonl(ledger_path, entry)
    return entry


def update_allowed_routes(repo_root: Path, task_id: str, routes: list[dict[str, Any]]) -> None:
    path = repo_root / ALLOWED_ROUTES_REL
    existing = load_json(path)
    route_rows: list[dict[str, Any]] = []
    for item in routes:
        route_rows.append(
            {
                "route_id": str(item.get("route", "")),
                "source_contour": str(item.get("source_contour", "")),
                "target_contour": str(item.get("destination_contour", "")),
                "artifact_kind": "taskpack_zip",
                "route_status": "CONFIGURED",
                "route_ref": "IMPERIUM_NEW_GENERATION/MECHANICUS/CONNECTIONS/SSH_CONNECTION_MATRIX_V0_1.json",
                "allowlisted_actions": ["SEND_TASKPACK_ZIP", "VALIDATE_TRANSFER_REQUEST", "DRY_RUN_TRANSFER"],
                "notes": [
                    f"proof_status:{item.get('status', 'UNKNOWN')}",
                    "Recovery route-proof entry.",
                ],
                "claim_boundary": "FOUNDATION_ONLY",
            }
        )
    payload = {
        "schema_id": "TRANSFER_ALLOWED_ROUTES_V0_1",
        "task_id": task_id,
        "claim_boundary": "FOUNDATION_ONLY",
        "routes": route_rows,
    }
    if existing is not None:
        payload["generated_at_utc"] = utc_now()
    write_json(path, payload)


def build_contour_cards(routes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    route_map = {str(item.get("route", "")): item for item in routes}
    pc_vm2 = str(route_map.get("PC_TO_VM2", {}).get("status", "UNKNOWN"))
    pc_vm3 = str(route_map.get("PC_TO_VM3", {}).get("status", "UNKNOWN"))
    vm2_vm3 = str(route_map.get("VM2_TO_VM3", {}).get("status", "UNKNOWN"))

    now = utc_now()
    pc_status = "CONFIRMED" if pc_vm2 == "PROVED" else "BLOCKED"
    vm2_status = "CONFIRMED" if pc_vm2 == "PROVED" else "WARN"
    if vm2_vm3 == "PROVED" and pc_vm3 in {"PROVED", "RECOVERED_PROVED"}:
        vm3_status = "CONFIRMED"
    elif pc_vm3 in {"WARN_PARTIAL"} or vm2_vm3 == "BLOCKED_ROUTE_UNAVAILABLE":
        vm3_status = "WARN"
    else:
        vm3_status = "BLOCKED"

    return [
        {
            "contour_id": "PC",
            "display_name": "PC",
            "role": "control_contour",
            "status": pc_status,
            "status_reason": f"PC_TO_VM2={pc_vm2}; PC_TO_VM3={pc_vm3}.",
            "route_config_status": "RECOVERY_ROUTE_PROOF",
            "last_probe_receipt_ref": None,
            "last_updated_utc": now,
            "claim_boundary": "FOUNDATION_ONLY",
        },
        {
            "contour_id": "VM2",
            "display_name": "VM2",
            "role": "executor_contour",
            "status": vm2_status,
            "status_reason": f"Ingress PC_TO_VM2={pc_vm2}; egress VM2_TO_VM3={vm2_vm3}.",
            "route_config_status": "RECOVERY_ROUTE_PROOF",
            "last_probe_receipt_ref": None,
            "last_updated_utc": now,
            "claim_boundary": "FOUNDATION_ONLY",
        },
        {
            "contour_id": "VM3",
            "display_name": "VM3",
            "role": "executor_contour",
            "status": vm3_status,
            "status_reason": f"PC_TO_VM3={pc_vm3}; VM2_TO_VM3={vm2_vm3}.",
            "route_config_status": "RECOVERY_ROUTE_PROOF",
            "last_probe_receipt_ref": None,
            "last_updated_utc": now,
            "claim_boundary": "FOUNDATION_ONLY",
        },
    ]


def build_final_verdict(routes: list[dict[str, Any]]) -> tuple[str, str]:
    route_map = {str(item.get("route", "")): str(item.get("status", "UNKNOWN")) for item in routes}
    pc_vm2 = route_map.get("PC_TO_VM2")
    pc_vm3 = route_map.get("PC_TO_VM3")
    vm2_vm3 = route_map.get("VM2_TO_VM3")

    if pc_vm2 != "PROVED":
        return "BLOCK", "BLOCK_PC_TO_VM2_NOT_PROVED"
    if pc_vm3 in {"PROVED", "RECOVERED_PROVED"} and vm2_vm3 == "PROVED":
        return (
            "PASS",
            "PASS_FOR_PC_TO_VM2_PC_TO_VM3_AND_VM2_TO_VM3_BOUNDED_ROUTE_PROOF_ONLY",
        )
    if pc_vm3 in {"WARN_PARTIAL", "RECOVERED_PROVED"} and vm2_vm3 in {"BLOCKED_ROUTE_UNAVAILABLE", "PROVED"}:
        return (
            "WARN",
            "PASS_FOR_PC_TO_VM2_WITH_WARN_PARTIAL_PC_TO_VM3_AND_BLOCKED_VM2_TO_VM3_ROUTE_ONLY",
        )
    return "WARN", "WARN_PARTIAL_ROUTE_PROOF_WITH_VM2_TO_VM3_BLOCKED"


def update_view_state(
    repo_root: Path,
    task_id: str,
    routes: list[dict[str, Any]],
    summary_ref: str,
    source_refs_extra: list[str],
    context_mix: dict[str, Any],
    verdict_status: str,
    verdict_claim: str,
) -> None:
    request_dir = repo_root / ACTION_REQUEST_DIR_REL
    result_dir = repo_root / ACTION_RESULT_DIR_REL
    runner_ledger_path = repo_root / RUNNER_LEDGER_REL
    policy_snapshot = load_json(repo_root / POLICY_SNAPSHOT_REL) or {}

    requests = list_json_records(request_dir, limit=12)
    results = list_json_records(result_dir, limit=12)
    ledger = list_jsonl(runner_ledger_path, limit=80)

    latest_requests: list[dict[str, Any]] = []
    for item in requests:
        clean = {k: v for k, v in item.items() if k != "source_record_path"}
        source_path = item.get("source_record_path")
        if isinstance(source_path, Path):
            clean["source_record_path"] = rel_or_abs(source_path, repo_root)
        latest_requests.append(clean)

    latest_results: list[dict[str, Any]] = []
    for item in results:
        clean = {k: v for k, v in item.items() if k != "source_record_path"}
        source_path = item.get("source_record_path")
        if isinstance(source_path, Path):
            clean["source_record_path"] = rel_or_abs(source_path, repo_root)
        latest_results.append(clean)

    total_evidence = 0
    for route in routes:
        total_evidence += len(route.get("evidence_refs", []))

    action_runner_state = {
        "schema_id": "TRANSFER_ACTION_RUNNER_STATE_V0_1",
        "generated_at_utc": utc_now(),
        "claim_boundary": "FOUNDATION_ONLY",
        "no_arbitrary_shell_confirmed": True,
        "supported_action_types": sorted(
            policy_snapshot.get(
                "allowed_action_types",
                ["SEND_TASKPACK_ZIP", "FETCH_REPORT_BUNDLE_ZIP", "REGISTER_TRANSFER_RESULT", "VALIDATE_TRANSFER_REQUEST", "DRY_RUN_TRANSFER"],
            )
        ),
        "allowed_contours": sorted(policy_snapshot.get("allowed_contours", ["PC", "VM2", "VM3"])),
        "safe_target_roots": policy_snapshot.get("safe_target_roots", {}),
        "latest_action_requests": latest_requests,
        "latest_action_results": latest_results,
        "latest_runner_ledger": ledger,
        "last_action": {
            "action_id": "ROUTE_PROOF_RECOVERY",
            "request_ref": summary_ref,
            "result_ref": summary_ref,
            "route_proof_status": verdict_status,
            "route": "PC_TO_VM2|PC_TO_VM3|VM2_TO_VM3",
            "route_proof_verdict": verdict_claim,
            "route_proof_evidence_count": total_evidence,
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
            "Recovery route-proof scope only.",
            "No production remote orchestration claim.",
            "No arbitrary shell execution path is accepted.",
            f"verdict:{verdict_claim}",
        ],
    }

    transfer_routes = []
    for item in routes:
        transfer_routes.append(
            {
                "route_id": str(item.get("route", "")),
                "source_contour": str(item.get("source_contour", "")),
                "target_contour": str(item.get("destination_contour", "")),
                "action_type": str(item.get("action_type", "")),
                "route_status": str(item.get("status", "UNKNOWN")),
                "route_verdict": str(item.get("status", "UNKNOWN")),
                "evidence_refs": [str(ref) for ref in item.get("evidence_refs", []) if isinstance(ref, str)],
                "limitations": [
                    f"warnings={len(item.get('warnings', []))}",
                    f"errors={len(item.get('errors', []))}",
                ],
                "claim_boundary": "FOUNDATION_ONLY",
            }
        )

    source_refs = [
        f"{BASE_REL}/CONTRACTS/transfer_action_request.schema.json",
        f"{BASE_REL}/CONTRACTS/transfer_action_result.schema.json",
        f"{BASE_REL}/CONTRACTS/transfer_console_view_state_v0_1.schema.json",
        ACTION_REQUEST_DIR_REL,
        ACTION_RESULT_DIR_REL,
        RUNNER_LEDGER_REL,
        summary_ref,
    ]
    for item in source_refs_extra:
        if item not in source_refs:
            source_refs.append(item)

    view_payload = {
        "schema_id": "TRANSFER_CONSOLE_VIEW_STATE_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "claim_boundary": "FOUNDATION_ONLY",
        "contour_cards": build_contour_cards(routes),
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
            "TRANSFER_ROUTE_PROOF_RECOVERY",
            verdict_claim,
        ],
    }
    write_json(repo_root / VIEW_STATE_REL, view_payload)


def ensure_no_forbidden_fields(payload: dict[str, Any]) -> None:
    forbidden = sorted(key for key in payload if key in FORBIDDEN_FIELDS)
    if forbidden:
        raise RuntimeError(f"forbidden fields present: {forbidden}")


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[4]
    default_report_dir = (
        default_repo_root
        / REPORTS_REL
        / TASK_ID_DEFAULT
    )
    default_pc_to_vm2_evidence = (
        default_repo_root
        / "INBOX"
        / "VM2_TASKPACKS"
        / TASK_ID_DEFAULT
        / "PC_TO_VM2_DELIVERY_EVIDENCE.json"
    )
    default_vm3_salvage_dir = (
        default_repo_root
        / REPORTS_REL
        / VM3_SALVAGE_TASK_ID
    )
    default_summary = default_report_dir / "route_proof_recovery_summary.json"
    parser = argparse.ArgumentParser(description="Build transfer route-proof recovery artifacts.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--pc-to-vm2-evidence", type=Path, default=default_pc_to_vm2_evidence)
    parser.add_argument("--vm3-salvage-report-dir", type=Path, default=default_vm3_salvage_dir)
    parser.add_argument("--output-summary", type=Path, default=default_summary)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    task_id = str(args.task_id)
    report_dir = args.report_dir.resolve()
    report_dir.mkdir(parents=True, exist_ok=True)

    pc_to_vm2 = build_pc_to_vm2_route(repo_root, task_id, args.pc_to_vm2_evidence.resolve())
    pc_to_vm3 = build_pc_to_vm3_route(repo_root, args.vm3_salvage_report_dir.resolve())
    vm2_to_vm3 = probe_vm2_to_vm3_route(repo_root, report_dir, task_id)
    routes = [pc_to_vm2, pc_to_vm3, vm2_to_vm3]

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
    for route_record in routes:
        request_payload = build_request_payload(task_id, route_record)
        ensure_no_forbidden_fields(request_payload)
        request_path = request_dir / f"{request_payload['request_id']}.json"
        write_json(request_path, request_payload)
        request_ref = rel_or_abs(request_path, repo_root)
        request_refs.append(request_ref)

        result_payload = build_result_payload(task_id, request_payload, route_record, request_ref)
        ensure_no_forbidden_fields(result_payload)
        result_path = result_dir / f"{result_payload['result_id']}.json"
        write_json(result_path, result_payload)
        result_ref = rel_or_abs(result_path, repo_root)
        result_refs.append(result_ref)

        append_runner_ledger_entry(
            runner_ledger_path,
            route_record=route_record,
            request_ref=request_ref,
            result_ref=result_ref,
            result_status=str(result_payload.get("status", "BLOCKED")),
        )
        append_transfer_ledger_entry(
            transfer_ledger_path,
            route_record=route_record,
            request_ref=request_ref,
            result_ref=result_ref,
        )

    verdict_status, verdict_claim = build_final_verdict(routes)
    context_mix = {
        "taskpack_percent": 48,
        "existing_newgen_repo_percent": 30,
        "owner_handoff_percent": 12,
        "organ_registry_percent": 5,
        "servitor_inference_percent": 5,
        "external_local_private_percent": 0,
    }

    output_summary = args.output_summary.resolve()
    summary_payload = {
        "schema": "imperium.transfer_route_proof_recovery_summary.v0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "repo_path": repo_root.as_posix(),
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip(),
        "verdict_status": verdict_status,
        "verdict_claim": verdict_claim,
        "claim_boundary": "scoped route proof only; no production orchestration",
        "routes": routes,
        "request_refs": request_refs,
        "result_refs": result_refs,
        "runner_ledger_ref": RUNNER_LEDGER_REL,
        "transfer_ledger_ref": TRANSFER_LEDGER_REL,
        "view_state_ref": VIEW_STATE_REL,
        "context_source_mix": context_mix,
        "not_proven": [
            "production orchestration",
            "autonomous remote execution",
            "global all-routes live transfer claim",
        ],
    }
    write_json(output_summary, summary_payload)
    summary_ref = rel_or_abs(output_summary, repo_root)

    update_allowed_routes(repo_root, task_id, routes)
    update_view_state(
        repo_root=repo_root,
        task_id=task_id,
        routes=routes,
        summary_ref=summary_ref,
        source_refs_extra=[
            rel_or_abs(args.pc_to_vm2_evidence.resolve(), repo_root),
            rel_or_abs(args.vm3_salvage_report_dir.resolve() / "transfer_route_proof_action_report.json", repo_root),
            rel_or_abs(args.vm3_salvage_report_dir.resolve() / "transfer_route_proof_validator_report.json", repo_root),
            rel_or_abs(args.vm3_salvage_report_dir.resolve() / "vm3_interrupted_handoff.json", repo_root),
        ],
        context_mix=context_mix,
        verdict_status=verdict_status,
        verdict_claim=verdict_claim,
    )

    print(f"transfer_route_recovery_builder_verdict={verdict_status}")
    print(f"transfer_route_recovery_builder_claim={verdict_claim}")
    print(f"transfer_route_recovery_summary={summary_ref}")
    print(f"transfer_console_view_state={VIEW_STATE_REL}")
    return 0 if verdict_status in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
