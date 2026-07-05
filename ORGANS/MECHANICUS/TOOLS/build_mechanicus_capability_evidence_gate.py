#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

TASK_ID = "MECHANICUS-CAPABILITY-EVIDENCE-GATE-0001"
VALIDATOR_ID = "mechanicus_capability_evidence_gate_validator.v0_1"
PASS_VERDICT = "PASS_MECHANICUS_CAPABILITY_EVIDENCE_GATE_READY"

REGISTRY = "ORGANS/MECHANICUS/MATRICES/MECHANICUS_FUNCTION_REGISTRY_V0_1.json"
MANIFEST = "ORGANS/MECHANICUS/MANIFEST.json"
MATRIX = "ORGANS/MECHANICUS/MATRICES/MECHANICUS_CAPABILITY_EVIDENCE_GATE_MATRIX_V0_1.json"
RECEIPT = "ORGANS/MECHANICUS/RECEIPTS/mechanicus_capability_evidence_gate_receipt.json"
SUMMARY = "ORGANS/MECHANICUS/REPORTS/MECHANICUS_CAPABILITY_EVIDENCE_GATE_SUMMARY_V0_1.json"
REPORT_JSON = "ORGANS/MECHANICUS/REPORTS/MECHANICUS_CAPABILITY_EVIDENCE_GATE_REPORT_V0_1.json"
REPORT_MD = "ORGANS/MECHANICUS/REPORTS/MECHANICUS_CAPABILITY_EVIDENCE_GATE_REPORT_V0_1.md"

CURRENT_STATUSES = {"PROVEN_BASELINE", "MEASURED_PRESENT", "PARTIAL_MEASURED"}
DEFERRED_STATUS = "FUTURE_DEFERRED"
FORBIDDEN_STATUS = "FORBIDDEN"


def read_json(root: Path, rel: str):
    return json.loads((root / rel).read_text(encoding="utf-8"))


def write_json(root: Path, rel: str, data):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def has_control_chars(text: str) -> bool:
    return any((ord(ch) < 32 and ch not in "\r\n\t") for ch in text)


def classify_evidence_path(path: str) -> str:
    lower = path.lower()
    if "/receipts/" in lower or lower.endswith("receipt.json"):
        return "receipt"
    if "/validators/" in lower or "validation" in lower or "validator" in lower:
        return "validator_or_validation"
    if "/reports/" in lower:
        return "report"
    if "/registry/" in lower:
        return "registry"
    if "/matrices/" in lower:
        return "matrix"
    return "other"


def check_json_parse(root: Path, rel: str, errors: list[str]) -> bool:
    if not rel.lower().endswith((".json", ".jsonl")):
        return True
    try:
        if rel.lower().endswith(".jsonl"):
            for i, line in enumerate((root / rel).read_text(encoding="utf-8").splitlines(), start=1):
                if line.strip():
                    json.loads(line)
        else:
            read_json(root, rel)
        return True
    except Exception as exc:
        errors.append(f"JSON parse failed for {rel}: {exc}")
        return False


def build(repo_root: Path):
    errors: list[str] = []
    warnings: list[str] = []
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    registry = read_json(repo_root, REGISTRY)
    manifest = read_json(repo_root, MANIFEST)
    matrix = read_json(repo_root, MATRIX)

    functions = registry.get("functions", [])
    coverage_records = []
    status_counts: dict[str, int] = {}
    evidence_type_counts: dict[str, int] = {}
    missing_required = []
    json_parse_failures = []
    proven_without_receipt_or_validator = []
    overclaim_failures = []
    future_or_forbidden = []

    for fn in functions:
        fid = fn.get("function_id")
        status = fn.get("status")
        status_counts[status] = status_counts.get(status, 0) + 1
        required = list(fn.get("evidence_paths") or [])
        optional = list(fn.get("optional_evidence_paths") or [])
        record = {
            "function_id": fid,
            "title": fn.get("title"),
            "status": status,
            "profile_zone": fn.get("profile_zone"),
            "coverage_status": None,
            "required_evidence_count": len(required),
            "required_evidence_present_count": 0,
            "optional_evidence_count": len(optional),
            "optional_evidence_present_count": 0,
            "evidence_types": {},
            "missing_required_evidence": [],
            "forbidden_overclaim": fn.get("forbidden_overclaim"),
            "deferred_until": fn.get("deferred_until"),
        }

        if has_control_chars(str(fid or "")):
            errors.append(f"Control character in function_id: {fid!r}")

        if status in CURRENT_STATUSES:
            if not required:
                missing_required.append({"function_id": fid, "path": "<missing evidence_paths>"})
                record["missing_required_evidence"].append("<missing evidence_paths>")
            for rel in required:
                if has_control_chars(rel):
                    errors.append(f"Control character in evidence path for {fid}: {rel!r}")
                    record["missing_required_evidence"].append(rel)
                    continue
                p = repo_root / rel
                if not p.exists():
                    missing_required.append({"function_id": fid, "path": rel})
                    record["missing_required_evidence"].append(rel)
                    continue
                record["required_evidence_present_count"] += 1
                et = classify_evidence_path(rel)
                record["evidence_types"][et] = record["evidence_types"].get(et, 0) + 1
                evidence_type_counts[et] = evidence_type_counts.get(et, 0) + 1
                before = len(errors)
                check_json_parse(repo_root, rel, errors)
                if len(errors) > before:
                    json_parse_failures.append({"function_id": fid, "path": rel})
            for rel in optional:
                if (repo_root / rel).exists():
                    record["optional_evidence_present_count"] += 1
                    et = classify_evidence_path(rel)
                    record["evidence_types"][et] = record["evidence_types"].get(et, 0) + 1
                    evidence_type_counts[et] = evidence_type_counts.get(et, 0) + 1
                    check_json_parse(repo_root, rel, errors)
            if status == "PROVEN_BASELINE":
                proof_types = set(record["evidence_types"].keys())
                if not ({"receipt", "validator_or_validation"} & proof_types):
                    proven_without_receipt_or_validator.append(fid)
            if not record["missing_required_evidence"]:
                record["coverage_status"] = "EVIDENCE_BOUND_BASELINE"
            else:
                record["coverage_status"] = "MISSING_REQUIRED_EVIDENCE"
        elif status == DEFERRED_STATUS:
            future_or_forbidden.append(fid)
            if not fn.get("deferred_until"):
                errors.append(f"FUTURE_DEFERRED function lacks deferred_until: {fid}")
            if required:
                warnings.append(f"Deferred function has evidence paths but is not counted as current capability: {fid}")
            record["coverage_status"] = "DEFERRED_NOT_CURRENT_CAPABILITY"
        elif status == FORBIDDEN_STATUS:
            future_or_forbidden.append(fid)
            if required:
                errors.append(f"FORBIDDEN function must not carry capability evidence: {fid}")
            record["coverage_status"] = "FORBIDDEN_CLAIM_ONLY"
        else:
            errors.append(f"Unknown function status for {fid}: {status}")
            record["coverage_status"] = "UNKNOWN_STATUS"

        # Enforce no assembled/six-gate closure overclaim in function text.
        joined = json.dumps(fn, ensure_ascii=False).lower()
        if "mechanicus_assembled" in joined and status != FORBIDDEN_STATUS:
            overclaim_failures.append(fid)
        coverage_records.append(record)

    if proven_without_receipt_or_validator:
        errors.append("PROVEN_BASELINE functions without receipt/validator evidence: " + ", ".join(proven_without_receipt_or_validator))
    if overclaim_failures:
        errors.append("Functions overclaim assembled status: " + ", ".join(overclaim_failures))
    if missing_required:
        errors.append(f"Missing required evidence paths: {len(missing_required)}")

    local_model = manifest.get("local_model_membrane", {})
    if local_model.get("status") != "DEFERRED_AFTER_CORE_V1":
        errors.append("local_model_membrane is not DEFERRED_AFTER_CORE_V1")
    if manifest.get("organ_assembly_claim") is not False:
        errors.append("manifest organ_assembly_claim must remain false")
    if manifest.get("six_gate_closure_claim") is not False:
        errors.append("manifest six_gate_closure_claim must remain false")

    active_functions = [r for r in coverage_records if r["status"] in CURRENT_STATUSES]
    baseline_bound = [r for r in active_functions if r["coverage_status"] == "EVIDENCE_BOUND_BASELINE"]
    capability_evidence_gate_status = "PASS_BASELINE" if not errors and len(baseline_bound) == len(active_functions) else "FAIL"

    six_gate_progress = matrix.get("six_gate_progress_after_pass", [])
    if capability_evidence_gate_status != "PASS_BASELINE":
        for g in six_gate_progress:
            if g.get("gate_id") == "G3_CAPABILITY_EVIDENCE":
                g["state"] = "FAIL"
                g["closure_claim"] = "NOT_CLOSED"

    warnings.extend([
        "This patch closes Capability Evidence baseline only; it does not assemble Mechanicus.",
        "Personal validators, current truth/receipts, residency/trust, Custodes and Throne gates remain future work.",
        "FUTURE_DEFERRED and FORBIDDEN functions are intentionally excluded from current capability evidence closure."
    ])

    report = {
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": PASS_VERDICT if not errors else "FAIL_MECHANICUS_CAPABILITY_EVIDENCE_GATE",
        "generated_at_utc": generated_at,
        "gate_id": "G3_CAPABILITY_EVIDENCE",
        "capability_evidence_gate_status": capability_evidence_gate_status,
        "function_count": len(functions),
        "current_function_count": len(active_functions),
        "evidence_bound_current_function_count": len(baseline_bound),
        "future_deferred_count": status_counts.get(DEFERRED_STATUS, 0),
        "forbidden_count": status_counts.get(FORBIDDEN_STATUS, 0),
        "missing_required_evidence_count": len(missing_required),
        "json_parse_failure_count": len(json_parse_failures),
        "status_counts": status_counts,
        "evidence_type_counts": evidence_type_counts,
        "coverage_records": coverage_records,
        "missing_required_evidence": missing_required,
        "json_parse_failures": json_parse_failures,
        "proven_without_receipt_or_validator": proven_without_receipt_or_validator,
        "local_model_membrane_status": local_model.get("status"),
        "organ_assembly_claim": False,
        "six_gate_closure_claim": False,
        "six_gate_progress": six_gate_progress,
        "deferred_capabilities": [r for r in coverage_records if r["status"] == DEFERRED_STATUS],
        "forbidden_capabilities": [r for r in coverage_records if r["status"] == FORBIDDEN_STATUS],
        "errors": errors,
        "warnings": warnings,
    }

    summary = {
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": report["verdict"],
        "generated_at_utc": generated_at,
        "capability_evidence_gate_status": capability_evidence_gate_status,
        "function_count": len(functions),
        "current_function_count": len(active_functions),
        "evidence_bound_current_function_count": len(baseline_bound),
        "future_deferred_count": status_counts.get(DEFERRED_STATUS, 0),
        "forbidden_count": status_counts.get(FORBIDDEN_STATUS, 0),
        "missing_required_evidence_count": len(missing_required),
        "json_parse_failure_count": len(json_parse_failures),
        "local_model_membrane_status": local_model.get("status"),
        "organ_assembly_claim": False,
        "six_gate_closure_claim": False,
        "next_gate_count": 4,
        "errors_count": len(errors),
        "warnings_count": len(warnings),
    }

    receipt = {
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": report["verdict"],
        "generated_at_utc": generated_at,
        "gate_id": "G3_CAPABILITY_EVIDENCE",
        "capability_evidence_gate_status": capability_evidence_gate_status,
        "function_count": len(functions),
        "current_function_count": len(active_functions),
        "evidence_bound_current_function_count": len(baseline_bound),
        "missing_required_evidence_count": len(missing_required),
        "organ_assembly_claim": False,
        "six_gate_closure_claim": False,
        "receipt": RECEIPT,
        "summary": SUMMARY,
        "report_json": REPORT_JSON,
        "report_md": REPORT_MD,
        "errors": errors,
        "warnings": warnings,
    }

    write_json(repo_root, REPORT_JSON, report)
    write_json(repo_root, SUMMARY, summary)
    write_json(repo_root, RECEIPT, receipt)

    md_lines = [
        "# MECHANICUS Capability Evidence Gate V0.1",
        "",
        f"- task_id: `{TASK_ID}`",
        f"- verdict: `{report['verdict']}`",
        f"- gate: `G3_CAPABILITY_EVIDENCE`",
        f"- capability_evidence_gate_status: `{capability_evidence_gate_status}`",
        f"- current functions bound to evidence: `{len(baseline_bound)}/{len(active_functions)}`",
        f"- missing required evidence: `{len(missing_required)}`",
        f"- local model membrane: `{local_model.get('status')}`",
        "",
        "## Six Gate Progress",
        "",
        "| Gate | State | Closure claim |",
        "|---|---:|---|",
    ]
    for gate in six_gate_progress:
        md_lines.append(f"| {gate.get('gate_id')} | {gate.get('state')} | {gate.get('closure_claim')} |")
    md_lines += ["", "## Function Coverage", "", "| Function | Status | Coverage | Required evidence present |", "|---|---:|---:|---:|"]
    for rec in coverage_records:
        md_lines.append(f"| {rec['function_id']} | {rec['status']} | {rec['coverage_status']} | {rec['required_evidence_present_count']}/{rec['required_evidence_count']} |")
    md_lines += ["", "## Warnings", ""]
    md_lines += [f"- {w}" for w in warnings]
    if errors:
        md_lines += ["", "## Errors", ""] + [f"- {e}" for e in errors]
    (repo_root / REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / REPORT_MD).write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    return receipt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()
    repo_root = Path(args.repo_root).resolve()
    receipt = build(repo_root)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    if receipt["errors"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
