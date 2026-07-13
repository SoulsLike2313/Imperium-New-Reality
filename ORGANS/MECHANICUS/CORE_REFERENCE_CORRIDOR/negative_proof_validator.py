"""Independent Phase 2 validator: derive actual verdicts from observations only."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


VALIDATOR_ID = "negative_proof_observation_validator_v1"
VALIDATOR_VERSION = "1.0.0"
SCENARIO_SCHEMA = "imperium.core_reference_corridor.negative_scenario_receipt.v1"
OBSERVATION_SCHEMA = "imperium.core_reference_corridor.negative_observation_receipt.v1"
HEX_64 = re.compile(r"^[0-9a-f]{64}$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_hash(value: dict[str, Any], *, omitted: str = "receipt_hash") -> str:
    clone = dict(value)
    clone.pop(omitted, None)
    payload = json.dumps(clone, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _common_integrity(
    receipt: dict[str, Any],
    report_root: Path,
    *,
    task_id: str,
    warp_id: str,
    base_head: str,
) -> tuple[dict[str, bool], str | None]:
    observations = _dict(receipt.get("observations"))
    checks: dict[str, bool] = {
        "scenario_schema": receipt.get("schema_version") == SCENARIO_SCHEMA,
        "observations_present": bool(observations),
        "receipt_hash": receipt.get("receipt_hash") == canonical_hash(receipt),
        "task_binding": receipt.get("task_id") == task_id,
        "warp_binding": receipt.get("warp_id") == warp_id,
        "base_binding": receipt.get("base_head") == base_head,
        "validator_identity": False,
        "expected_source_hash": False,
        "expected_entry_binding": False,
        "observation_evidence_hash": False,
        "observation_receipt_hash": False,
        "observation_binding": False,
        "observer_identity": False,
        "fixture_isolation": False,
        "reality_unchanged": False,
        "warp_outside_scope_unchanged": False,
        "process_outcome_measured": False,
        "failure_localized": False,
    }
    validator = _dict(receipt.get("validator"))
    validator_path = Path(str(validator.get("path", "")))
    if validator.get("id") == VALIDATOR_ID and validator.get("version") == VALIDATOR_VERSION and validator_path.is_file():
        checks["validator_identity"] = validator.get("sha256") == sha256_file(validator_path) == sha256_file(Path(__file__))
    expected_source = _dict(receipt.get("expected_source"))
    expected_path = Path(str(expected_source.get("path", "")))
    if expected_path.is_file() and HEX_64.fullmatch(str(expected_source.get("sha256", ""))):
        checks["expected_source_hash"] = expected_source["sha256"] == sha256_file(expected_path)
        if checks["expected_source_hash"]:
            try:
                catalog = json.loads(expected_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                catalog = {}
            rows = catalog.get("scenarios", []) if isinstance(catalog, dict) else []
            matches = [row for row in rows if isinstance(row, dict) and row.get("scenario_id") == receipt.get("scenario_id")]
            if len(matches) == 1:
                entry = matches[0]
                entry_hash = hashlib.sha256(json.dumps(entry, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
                checks["expected_entry_binding"] = entry_hash == expected_source.get("entry_sha256") and entry.get("expected_verdict") == receipt.get("expected_verdict")
    refs = _list(receipt.get("observation_evidence_refs"))
    if len(refs) == 1 and isinstance(refs[0], dict):
        relative = refs[0].get("path")
        declared_hash = refs[0].get("sha256")
        if isinstance(relative, str) and isinstance(declared_hash, str):
            evidence_path = (report_root / relative).resolve()
            if _within(evidence_path, report_root) and evidence_path.is_file():
                checks["observation_evidence_hash"] = declared_hash == sha256_file(evidence_path)
                try:
                    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    evidence = {}
                if isinstance(evidence, dict):
                    checks["observation_receipt_hash"] = evidence.get("schema_version") == OBSERVATION_SCHEMA and evidence.get("receipt_hash") == canonical_hash(evidence)
                    checks["observation_binding"] = (
                        evidence.get("scenario_id") == receipt.get("scenario_id")
                        and evidence.get("fixture_id") == receipt.get("fixture_id")
                        and evidence.get("observations") == observations
                    )
                    observer = _dict(evidence.get("observer"))
                    observer_path = Path(str(observer.get("path", "")))
                    checks["observer_identity"] = (
                        observer.get("id") == "negative_scenario_observer_v1"
                        and observer.get("version") == "1.0.0"
                        and observer_path.is_file()
                        and observer.get("sha256") == sha256_file(observer_path)
                    )
    boundary = Path(str(observations.get("fixture_boundary", "")))
    fixture = Path(str(observations.get("fixture_root", "")))
    marker_hash = observations.get("fixture_marker_sha256")
    checks["fixture_isolation"] = (
        bool(observations.get("fixture_isolated"))
        and bool(str(boundary))
        and bool(str(fixture))
        and _within(fixture, boundary)
        and fixture.resolve() != boundary.resolve()
        and marker_hash == hashlib.sha256((str(receipt.get("fixture_id")) + "\n").encode("utf-8")).hexdigest()
    )
    before, after = _dict(observations.get("host_reality_before")), _dict(observations.get("host_reality_after"))
    checks["reality_unchanged"] = (
        observations.get("host_reality_changed") is False
        and before.get("reality_head") == after.get("reality_head")
        and before.get("reality_origin_master") == after.get("reality_origin_master")
        and before.get("reality_head") == before.get("reality_origin_master")
        and before.get("reality_status") == after.get("reality_status") == []
    )
    checks["warp_outside_scope_unchanged"] = observations.get("host_warp_changed_outside_scope") is False
    process_started = observations.get("process_started")
    checks["process_outcome_measured"] = process_started is False or (
        process_started is True
        and any(key in observations for key in ("process_exit_code", "validator_exit_code", "termination"))
    )
    checks["failure_localized"] = (
        observations.get("failure_localized") is True
        and isinstance(observations.get("failure_code"), str)
        and isinstance(observations.get("failure_stage"), str)
    )
    precedence = [
        ("observations_present", "NOT_PROVEN_OBSERVATIONS_MISSING"),
        ("scenario_schema", "BLOCK_SCENARIO_SCHEMA_INVALID"),
        ("receipt_hash", "BLOCK_RECEIPT_HASH_MISMATCH"),
        ("validator_identity", "BLOCK_VALIDATOR_IDENTITY_MISMATCH"),
        ("expected_source_hash", "BLOCK_EXPECTED_SOURCE_HASH_MISMATCH"),
        ("observation_evidence_hash", "BLOCK_OBSERVATION_EVIDENCE_HASH_MISMATCH"),
        ("observation_receipt_hash", "BLOCK_OBSERVATION_RECEIPT_HASH_MISMATCH"),
        ("observation_binding", "BLOCK_OBSERVATION_BINDING_MISMATCH"),
        ("observer_identity", "BLOCK_OBSERVER_IDENTITY_MISMATCH"),
        ("task_binding", "BLOCK_SCENARIO_TASK_BINDING_MISMATCH"),
        ("warp_binding", "BLOCK_SCENARIO_WARP_BINDING_MISMATCH"),
        ("base_binding", "BLOCK_SCENARIO_BASE_BINDING_MISMATCH"),
        ("fixture_isolation", "BLOCK_FIXTURE_ISOLATION_NOT_PROVEN"),
        ("reality_unchanged", "BLOCK_HOST_REALITY_CHANGED"),
        ("warp_outside_scope_unchanged", "BLOCK_HOST_WARP_OUTSIDE_SCOPE_CHANGED"),
        ("process_outcome_measured", "NOT_PROVEN_PROCESS_OUTCOME"),
        ("failure_localized", "NOT_PROVEN_FAILURE_LOCALIZATION"),
    ]
    return checks, next((failure for check, failure in precedence if not checks[check]), None)


def derive_actual(scenario_id: str, observations: dict[str, Any]) -> str:
    """Pure scenario rules. No expected verdict is accepted by this function."""
    if scenario_id == "unauthorized_reality_write":
        if observations.get("target_role") == "REALITY" and observations.get("write_attempted") is True and observations.get("write_blocked_before_io") is True and observations.get("target_exists_after") is False:
            return "BLOCK_REALITY_WRITE_PROVEN"
    elif scenario_id == "write_outside_allowed_warp_scope":
        if observations.get("target_outside_allowed_scope") is True and observations.get("write_blocked_before_io") is True and observations.get("target_exists_after") is False:
            return "BLOCK_WARP_SCOPE_PROVEN"
    elif scenario_id == "unregistered_capability":
        if observations.get("capability_registered") is False and observations.get("process_started") is False and observations.get("sentinel_created") is False and observations.get("default_policy") == "DENY":
            return "BLOCK_UNREGISTERED_CAPABILITY_PROVEN"
        if observations.get("capability_registered") is False and observations.get("process_started") is True:
            return "BLOCK_UNKNOWN_CAPABILITY_EXECUTED"
    elif scenario_id == "executable_hash_mismatch":
        if observations.get("hash_match") is False and observations.get("blocked_before_execution") is True and observations.get("process_started") is False and observations.get("sentinel_created") is False:
            return "BLOCK_EXECUTABLE_HASH_MISMATCH_PROVEN"
    elif scenario_id == "timeout":
        termination = _dict(observations.get("termination"))
        if observations.get("timeout_triggered") is True and observations.get("parent_alive_after") is False and termination.get("requested") is True and termination.get("tree_terminated") is True:
            return "BLOCK_TIMEOUT_PROVEN"
    elif scenario_id == "parent_child_grandchild_termination":
        termination = _dict(observations.get("termination"))
        if observations.get("observed_process_depth") == 3 and observations.get("parent_alive_after") is False and observations.get("descendants_alive_after") == [] and termination.get("tree_terminated") is True:
            return "BLOCK_PROCESS_TREE_TERMINATED_PROVEN"
    elif scenario_id == "stale_base_head":
        if observations.get("base_head_match") is False and observations.get("blocked_before_state_change") is True and observations.get("state_unchanged") is True:
            return "BLOCK_STALE_BASE_HEAD_PROVEN"
    elif scenario_id == "dirty_reality":
        if observations.get("subject_reality_dirty") is True and observations.get("blocked_before_warp_create") is True and observations.get("subject_state_unchanged") is True:
            return "BLOCK_DIRTY_REALITY_PROVEN"
    elif scenario_id == "failed_validator":
        if isinstance(observations.get("validator_exit_code"), int) and observations["validator_exit_code"] != 0 and observations.get("validator_rejected") is True:
            return "BLOCK_FAILED_VALIDATOR_PROVEN"
    elif scenario_id == "evidence_tampering":
        if observations.get("evidence_hash_match") is False and observations.get("tamper_detected") is True and observations.get("evidence_rejected") is True:
            return "BLOCK_EVIDENCE_TAMPERING_PROVEN"
    elif scenario_id in {"wrong_task_id", "wrong_warp_id", "wrong_base_head"}:
        if observations.get("binding_match") is False and observations.get("evidence_rejected") is True:
            return {"wrong_task_id": "BLOCK_WRONG_TASK_ID_PROVEN", "wrong_warp_id": "BLOCK_WRONG_WARP_ID_PROVEN", "wrong_base_head": "BLOCK_WRONG_BASE_HEAD_PROVEN"}[scenario_id]
    elif scenario_id == "missing_organ":
        if _list(observations.get("missing_organs")) and observations.get("pass_claim_rejected") is True:
            return "BLOCK_MISSING_ORGAN_PROVEN"  # MUTATION_TARGET_ORGAN_VERDICT
    elif scenario_id == "throne_overclaim":
        if _list(observations.get("critical_blocking_organs")) and observations.get("throne_claim") == "PASS_PROVEN" and observations.get("throne_claim_rejected") is True and observations.get("downgraded_verdict") == "BLOCK":
            return "BLOCK_THRONE_OVERCLAIM_PROVEN"
    elif scenario_id == "direct_legacy_command_attempt":
        if observations.get("command_registered") is False and observations.get("invocation_blocked") is True and observations.get("backend_handler_called") is False:
            return "BLOCK_LEGACY_COMMAND_PROVEN"
    elif scenario_id == "direct_tauri_bypass_attempt":
        if observations.get("corridor_token_present") is False and observations.get("invocation_blocked") is True and observations.get("backend_handler_called") is False:
            return "BLOCK_TAURI_BYPASS_PROVEN"
    elif scenario_id == "parity_mismatch":
        if observations.get("parity_match") is False and (_list(observations.get("missing_in_ui")) or _list(observations.get("unknown_in_ui"))) and observations.get("action_surface_blocked") is True:
            return "BLOCK_PARITY_MISMATCH_PROVEN"
    elif scenario_id == "warp_reject_discard_destroy":
        states = _list(observations.get("state_sequence"))
        if states[-3:] == ["REJECTED", "DISCARDED", "DESTROYED"] and observations.get("owner_decisions_recorded") is True and observations.get("managed_warp_exists_after") is False and observations.get("source_head_before") == observations.get("source_head_after") and observations.get("source_status_after") == []:
            return "WARP_LIFECYCLE_CONTAINED_PROVEN"
    elif scenario_id == "restart_and_state_recovery":
        if observations.get("interruption_observed") is True and observations.get("pending_receipt_present_before_restart") is True and observations.get("recovered_state") == "TASK_REGISTRATION" and observations.get("recovered_state_version") == 2 and observations.get("pending_receipt_present_after_restart") is False and observations.get("transition_log_entries") == 2:
            return "RESTART_STATE_RECOVERY_PROVEN"
    return "NOT_PROVEN"


def validate_receipt(
    receipt: dict[str, Any],
    report_root: Path,
    *,
    task_id: str,
    warp_id: str,
    base_head: str,
    mode: str = "validate",
) -> dict[str, Any]:
    checks, common_failure = _common_integrity(receipt, report_root, task_id=task_id, warp_id=warp_id, base_head=base_head)
    actual = common_failure or derive_actual(str(receipt.get("scenario_id", "")), _dict(receipt.get("observations")))
    expected = receipt.get("expected_verdict")
    declared = receipt.get("actual_verdict")
    comparison_match = actual == expected
    declared_match = declared == actual
    validation_pass = mode == "validate" and all(checks.values()) and actual != "NOT_PROVEN" and comparison_match and declared_match
    result: dict[str, Any] = {
        "schema_version": "imperium.core_reference_corridor.negative_scenario_validation.v1",
        "validator_id": VALIDATOR_ID,
        "validator_version": VALIDATOR_VERSION,
        "validator_path": str(Path(__file__).resolve()),
        "validator_sha256": sha256_file(Path(__file__)),
        "mode": mode,
        "scenario_id": receipt.get("scenario_id"),
        "expected_verdict": expected,
        "declared_actual_verdict": declared,
        "actual_verdict": actual,
        "actual_source": "MEASURED_OBSERVATIONS_ONLY",
        "checks": checks,
        "comparison_match": comparison_match,
        "declared_actual_match": declared_match,
        "failed_checks": [key for key, passed in checks.items() if not passed],
        "validation_verdict": "PASS" if validation_pass else ("DERIVED" if mode == "derive" else "BLOCK"),
    }
    result["receipt_hash"] = canonical_hash(result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--report-root", type=Path, required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--warp-id", required=True)
    parser.add_argument("--base-head", required=True)
    parser.add_argument("--mode", choices=("derive", "validate"), default="validate")
    args = parser.parse_args(argv)
    try:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
        if not isinstance(receipt, dict):
            raise ValueError("receipt must be a JSON object")
        result = validate_receipt(receipt, args.report_root.resolve(), task_id=args.task_id, warp_id=args.warp_id, base_head=args.base_head, mode=args.mode)
    except Exception as exc:
        result = {"schema_version": "imperium.core_reference_corridor.negative_scenario_validation.v1", "validator_id": VALIDATOR_ID, "mode": args.mode, "actual_verdict": "BLOCK_VALIDATOR_INPUT_ERROR", "validation_verdict": "BLOCK", "error": f"{type(exc).__name__}: {exc}"}
        result["receipt_hash"] = canonical_hash(result)
    print(json.dumps(result, sort_keys=True, ensure_ascii=True))
    if args.mode == "derive":
        return 0
    return 0 if result.get("validation_verdict") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
