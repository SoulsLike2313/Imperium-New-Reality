#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

TASK_ID = "MECHANICUS-TOOL-ADMISSION-V2-0001"
VALIDATOR_ID = "mechanicus_tool_admission_v2_validator.v0_1"
INVENTORY = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_INVENTORY_V0_1.json")
COMMAND_POLICY = Path("ORGANS/MECHANICUS/REGISTRY/command_policy.json")
REPORT_JSON = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_ADMISSION_V2_REPORT_V0_1.json")
REPORT_MD = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_ADMISSION_V2_REPORT_V0_1.md")
SUMMARY_JSON = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_ADMISSION_V2_SUMMARY_V0_1.json")
RECEIPT_JSON = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_tool_admission_v2_receipt.json")

READONLY_KIND_MARKERS = (
    "validator", "scanner", "scan", "census", "report", "inventory", "proof", "matrix", "schema", "receipt", "doctor"
)
RUNNER_MARKERS = ("runner", "run_", "ps1", "patch_runner")
DANGEROUS_RISK_MARKERS = (
    "unsafe_mutation", "delete_files", "mass_move", "arbitrary_shell", "secret", "stage_local_config"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def text_contains_any(text: str, needles) -> bool:
    t = (text or "").lower()
    return any(n.lower() in t for n in needles)


def source_value(record: dict, *names: str, default=""):
    for name in names:
        value = record.get(name)
        if value is not None and value != "":
            return value
    return default


def normalize_risks(risks) -> list[str]:
    if risks is None:
        return []
    if isinstance(risks, list):
        return [str(x) for x in risks]
    return [str(risks)]


def classify_tool(record: dict, allowlisted: set[str]) -> dict:
    tool_id = str(source_value(record, "tool_id", "id", default="UNKNOWN_TOOL"))
    tool_class = str(source_value(record, "tool_class", default="unknown_tool_class"))
    kind = str(source_value(record, "kind", default="unknown_kind"))
    path_or_command = str(source_value(record, "path_or_command", "path", "command", default=""))
    purpose = str(source_value(record, "purpose", default=""))
    provenance = str(source_value(record, "provenance", default="unknown"))
    owner_scope = str(source_value(record, "owner_scope", "owner", default="unknown"))
    language_lane = str(source_value(record, "language_lane", "lane", default="unknown"))
    source_admission_state = str(source_value(record, "admission_state", "status", default="DISCOVERED"))
    source_risks = normalize_risks(record.get("risks"))
    validation_evidence = record.get("validation_evidence", {}) if isinstance(record.get("validation_evidence"), dict) else {}

    text_blob = " ".join([tool_id, tool_class, kind, path_or_command, purpose, provenance, owner_scope, language_lane, " ".join(source_risks)])
    promotion_blockers: list[str] = []

    if tool_id in ("", "UNKNOWN_TOOL"):
        promotion_blockers.append("missing_tool_id")
    if not purpose:
        promotion_blockers.append("missing_purpose")
    if not path_or_command:
        promotion_blockers.append("missing_path_or_command")
    if provenance in ("", "unknown"):
        promotion_blockers.append("unknown_provenance")
    if language_lane in ("", "unknown", "none", "null"):
        promotion_blockers.append("missing_or_unknown_language_lane")

    if source_admission_state in {"REJECTED_REWORK_REQUIRED", "QUARANTINED"}:
        promotion_blockers.append("source_inventory_not_admitted")
    if any(text_contains_any(r, DANGEROUS_RISK_MARKERS) for r in source_risks):
        promotion_blockers.append("dangerous_risk_marker_present")

    allowed_actions: list[str] = []
    forbidden_actions = [
        "arbitrary_shell",
        "real_execution_without_owner_approval",
        "direct_master_mutation",
        "secret_or_local_config_staging",
        "self_promotion_without_receipt"
    ]

    input_contract_status = "MISSING"
    output_contract_status = "MISSING"
    receipt_contract_status = "MISSING"
    validator_coverage = "INVENTORY_ONLY"
    custodes_audit_status = "NOT_AUDITED_V2_PROSECUTOR_MATRIX_ONLY"
    throne_relevance = "TOOL_ADMISSION_FOUNDATION_INPUT_NOT_CROWNED"

    if tool_class == "external_tool":
        risk_class = "HOST_BOUND_CAPABILITY"
        execution_mode = "HOST_BOUND_PROBE_ONLY"
        v2_status = "ADMITTED_HOST_BOUND_CAPABILITY" if source_admission_state.startswith("ADMITTED") and not promotion_blockers else "CANDIDATE_REQUIRES_REVIEW"
        allowed_actions = ["presence_or_version_probe", "host_bound_capability_report"]
        input_contract_status = "SOURCE_REPORT_BOUND"
        output_contract_status = "SOURCE_REPORT_BOUND"
        receipt_contract_status = "SOURCE_REPORT_BOUND" if validation_evidence else "MISSING"
        validator_coverage = "HOST_TOOLCHAIN_PROBE_BOUND" if validation_evidence else "INVENTORY_ONLY"
    elif tool_id in allowlisted:
        risk_class = "LOW_DRY_RUN"
        execution_mode = "DRY_RUN_ALLOWLISTED"
        v2_status = "ADMITTED_DRY_RUN" if not [b for b in promotion_blockers if b not in {"missing_or_unknown_language_lane"}] else "CANDIDATE_REQUIRES_REVIEW"
        allowed_actions = ["dry_run_only", "emit_receipt", "read_registered_inputs"]
        input_contract_status = "DECLARED"
        output_contract_status = "DECLARED"
        receipt_contract_status = "DECLARED"
        validator_coverage = "COMMAND_POLICY_ALLOWLIST_BOUND"
    elif text_contains_any(text_blob, RUNNER_MARKERS):
        risk_class = "PATCH_RUNNER_SCOPE"
        execution_mode = "PATCH_RUNNER_NOT_PROMOTED"
        v2_status = "CANDIDATE_REQUIRES_REVIEW" if source_admission_state.startswith("ADMITTED") else "REJECTED_REWORK_REQUIRED"
        allowed_actions = ["patch_scope_execution_only_when_owner_runs_warp_runner"]
        input_contract_status = "IMPLIED_BY_TOOL_CLASS"
        output_contract_status = "IMPLIED_BY_TOOL_CLASS"
        receipt_contract_status = "MISSING" if not validation_evidence else "SOURCE_REPORT_BOUND"
        promotion_blockers.append("runner_not_promoted_to_general_tool_execution")
    elif source_admission_state in {"REJECTED_REWORK_REQUIRED", "QUARANTINED"}:
        risk_class = "QUARANTINE_OR_REWORK"
        execution_mode = "EXECUTION_BLOCKED"
        v2_status = "REJECTED_REWORK_REQUIRED" if source_admission_state == "REJECTED_REWORK_REQUIRED" else "QUARANTINED"
        allowed_actions = ["inspect_as_debt", "repair_in_future_patch"]
    elif text_contains_any(text_blob, READONLY_KIND_MARKERS):
        risk_class = "LOW_READ_ONLY"
        execution_mode = "LOCAL_READ_ONLY_BY_CONTRACT"
        v2_status = "ADMITTED_READ_ONLY" if not [b for b in promotion_blockers if b not in {"missing_or_unknown_language_lane"}] else "CANDIDATE_REQUIRES_REVIEW"
        allowed_actions = ["read_repo", "parse_files", "write_report_when_runner_applies_patch"]
        input_contract_status = "IMPLIED_BY_TOOL_CLASS"
        output_contract_status = "IMPLIED_BY_TOOL_CLASS"
        receipt_contract_status = "SOURCE_REPORT_BOUND" if validation_evidence else "MISSING"
        validator_coverage = "READ_ONLY_CLASS_INFERRED_FROM_INVENTORY"
    else:
        risk_class = "MEDIUM_REVIEW_REQUIRED"
        execution_mode = "EXECUTION_BLOCKED"
        v2_status = "CANDIDATE_REQUIRES_REVIEW" if source_admission_state.startswith("ADMITTED") else "REJECTED_REWORK_REQUIRED"
        allowed_actions = ["inspect", "classify_in_future_patch"]

    if source_admission_state == "DEPRECATED":
        v2_status = "DEPRECATED"
        risk_class = "QUARANTINE_OR_REWORK"
        execution_mode = "EXECUTION_BLOCKED"
    if any(b in promotion_blockers for b in ("dangerous_risk_marker_present",)):
        v2_status = "QUARANTINED"
        risk_class = "QUARANTINE_OR_REWORK"
        execution_mode = "EXECUTION_BLOCKED"

    # No real execution authority can be granted by this foundation patch.
    if v2_status == "ADMITTED_OWNER_APPROVED_EXECUTION":
        promotion_blockers.append("owner_approved_real_execution_forbidden_in_v2_foundation")
        v2_status = "CANDIDATE_REQUIRES_REVIEW"
        execution_mode = "OWNER_APPROVED_REAL_EXECUTION_NOT_GRANTED"

    return {
        "tool_id": tool_id,
        "source_admission_state": source_admission_state,
        "tool_class": tool_class,
        "kind": kind,
        "owner_scope": owner_scope,
        "path_or_command": path_or_command,
        "purpose": purpose,
        "provenance": provenance,
        "language_lane": language_lane,
        "risk_class": risk_class,
        "execution_mode": execution_mode,
        "allowed_actions": allowed_actions,
        "forbidden_actions": forbidden_actions,
        "input_contract_status": input_contract_status,
        "output_contract_status": output_contract_status,
        "receipt_contract_status": receipt_contract_status,
        "validator_coverage": validator_coverage,
        "custodes_audit_status": custodes_audit_status,
        "throne_relevance": throne_relevance,
        "v2_admission_status": v2_status,
        "promotion_blockers": sorted(set(promotion_blockers)),
        "source_risks": source_risks,
        "source_validation_evidence_present": bool(validation_evidence)
    }


def build(repo_root: Path, apply: bool) -> dict:
    inventory_path = repo_root / INVENTORY
    policy_path = repo_root / COMMAND_POLICY
    errors: list[str] = []
    warnings: list[str] = []

    if not inventory_path.exists():
        errors.append(f"missing source inventory: {INVENTORY.as_posix()}")
        tools = []
        inventory = {}
    else:
        inventory = load_json(inventory_path)
        tools = inventory.get("tools")
        if tools is None:
            tools = inventory.get("records")
        if tools is None:
            tools = []
        if not isinstance(tools, list):
            errors.append("source inventory tools/records is not a list")
            tools = []

    if not policy_path.exists():
        errors.append(f"missing command policy: {COMMAND_POLICY.as_posix()}")
        policy = {}
    else:
        policy = load_json(policy_path)
        if policy.get("arbitrary_shell_execution_allowed") is not False:
            errors.append("command policy does not explicitly forbid arbitrary shell execution")

    allowlisted = set(policy.get("allowlisted_tool_ids_for_dry_run") or [])
    records = [classify_tool(t, allowlisted) for t in tools]
    status_counts = Counter(r["v2_admission_status"] for r in records)
    execution_counts = Counter(r["execution_mode"] for r in records)
    risk_counts = Counter(r["risk_class"] for r in records)
    source_state_counts = Counter(r["source_admission_state"] for r in records)

    real_execution_enabled_count = status_counts.get("ADMITTED_OWNER_APPROVED_EXECUTION", 0)
    if real_execution_enabled_count:
        errors.append("V2 foundation granted real execution authority; forbidden")
    if not tools:
        errors.append("source inventory contains no tools")
    if status_counts.get("REJECTED_REWORK_REQUIRED", 0) or status_counts.get("CANDIDATE_REQUIRES_REVIEW", 0):
        warnings.append("Tool admission V2 exposes non-admitted tools; this is expected debt visibility, not failure.")
    if risk_counts.get("HOST_BOUND_CAPABILITY", 0):
        warnings.append("Host-bound capabilities remain host-bound until reproducibility/bootstrap proof exists.")

    deferred_capabilities = [
        {
            "capability_id": "LOCAL_MODEL_MEMBRANE",
            "status": "DEFERRED_AFTER_CORE_V1",
            "core_v1_dependency": False,
            "admission_authority": False,
            "execution_authority": False,
            "allowed_future_role": "translate Owner intent into machine-readable intent envelopes and explain routing/cost after script-first gates exist"
        },
        {
            "capability_id": "SAFE_REAL_EXECUTION_GATEWAY",
            "status": "FUTURE_PATCH_REQUIRED",
            "core_v1_dependency": True,
            "admission_authority": False,
            "execution_authority": "not granted by V2 foundation"
        }
    ]

    report = {
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": "PASS_MECHANICUS_TOOL_ADMISSION_V2_READY" if not errors else "FAIL_MECHANICUS_TOOL_ADMISSION_V2",
        "generated_at_utc": utc_now(),
        "repo_root": str(repo_root),
        "source_inventory_path": INVENTORY.as_posix(),
        "source_command_policy_path": COMMAND_POLICY.as_posix(),
        "source_tool_count": len(tools),
        "source_counts_by_state": dict(sorted(source_state_counts.items())),
        "admission_counts_by_v2_status": dict(sorted(status_counts.items())),
        "execution_mode_counts": dict(sorted(execution_counts.items())),
        "risk_class_counts": dict(sorted(risk_counts.items())),
        "real_execution_enabled_count": real_execution_enabled_count,
        "dry_run_allowlist_count": len(allowlisted),
        "script_first_posture": {
            "core_v1_requires_internal_llm_magic": False,
            "local_model_membrane": "DEFERRED_AFTER_CORE_V1_NOT_A_DEPENDENCY",
            "tool_admission_is_script_first": True
        },
        "deferred_capabilities": deferred_capabilities,
        "admission_records": records,
        "errors": errors,
        "warnings": warnings,
    }

    summary = {
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": report["verdict"],
        "generated_at_utc": report["generated_at_utc"],
        "source_tool_count": report["source_tool_count"],
        "v2_admitted_read_only_count": status_counts.get("ADMITTED_READ_ONLY", 0),
        "v2_admitted_dry_run_count": status_counts.get("ADMITTED_DRY_RUN", 0),
        "v2_host_bound_count": status_counts.get("ADMITTED_HOST_BOUND_CAPABILITY", 0),
        "candidate_requires_review_count": status_counts.get("CANDIDATE_REQUIRES_REVIEW", 0),
        "blocked_or_rejected_count": status_counts.get("REJECTED_REWORK_REQUIRED", 0) + status_counts.get("QUARANTINED", 0),
        "real_execution_enabled_count": real_execution_enabled_count,
        "warnings_count": len(warnings),
        "errors_count": len(errors),
        "local_model_membrane_status": "DEFERRED_AFTER_CORE_V1",
        "safe_real_execution_gateway_status": "FUTURE_PATCH_REQUIRED"
    }

    receipt = {
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": report["verdict"],
        "generated_at_utc": report["generated_at_utc"],
        "report": REPORT_JSON.as_posix(),
        "summary": SUMMARY_JSON.as_posix(),
        "source_inventory": INVENTORY.as_posix(),
        "source_tool_count": len(tools),
        "real_execution_enabled_count": real_execution_enabled_count,
        "errors": errors,
        "warnings": warnings
    }

    if apply:
        write_json(repo_root / REPORT_JSON, report)
        write_json(repo_root / SUMMARY_JSON, summary)
        write_json(repo_root / RECEIPT_JSON, receipt)
        md = [
            "# MECHANICUS TOOL ADMISSION V2 REPORT V0.1",
            "",
            f"Task: `{TASK_ID}`",
            f"Verdict: `{report['verdict']}`",
            f"Generated: `{report['generated_at_utc']}`",
            "",
            "## Counts",
            "",
            f"- Source tools: {len(tools)}",
            f"- Admitted read-only: {summary['v2_admitted_read_only_count']}",
            f"- Admitted dry-run: {summary['v2_admitted_dry_run_count']}",
            f"- Host-bound capabilities: {summary['v2_host_bound_count']}",
            f"- Candidate/review: {summary['candidate_requires_review_count']}",
            f"- Blocked/rejected/quarantined: {summary['blocked_or_rejected_count']}",
            f"- Real execution enabled: {real_execution_enabled_count}",
            "",
            "## Boundary",
            "",
            "Tool inventory is not tool admission. Read-only/dry-run admission is not real execution authority. Local model membrane remains deferred after Core v1 and cannot admit or execute tools.",
            "",
            "## Warnings",
            "",
        ]
        if warnings:
            md.extend([f"- {w}" for w in warnings])
        else:
            md.append("- None")
        md.extend(["", "## Errors", ""])
        if errors:
            md.extend([f"- {e}" for e in errors])
        else:
            md.append("- None")
        (repo_root / REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
        (repo_root / REPORT_MD).write_text("\n".join(md) + "\n", encoding="utf-8")

    return {
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": report["verdict"],
        "receipt": RECEIPT_JSON.as_posix(),
        "summary": SUMMARY_JSON.as_posix(),
        "report_json": REPORT_JSON.as_posix(),
        "report_md": REPORT_MD.as_posix(),
        "source_tool_count": len(tools),
        "real_execution_enabled_count": real_execution_enabled_count,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    result = build(Path(args.repo_root).resolve(), args.apply)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not result["errors"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
