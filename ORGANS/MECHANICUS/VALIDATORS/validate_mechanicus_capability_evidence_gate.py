#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

TASK_ID = "MECHANICUS-CAPABILITY-EVIDENCE-GATE-0001"
VALIDATOR_ID = "mechanicus_capability_evidence_gate_validator.v0_1"
PASS_VERDICT = "PASS_MECHANICUS_CAPABILITY_EVIDENCE_GATE_READY"

REQUIRED_STATIC = [
    "ORGANS/MECHANICUS/MANIFEST.json",
    "ORGANS/MECHANICUS/FUNCTIONS.md",
    "ORGANS/MECHANICUS/MATRICES/MECHANICUS_FUNCTION_REGISTRY_V0_1.json",
    "ORGANS/MECHANICUS/LAWS/MECHANICUS_CAPABILITY_EVIDENCE_GATE_LAW_V0_1.json",
    "ORGANS/MECHANICUS/MATRICES/MECHANICUS_CAPABILITY_EVIDENCE_GATE_MATRIX_V0_1.json",
    "ORGANS/MECHANICUS/TOOLS/build_mechanicus_capability_evidence_gate.py",
    "ORGANS/CUSTODES/MATRICES/CUSTODES_MECHANICUS_CAPABILITY_EVIDENCE_GATE_PROSECUTOR_MATRIX_V0_1.json",
    "ORGANS/THRONE/MATRICES/THRONE_MECHANICUS_CAPABILITY_EVIDENCE_GATE_CROWN_MATRIX_V0_1.json",
]

GENERATED = [
    "ORGANS/MECHANICUS/RECEIPTS/mechanicus_capability_evidence_gate_receipt.json",
    "ORGANS/MECHANICUS/REPORTS/MECHANICUS_CAPABILITY_EVIDENCE_GATE_SUMMARY_V0_1.json",
    "ORGANS/MECHANICUS/REPORTS/MECHANICUS_CAPABILITY_EVIDENCE_GATE_REPORT_V0_1.json",
    "ORGANS/MECHANICUS/REPORTS/MECHANICUS_CAPABILITY_EVIDENCE_GATE_REPORT_V0_1.md",
]


def has_control_chars(data: str) -> list[dict]:
    hits = []
    for idx, ch in enumerate(data):
        if ord(ch) < 32 and ch not in "\r\n\t":
            hits.append({"offset": idx, "ord": ord(ch)})
            if len(hits) >= 10:
                break
    return hits


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()
    repo_root = Path(args.repo_root).resolve()

    checks = []
    errors = []
    warnings = []

    for rel in REQUIRED_STATIC:
        path = repo_root / rel
        if path.exists():
            checks.append({"name": f"exists::{rel}", "status": "PASS", "details": {"path": rel}})
            text = path.read_text(encoding="utf-8", errors="replace")
            hits = has_control_chars(text)
            checks.append({"name": f"no_control_chars::{rel}", "status": "PASS" if not hits else "FAIL", "details": {"hits": hits}})
            if hits:
                errors.append(f"Control characters found in {rel}: {hits}")
            if rel.endswith(".json"):
                try:
                    load_json(path)
                    checks.append({"name": f"json_parse::{rel}", "status": "PASS", "details": {}})
                except Exception as exc:
                    checks.append({"name": f"json_parse::{rel}", "status": "FAIL", "details": {"error": str(exc)}})
                    errors.append(f"JSON parse failed for {rel}: {exc}")
        else:
            checks.append({"name": f"exists::{rel}", "status": "FAIL", "details": {"path": rel}})
            errors.append(f"Required file missing: {rel}")

    if not errors:
        builder = repo_root / "ORGANS/MECHANICUS/TOOLS/build_mechanicus_capability_evidence_gate.py"
        proc = subprocess.run([sys.executable, str(builder), "--repo-root", str(repo_root)], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0:
            checks.append({"name": "builder_runs", "status": "FAIL", "details": {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}})
            errors.append("Builder failed")
        else:
            try:
                receipt = json.loads(proc.stdout)
            except Exception as exc:
                checks.append({"name": "builder_output_json", "status": "FAIL", "details": {"error": str(exc), "stdout": proc.stdout}})
                errors.append("Builder did not return JSON receipt")
                receipt = None
            if receipt:
                checks.append({"name": "builder_runs", "status": "PASS", "details": receipt})
                if receipt.get("verdict") != PASS_VERDICT:
                    errors.append(f"Unexpected builder verdict: {receipt.get('verdict')}")
                if receipt.get("organ_assembly_claim") is not False:
                    errors.append("organ_assembly_claim must remain false")
                if receipt.get("six_gate_closure_claim") is not False:
                    errors.append("six_gate_closure_claim must remain false")
                if receipt.get("missing_required_evidence_count") != 0:
                    errors.append("Capability evidence gate has missing required evidence")

    for rel in GENERATED:
        path = repo_root / rel
        checks.append({"name": f"generated::{rel}", "status": "PASS" if path.exists() else "FAIL", "details": {"path": rel}})
        if not path.exists():
            errors.append(f"Generated output missing: {rel}")

    if not errors:
        summary = load_json(repo_root / "ORGANS/MECHANICUS/REPORTS/MECHANICUS_CAPABILITY_EVIDENCE_GATE_SUMMARY_V0_1.json")
        report = load_json(repo_root / "ORGANS/MECHANICUS/REPORTS/MECHANICUS_CAPABILITY_EVIDENCE_GATE_REPORT_V0_1.json")
        checks.append({"name": "summary_verdict_pass", "status": "PASS" if summary.get("verdict") == PASS_VERDICT else "FAIL", "details": {"verdict": summary.get("verdict")}})
        checks.append({"name": "g3_status_pass_baseline", "status": "PASS" if summary.get("capability_evidence_gate_status") == "PASS_BASELINE" else "FAIL", "details": {"value": summary.get("capability_evidence_gate_status")}})
        checks.append({"name": "all_current_functions_bound", "status": "PASS" if summary.get("current_function_count") == summary.get("evidence_bound_current_function_count") else "FAIL", "details": {"current": summary.get("current_function_count"), "bound": summary.get("evidence_bound_current_function_count")}})
        checks.append({"name": "local_model_deferred", "status": "PASS" if summary.get("local_model_membrane_status") == "DEFERRED_AFTER_CORE_V1" else "FAIL", "details": {"value": summary.get("local_model_membrane_status")}})
        if summary.get("current_function_count") != summary.get("evidence_bound_current_function_count"):
            errors.append("Not all current functions are evidence-bound")
        if report.get("organ_assembly_claim") is not False or report.get("six_gate_closure_claim") is not False:
            errors.append("Report overclaims organ/six-gate closure")
        warnings.extend(report.get("warnings") or [])

    result = {
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": PASS_VERDICT if not errors else "FAIL_MECHANICUS_CAPABILITY_EVIDENCE_GATE",
        "receipt": "ORGANS/MECHANICUS/RECEIPTS/mechanicus_capability_evidence_gate_receipt.json",
        "summary": "ORGANS/MECHANICUS/REPORTS/MECHANICUS_CAPABILITY_EVIDENCE_GATE_SUMMARY_V0_1.json",
        "report_json": "ORGANS/MECHANICUS/REPORTS/MECHANICUS_CAPABILITY_EVIDENCE_GATE_REPORT_V0_1.json",
        "report_md": "ORGANS/MECHANICUS/REPORTS/MECHANICUS_CAPABILITY_EVIDENCE_GATE_REPORT_V0_1.md",
        "errors": errors,
        "warnings": list(dict.fromkeys(warnings)),
        "checks": checks,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if not errors else 2)


if __name__ == "__main__":
    main()
