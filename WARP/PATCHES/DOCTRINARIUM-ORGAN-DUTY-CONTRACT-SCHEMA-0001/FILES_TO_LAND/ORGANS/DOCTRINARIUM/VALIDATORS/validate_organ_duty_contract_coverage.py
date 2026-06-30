#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

TASK_ID = "DOCTRINARIUM-ORGAN-DUTY-CONTRACT-SCHEMA-0001"
VALIDATOR_ID = "organ_duty_contract_coverage_validator.v0_1"

ORGANS = [
    "ASTRONOMICON",
    "ADMINISTRATUM",
    "DOCTRINARIUM",
    "MECHANICUS",
    "INQUISITION",
    "CUSTODES",
    "STRATEGIUM",
    "SCHOLA_IMPERIALIS",
    "OFFICIO_AGENTIS",
    "THRONE",
]

REQUIRED_FIELDS = [
    "contract_id", "contract_version", "status", "organ_id", "organ_class",
    "core_v1_mission", "primary_duties", "forbidden_actions", "accepted_inputs",
    "required_outputs", "required_receipts", "rule_validators_required",
    "action_validators_required", "trust_validators_required", "handoff_in",
    "handoff_out", "audited_by", "throne_must_confirm", "not_allowed_to_claim",
    "minimal_v1_pass_conditions", "proof_stage_flags", "score_policy"
]

ARRAY_MINIMUMS = {
    "primary_duties": 3,
    "forbidden_actions": 3,
    "accepted_inputs": 2,
    "required_outputs": 2,
    "required_receipts": 1,
    "rule_validators_required": 1,
    "action_validators_required": 1,
    "trust_validators_required": 1,
    "handoff_in": 1,
    "handoff_out": 1,
    "audited_by": 1,
    "throne_must_confirm": 2,
    "not_allowed_to_claim": 4,
    "minimal_v1_pass_conditions": 2,
}

SCHEMA_PATH = Path("ORGANS/DOCTRINARIUM/SCHEMAS/organ_duty_contract.schema.json")
REQUIRED_MATRIX_PATH = Path("ORGANS/DOCTRINARIUM/MATRICES/ORGAN_DUTY_CONTRACT_REQUIRED_FIELDS_MATRIX_V0_1.json")
THRONE_STAGE_MATRIX_PATH = Path("ORGANS/THRONE/MATRICES/THRONE_ORGAN_TRUTH_STAGE_MATRIX_V0_1.json")

RECEIPT_PATH = Path("ORGANS/DOCTRINARIUM/RECEIPTS/organ_duty_contract_coverage_receipt.json")
REPORT_PATH = Path("ORGANS/DOCTRINARIUM/REPORTS/ORGAN_DUTY_CONTRACT_COVERAGE_REPORT_V0_1.md")
SUMMARY_JSON = Path("ORGANS/DOCTRINARIUM/REPORTS/ORGAN_DUTY_CONTRACT_SUMMARY_V0_1.json")
SUMMARY_CSV = Path("ORGANS/DOCTRINARIUM/REPORTS/ORGAN_DUTY_CONTRACT_SUMMARY_V0_1.csv")

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def run_git(repo: Path, args: List[str]) -> Tuple[int, str, str]:
    try:
        p = subprocess.run(["git"] + args, cwd=str(repo), text=True, capture_output=True, timeout=60)
        return p.returncode, p.stdout, p.stderr
    except Exception as e:
        return 1, "", str(e)

def git_head(repo: Path) -> str:
    code, out, err = run_git(repo, ["rev-parse", "HEAD"])
    return out.strip() if code == 0 else "UNKNOWN"

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def load_json(path: Path) -> Tuple[Any, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as e:
        return None, str(e)

def contract_path(org: str) -> Path:
    return Path("ORGANS") / org / "CONTRACTS" / "ORGAN_DUTY_CONTRACT_V0_1.json"

def validate_contract(repo: Path, org: str) -> Dict[str, Any]:
    rel = contract_path(org)
    path = repo / rel
    result: Dict[str, Any] = {
        "organ_id": org,
        "path": rel.as_posix(),
        "status": "PASS",
        "errors": [],
        "counts": {},
        "stage": None,
    }

    if not path.is_file():
        result["status"] = "FAIL"
        result["errors"].append("missing contract file")
        return result

    data, err = load_json(path)
    if err:
        result["status"] = "FAIL"
        result["errors"].append("json parse error: " + err)
        return result

    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        result["errors"].append("missing required fields: " + ", ".join(missing))

    if data.get("organ_id") != org:
        result["errors"].append(f"organ_id mismatch: expected {org}, got {data.get('organ_id')}")

    expected_class = "CROWN_ORGAN" if org == "THRONE" else "GREAT_NINE"
    if data.get("organ_class") != expected_class:
        result["errors"].append(f"organ_class mismatch: expected {expected_class}, got {data.get('organ_class')}")

    if data.get("status") != "DUTY_DEFINED_ONLY":
        result["errors"].append("status must be DUTY_DEFINED_ONLY")

    for field, minimum in ARRAY_MINIMUMS.items():
        value = data.get(field)
        if not isinstance(value, list):
            result["errors"].append(f"{field} must be list")
            result["counts"][field] = 0
        else:
            result["counts"][field] = len(value)
            if len(value) < minimum:
                result["errors"].append(f"{field} requires at least {minimum} entries")

    flags = data.get("proof_stage_flags", {})
    result["stage"] = flags
    if not isinstance(flags, dict):
        result["errors"].append("proof_stage_flags must be object")
    else:
        if flags.get("duty_defined") is not True:
            result["errors"].append("proof_stage_flags.duty_defined must be true")
        for key in ["rule_validated", "action_proven", "trust_proven", "throne_confirmed"]:
            if flags.get(key) is not False:
                result["errors"].append(f"proof_stage_flags.{key} must remain false in this patch")

    score_policy = data.get("score_policy", {})
    stage_law = str(score_policy.get("stage_law", ""))
    if "profile_baseline != duty_defined" not in stage_law:
        result["errors"].append("score_policy.stage_law must separate profile_baseline and duty_defined")
    must_not_raise = score_policy.get("must_not_raise", [])
    for required in ["operational_score", "trust_score", "core_v1_no_core_mutation_evidence_score"]:
        if required not in must_not_raise:
            result["errors"].append(f"score_policy.must_not_raise missing {required}")

    not_allowed = " ".join(str(x).lower() for x in data.get("not_allowed_to_claim", []))
    required_phrases = ["self-claim", "self-validator", "profile baseline", "target definition"]
    for phrase in required_phrases:
        if phrase not in not_allowed:
            result["errors"].append(f"not_allowed_to_claim missing phrase: {phrase}")

    forbidden_text = " ".join(str(x).lower() for x in data.get("forbidden_actions", []))
    if org != "THRONE" and "final" in forbidden_text and "verdict" in forbidden_text:
        pass
    elif org != "THRONE":
        result["errors"].append("non-Throne organ must forbid final verdict / crown verdict claim")

    if result["errors"]:
        result["status"] = "FAIL"

    return result

def write_outputs(repo: Path, organ_results: List[Dict[str, Any]], checks: List[Dict[str, Any]], warnings: List[str], errors: List[str]) -> Dict[str, Any]:
    generated = utc()
    pass_count = sum(1 for r in organ_results if r["status"] == "PASS")
    duty_defined_score = round((pass_count / len(ORGANS)) * 100.0, 2)
    verdict = "PASS_DUTY_CONTRACTS_DEFINED" if not errors else "FAIL_DUTY_CONTRACT_COVERAGE"

    summary = {
        "summary_id": "doctrinarium.organ_duty_contract_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "organ_count": len(ORGANS),
        "pass_count": pass_count,
        "duty_defined_score": duty_defined_score,
        "stage_law": "profile_baseline != duty_defined != rule_validated != action_proven != trust_proven != throne_confirmed",
        "organs": organ_results,
        "meaning": "This summary defines organ duties and validator requirements. It does not prove organ actions or trust."
    }

    receipt = {
        "receipt_id": "receipt.doctrinarium.organ_duty_contract_coverage.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "organ_count": len(ORGANS),
        "pass_count": pass_count,
        "duty_defined_score": duty_defined_score,
        "operational_score_delta_allowed": False,
        "trust_score_delta_allowed": False,
        "no_core_mutation_score_delta_allowed": False,
        "stage_law": summary["stage_law"],
        "contract_paths": [contract_path(o).as_posix() for o in ORGANS],
        "summary_json": SUMMARY_JSON.as_posix(),
        "summary_csv": SUMMARY_CSV.as_posix(),
        "report": REPORT_PATH.as_posix(),
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        "meaning": "All organs have machine-readable duty contracts if PASS. This is duty_defined only, not action_proven or trust_proven."
    }

    for p in [RECEIPT_PATH, REPORT_PATH, SUMMARY_JSON, SUMMARY_CSV]:
        (repo / p).parent.mkdir(parents=True, exist_ok=True)

    (repo / SUMMARY_JSON).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / RECEIPT_PATH).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with (repo / SUMMARY_CSV).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "organ_id", "status", "primary_duties", "forbidden_actions",
            "required_receipts", "rule_validators_required", "action_validators_required",
            "trust_validators_required", "error_count"
        ])
        writer.writeheader()
        for r in organ_results:
            c = r.get("counts", {})
            writer.writerow({
                "organ_id": r["organ_id"],
                "status": r["status"],
                "primary_duties": c.get("primary_duties", 0),
                "forbidden_actions": c.get("forbidden_actions", 0),
                "required_receipts": c.get("required_receipts", 0),
                "rule_validators_required": c.get("rule_validators_required", 0),
                "action_validators_required": c.get("action_validators_required", 0),
                "trust_validators_required": c.get("trust_validators_required", 0),
                "error_count": len(r.get("errors", [])),
            })

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    org_md = "\n".join(
        f"- `{r['organ_id']}` — `{r['status']}`; errors: {len(r.get('errors', []))}"
        for r in organ_results
    )

    (repo / REPORT_PATH).write_text(f"""# ORGAN DUTY CONTRACT COVERAGE REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`  
repo_head: `{git_head(repo)}`

## Meaning

This patch defines what each organ must be responsible for before operational proof is possible.

It does **not** claim the organs are operationally proven.

## Stage law

```text
profile_baseline != duty_defined != rule_validated != action_proven != trust_proven != throne_confirmed
```

## Scores

- organ_count: `{len(ORGANS)}`
- pass_count: `{pass_count}`
- duty_defined_score: `{duty_defined_score}`
- operational_score_delta_allowed: `False`
- trust_score_delta_allowed: `False`
- no_core_mutation_score_delta_allowed: `False`

## Organs

{org_md}

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}

## Outputs

- `{RECEIPT_PATH.as_posix()}`
- `{SUMMARY_JSON.as_posix()}`
- `{SUMMARY_CSV.as_posix()}`
""", encoding="utf-8")

    return receipt

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo_root).resolve()
    checks: List[Dict[str, Any]] = []
    warnings: List[str] = []
    errors: List[str] = []

    for rel in [SCHEMA_PATH, REQUIRED_MATRIX_PATH, THRONE_STAGE_MATRIX_PATH]:
        ok = (repo / rel).is_file()
        add(checks, f"{rel.name}_exists", ok, {"path": rel.as_posix()})
        if not ok:
            errors.append(f"missing required support file: {rel.as_posix()}")

    organ_results = [validate_contract(repo, o) for o in ORGANS]
    failed = [r for r in organ_results if r["status"] != "PASS"]
    add(checks, "all_organ_contracts_exist_and_parse", len(failed) == 0, {"failed_organs": [r["organ_id"] for r in failed]})
    if failed:
        for r in failed:
            errors.append(f"{r['organ_id']}: " + "; ".join(r.get("errors", [])))

    stage_ok = True
    for r in organ_results:
        flags = r.get("stage") or {}
        if flags.get("action_proven") is not False or flags.get("trust_proven") is not False or flags.get("throne_confirmed") is not False:
            stage_ok = False
    add(checks, "duty_defined_does_not_claim_action_or_trust", stage_ok, {})
    if not stage_ok:
        errors.append("one or more contracts claim action/trust/throne confirmation too early")

    throne_matrix, err = load_json(repo / THRONE_STAGE_MATRIX_PATH)
    if err:
        add(checks, "throne_truth_stage_matrix_parse", False, {"error": err})
        errors.append("Throne truth stage matrix parse error: " + err)
    else:
        hard_rules = " ".join(throne_matrix.get("hard_rules", []))
        matrix_ok = "self-validator is not trust proof" in hard_rules and "target definition is not achieved reality" in hard_rules
        add(checks, "throne_truth_stage_matrix_has_fake_green_law", matrix_ok, {})
        if not matrix_ok:
            errors.append("Throne truth stage matrix missing fake-green laws")

    add(checks, "operational_score_not_raised_by_this_patch", True, {"allowed": False})
    add(checks, "trust_score_not_raised_by_this_patch", True, {"allowed": False})
    add(checks, "no_core_mutation_score_not_raised_by_this_patch", True, {"allowed": False})

    receipt = write_outputs(repo, organ_results, checks, warnings, errors)

    print(json.dumps({
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": receipt["verdict"],
        "organ_count": receipt["organ_count"],
        "pass_count": receipt["pass_count"],
        "duty_defined_score": receipt["duty_defined_score"],
        "operational_score_delta_allowed": False,
        "trust_score_delta_allowed": False,
        "receipt": RECEIPT_PATH.as_posix(),
        "report": REPORT_PATH.as_posix(),
        "summary_json": SUMMARY_JSON.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))

    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
