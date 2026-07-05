#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

TASK_ID = "MECHANICUS-MANIFEST-AND-FUNCTIONS-GATE-0001"
VALIDATOR_ID = "mechanicus_manifest_and_functions_gate_validator.v0_1"
MANIFEST = Path("ORGANS/MECHANICUS/MANIFEST.json")
FUNCTIONS_MD = Path("ORGANS/MECHANICUS/FUNCTIONS.md")
FUNCTION_REGISTRY = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_FUNCTION_REGISTRY_V0_1.json")
GATE_MATRIX = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE_MATRIX_V0_1.json")
REPORT_JSON = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE_REPORT_V0_1.json")
REPORT_MD = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE_REPORT_V0_1.md")
SUMMARY_JSON = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE_SUMMARY_V0_1.json")
RECEIPT_JSON = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_manifest_and_functions_gate_receipt.json")

FORBIDDEN_REPORT_CLAIMS = ["MECHANICUS_ASSEMBLED", "SIX_GATES_100_PERCENT_CLOSED", "PASS_MECHANICUS_ASSEMBLED"]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def rel_exists(repo_root: Path, rel: str) -> bool:
    return (repo_root / rel).exists()


def build(repo_root: Path, write_outputs: bool = True) -> dict:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[dict] = []

    def check(name: str, status: bool, details: dict | None = None, error: str | None = None):
        checks.append({"name": name, "status": "PASS" if status else "FAIL", "details": details or {}})
        if not status and error:
            errors.append(error)

    static_paths = [MANIFEST, FUNCTIONS_MD, FUNCTION_REGISTRY, GATE_MATRIX]
    for p in static_paths:
        check(f"exists::{p.as_posix()}", (repo_root / p).exists(), {"path": p.as_posix()}, f"missing required file: {p.as_posix()}")

    manifest = {}
    registry = {}
    matrix = {}
    if not errors:
        try:
            manifest = load_json(repo_root / MANIFEST)
            check("json_parse::MANIFEST", True)
        except Exception as exc:
            check("json_parse::MANIFEST", False, {"error": str(exc)}, f"MANIFEST JSON parse failed: {exc}")
        try:
            registry = load_json(repo_root / FUNCTION_REGISTRY)
            check("json_parse::FUNCTION_REGISTRY", True)
        except Exception as exc:
            check("json_parse::FUNCTION_REGISTRY", False, {"error": str(exc)}, f"function registry JSON parse failed: {exc}")
        try:
            matrix = load_json(repo_root / GATE_MATRIX)
            check("json_parse::GATE_MATRIX", True)
        except Exception as exc:
            check("json_parse::GATE_MATRIX", False, {"error": str(exc)}, f"gate matrix JSON parse failed: {exc}")

    if not errors:
        required_manifest_fields = matrix.get("required_manifest_fields", [])
        missing_manifest = [field for field in required_manifest_fields if field not in manifest]
        check("manifest_has_required_fields", not missing_manifest, {"missing": missing_manifest}, f"manifest missing fields: {missing_manifest}")
        check("manifest_organ_id_mechanicus", manifest.get("organ_id") == "MECHANICUS", {"organ_id": manifest.get("organ_id")}, "manifest organ_id is not MECHANICUS")
        check("manifest_no_full_implementation_claim", manifest.get("full_implementation_claim") is False, {"value": manifest.get("full_implementation_claim")}, "manifest full_implementation_claim must be false")
        check("manifest_no_organ_assembly_claim", manifest.get("organ_assembly_claim") is False, {"value": manifest.get("organ_assembly_claim")}, "manifest organ_assembly_claim must be false")
        check("manifest_no_six_gate_closure_claim", manifest.get("six_gate_closure_claim") is False, {"value": manifest.get("six_gate_closure_claim")}, "manifest six_gate_closure_claim must be false")
        six_gates = manifest.get("six_gates", [])
        check("manifest_has_exactly_six_gates", isinstance(six_gates, list) and len(six_gates) == 6, {"count": len(six_gates) if isinstance(six_gates, list) else None}, "manifest must contain exactly six gates")
        local_model = manifest.get("local_model_membrane", {})
        check("local_model_membrane_deferred", local_model.get("status") == "DEFERRED_AFTER_CORE_V1", {"status": local_model.get("status")}, "local model membrane must remain DEFERRED_AFTER_CORE_V1")

        for rel in manifest.get("required_current_evidence", []):
            check(f"evidence_exists::{rel}", rel_exists(repo_root, rel), {"path": rel}, f"required current evidence missing: {rel}")

        functions_text = (repo_root / FUNCTIONS_MD).read_text(encoding="utf-8")
        required_markers = ["MECHANICUS_ASSEMBLED", "SIX_GATES_100_PERCENT_CLOSED", "DEFERRED_AFTER_CORE_V1", "FUNCTION_REGISTRY"]
        # FUNCTIONS.md names the registry path, not necessarily exact label FUNCTION_REGISTRY; accept path marker too.
        marker_status = {
            "MECHANICUS_ASSEMBLED": "MECHANICUS_ASSEMBLED" in functions_text,
            "SIX_GATES_100_PERCENT_CLOSED": "SIX_GATES_100_PERCENT_CLOSED" in functions_text,
            "DEFERRED_AFTER_CORE_V1": "DEFERRED_AFTER_CORE_V1" in functions_text,
            "registry_path": "MECHANICUS_FUNCTION_REGISTRY_V0_1.json" in functions_text,
        }
        check("functions_md_has_required_markers", all(marker_status.values()), marker_status, f"FUNCTIONS.md missing required markers: {[k for k, v in marker_status.items() if not v]}")

        functions = registry.get("functions", [])
        allowed_statuses = set(matrix.get("allowed_function_statuses", []))
        required_function_fields = matrix.get("required_function_fields", [])
        check("function_registry_has_functions", isinstance(functions, list) and len(functions) >= 8, {"count": len(functions) if isinstance(functions, list) else None}, "function registry must contain at least 8 functions")
        status_counts = Counter()
        missing_function_fields = []
        missing_evidence = []
        for fn in functions if isinstance(functions, list) else []:
            fid = fn.get("function_id", "<missing>")
            missing = [field for field in required_function_fields if field not in fn]
            if missing:
                missing_function_fields.append({"function_id": fid, "missing": missing})
            status = fn.get("status")
            status_counts[status] += 1
            if status not in allowed_statuses:
                errors.append(f"function {fid} has invalid status {status}")
            if status in {"PROVEN_BASELINE", "MEASURED_PRESENT", "PARTIAL_MEASURED"}:
                for rel in fn.get("evidence_paths", []):
                    if not rel_exists(repo_root, rel):
                        optional = rel in fn.get("optional_evidence_paths", [])
                        if optional:
                            warnings.append(f"optional evidence missing for {fid}: {rel}")
                        else:
                            missing_evidence.append({"function_id": fid, "path": rel})
            if status == "FORBIDDEN" and fn.get("evidence_paths"):
                errors.append(f"forbidden function {fid} must not have evidence paths")
        check("function_records_have_required_fields", not missing_function_fields, {"missing": missing_function_fields}, f"function records missing required fields: {missing_function_fields}")
        check("function_evidence_paths_exist", not missing_evidence, {"missing": missing_evidence}, f"required function evidence missing: {missing_evidence}")
        check("function_registry_has_proven_baseline", status_counts.get("PROVEN_BASELINE", 0) >= 1, {"count": status_counts.get("PROVEN_BASELINE", 0)}, "function registry must contain at least one PROVEN_BASELINE function")
        check("function_registry_has_future_deferred", status_counts.get("FUTURE_DEFERRED", 0) >= 1, {"count": status_counts.get("FUTURE_DEFERRED", 0)}, "function registry must contain at least one FUTURE_DEFERRED function")
        check("function_registry_has_forbidden", status_counts.get("FORBIDDEN", 0) >= 1, {"count": status_counts.get("FORBIDDEN", 0)}, "function registry must contain at least one FORBIDDEN function")

        # Ensure generated report text will not claim forbidden closure.
        forbidden_claims_in_manifest_status = [claim for claim in FORBIDDEN_REPORT_CLAIMS if claim in str(manifest.get("status", ""))]
        check("manifest_status_has_no_forbidden_closure_claim", not forbidden_claims_in_manifest_status, {"forbidden": forbidden_claims_in_manifest_status}, f"manifest status contains forbidden closure claim: {forbidden_claims_in_manifest_status}")
    else:
        functions = []
        status_counts = Counter()
        six_gates = []

    verdict = "PASS_MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE_READY" if not errors else "FAIL_MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE"
    gate_statuses = []
    if not errors and isinstance(manifest.get("six_gates"), list):
        gate_statuses = [
            {
                "gate_id": gate.get("gate_id"),
                "current_state_after_this_patch": gate.get("current_state_after_this_patch"),
                "closure_claim": gate.get("closure_claim"),
            }
            for gate in manifest.get("six_gates", [])
        ]
    warnings.extend([
        "This patch closes identity/functions baseline only; it does not assemble Mechanicus.",
        "Personal validators, evidence coverage, residency/trust, Custodes and Throne gates remain future work."
    ])

    report = {
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": now,
        "manifest_path": MANIFEST.as_posix(),
        "functions_md_path": FUNCTIONS_MD.as_posix(),
        "function_registry_path": FUNCTION_REGISTRY.as_posix(),
        "gate_matrix_path": GATE_MATRIX.as_posix(),
        "organ_assembly_claim": False,
        "six_gate_closure_claim": False,
        "identity_gate_status": "PASS_BASELINE" if not errors else "FAIL",
        "functions_gate_status": "PASS_BASELINE" if not errors else "FAIL",
        "six_gate_progress": gate_statuses,
        "function_status_counts": dict(status_counts),
        "function_count": len(functions) if isinstance(functions, list) else 0,
        "local_model_membrane_status": (manifest.get("local_model_membrane") or {}).get("status") if isinstance(manifest, dict) else None,
        "next_gate_work": manifest.get("next_gate_work", []) if isinstance(manifest, dict) else [],
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
    }
    summary = {
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": now,
        "identity_gate_status": report["identity_gate_status"],
        "functions_gate_status": report["functions_gate_status"],
        "organ_assembly_claim": False,
        "six_gate_closure_claim": False,
        "function_count": report["function_count"],
        "function_status_counts": report["function_status_counts"],
        "local_model_membrane_status": report["local_model_membrane_status"],
        "next_gate_count": len(report["next_gate_work"]),
        "errors": errors,
        "warnings": warnings,
    }
    receipt = {
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": now,
        "manifest": MANIFEST.as_posix(),
        "functions_md": FUNCTIONS_MD.as_posix(),
        "summary": SUMMARY_JSON.as_posix(),
        "report_json": REPORT_JSON.as_posix(),
        "report_md": REPORT_MD.as_posix(),
        "identity_gate_status": report["identity_gate_status"],
        "functions_gate_status": report["functions_gate_status"],
        "organ_assembly_claim": False,
        "six_gate_closure_claim": False,
        "errors": errors,
        "warnings": warnings,
    }

    if write_outputs:
        for out_path, payload in [(REPORT_JSON, report), (SUMMARY_JSON, summary), (RECEIPT_JSON, receipt)]:
            p = repo_root / out_path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        md_lines = [
            "# MECHANICUS MANIFEST AND FUNCTIONS GATE REPORT V0.1",
            "",
            f"- task_id: `{TASK_ID}`",
            f"- verdict: `{verdict}`",
            f"- generated_at_utc: `{now}`",
            f"- identity_gate_status: `{report['identity_gate_status']}`",
            f"- functions_gate_status: `{report['functions_gate_status']}`",
            "- organ_assembly_claim: `false`",
            "- six_gate_closure_claim: `false`",
            f"- function_count: `{report['function_count']}`",
            f"- local_model_membrane_status: `{report['local_model_membrane_status']}`",
            "",
            "## Function status counts",
        ]
        for name, value in sorted(report["function_status_counts"].items()):
            md_lines.append(f"- `{name}`: `{value}`")
        md_lines.extend(["", "## Six-gate progress"])
        for gate in gate_statuses:
            md_lines.append(f"- `{gate.get('gate_id')}`: `{gate.get('current_state_after_this_patch')}` / `{gate.get('closure_claim')}`")
        md_lines.extend(["", "## Warnings"])
        for warning in warnings:
            md_lines.append(f"- {warning}")
        md_lines.extend(["", "## Errors"])
        if errors:
            for error in errors:
                md_lines.append(f"- {error}")
        else:
            md_lines.append("- none")
        (repo_root / REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
        (repo_root / REPORT_MD).write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    return {"receipt": receipt, "summary": summary, "report": report}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    repo_root = Path(args.repo_root).resolve()
    result = build(repo_root, write_outputs=not args.no_write)
    print(json.dumps(result["receipt"], ensure_ascii=False, indent=2))
    if result["receipt"]["errors"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
