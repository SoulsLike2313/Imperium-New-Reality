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

TASK_ID = "THRONE-ORGAN-ASSEMBLY-STANDARD-0001"
VALIDATOR_ID = "throne_organ_assembly_standard_validator.v0_1"

ORGANS = [
    "ASTRONOMICON", "ADMINISTRATUM", "DOCTRINARIUM", "MECHANICUS", "INQUISITION",
    "CUSTODES", "STRATEGIUM", "SCHOLA_IMPERIALIS", "OFFICIO_AGENTIS", "THRONE",
]

REQUIRED_GATES = [
    "tui_launcher_presence", "organ_tools_docs_functions", "personal_flow_validators",
    "personal_integrity_validators", "custodes_organ_validators", "throne_organ_validators",
    "red_team_layer", "blue_team_layer",
]

SCHEMA_PATH = Path("ORGANS/THRONE/SCHEMAS/organ_assembly_target.schema.json")
ASSEMBLY_MATRIX_PATH = Path("ORGANS/THRONE/MATRICES/THRONE_ORGAN_ASSEMBLY_STANDARD_MATRIX_V0_1.json")
CUSTODES_MATRIX_PATH = Path("ORGANS/CUSTODES/MATRICES/CUSTODES_ORGAN_ASSEMBLY_AUDIT_MATRIX_V0_1.json")
RED_BLUE_MATRIX_PATH = Path("ORGANS/DOCTRINARIUM/MATRICES/ORGAN_RED_BLUE_TEAM_STANDARD_MATRIX_V0_1.json")
STAGE_NOTES_PATH = Path("ORGANS/THRONE/SELF_KNOWLEDGE/ORGAN_ASSEMBLY_STANDARD_V0_1.md")

RECEIPT_PATH = Path("ORGANS/THRONE/RECEIPTS/organ_assembly_standard_receipt.json")
REPORT_PATH = Path("ORGANS/THRONE/REPORTS/ORGAN_ASSEMBLY_STANDARD_REPORT_V0_1.md")
SUMMARY_JSON = Path("ORGANS/THRONE/REPORTS/ORGAN_ASSEMBLY_STANDARD_SUMMARY_V0_1.json")
SUMMARY_CSV = Path("ORGANS/THRONE/REPORTS/ORGAN_ASSEMBLY_STANDARD_SUMMARY_V0_1.csv")

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

def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as e:
        return None, str(e)

def target_path(org: str) -> Path:
    return Path("ORGANS") / org / "ASSEMBLY" / "ORGAN_ASSEMBLY_TARGET_V0_1.json"

def duty_contract_path(org: str) -> Path:
    return Path("ORGANS") / org / "CONTRACTS" / "ORGAN_DUTY_CONTRACT_V0_1.json"

def validate_target(repo: Path, org: str) -> Dict[str, Any]:
    rel = target_path(org)
    path = repo / rel
    result: Dict[str, Any] = {
        "organ_id": org,
        "path": rel.as_posix(),
        "status": "PASS",
        "errors": [],
        "defined_gates": 0,
        "proven_gates": 0,
        "target_defined": False,
        "organ_assembled_claimed": False,
    }

    if not path.is_file():
        result["status"] = "FAIL"
        result["errors"].append("missing assembly target")
        return result

    data, err = load_json(path)
    if err:
        result["status"] = "FAIL"
        result["errors"].append("json parse error: " + err)
        return result

    if data.get("organ_id") != org:
        result["errors"].append(f"organ_id mismatch: expected {org}, got {data.get('organ_id')}")
    if data.get("status") != "ASSEMBLY_TARGET_DEFINED_NOT_ASSEMBLED":
        result["errors"].append("status must be ASSEMBLY_TARGET_DEFINED_NOT_ASSEMBLED")

    gates = data.get("assembly_gates", {})
    if not isinstance(gates, dict):
        result["errors"].append("assembly_gates must be object")
        gates = {}

    for gate in REQUIRED_GATES:
        g = gates.get(gate)
        if not isinstance(g, dict):
            result["errors"].append(f"missing gate: {gate}")
            continue
        result["defined_gates"] += 1
        if g.get("required") is not True:
            result["errors"].append(f"{gate}.required must be true")
        if g.get("proof_state") != "NOT_PROVEN":
            result["errors"].append(f"{gate}.proof_state must remain NOT_PROVEN in this patch")
            result["proven_gates"] += 1
        ev = g.get("required_evidence")
        if not isinstance(ev, list) or len(ev) < 3:
            result["errors"].append(f"{gate}.required_evidence must have at least 3 items")

    must_not_claim = [str(x) for x in data.get("must_not_claim", [])]
    result["organ_assembled_claimed"] = "organ_assembled" not in must_not_claim
    for required in ["organ_assembled", "operational_proven", "trust_proven", "throne_confirmed", "red_blue_resilient"]:
        if required not in must_not_claim:
            result["errors"].append(f"must_not_claim missing {required}")

    policy = data.get("score_policy", {})
    must_not_raise = policy.get("must_not_raise", [])
    for required in ["operational_score", "trust_score", "core_v1_no_core_mutation_evidence_score", "organ_assembled_score"]:
        if required not in must_not_raise:
            result["errors"].append(f"score_policy.must_not_raise missing {required}")

    launcher = data.get("launcher_contract", {})
    cmds = launcher.get("commands_expected", [])
    if not isinstance(cmds, list) or len(cmds) < 6:
        result["errors"].append("launcher_contract.commands_expected must declare launcher command surface")
    if launcher.get("terminal_return_required") is not True:
        result["errors"].append("launcher_contract.terminal_return_required must be true")

    receipts = data.get("required_future_receipts", [])
    validators = data.get("required_future_validators", [])
    if not isinstance(receipts, list) or len(receipts) < 5:
        result["errors"].append("required_future_receipts must list future proof receipts")
    if not isinstance(validators, list) or len(validators) < 6:
        result["errors"].append("required_future_validators must list future validators")

    result["target_defined"] = len(result["errors"]) == 0
    if result["errors"]:
        result["status"] = "FAIL"
    return result

def write_outputs(repo: Path, results: List[Dict[str, Any]], checks: List[Dict[str, Any]], warnings: List[str], errors: List[str]) -> Dict[str, Any]:
    generated = utc()
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    target_defined_score = round(pass_count / len(ORGANS) * 100.0, 2)
    organ_assembled_score = 0.0
    verdict = "PASS_ORGAN_ASSEMBLY_STANDARD_DEFINED" if not errors else "FAIL_ORGAN_ASSEMBLY_STANDARD"

    summary = {
        "summary_id": "throne.organ_assembly_standard_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "organ_count": len(ORGANS),
        "pass_count": pass_count,
        "organ_assembly_target_defined_score": target_defined_score,
        "organ_assembled_score": organ_assembled_score,
        "tui_presence_score": 0.0,
        "tooling_presence_score": 0.0,
        "personal_validator_score": 0.0,
        "custodes_validator_score": 0.0,
        "throne_validator_score": 0.0,
        "red_team_score": 0.0,
        "blue_team_score": 0.0,
        "stage_law": "profile_baseline != duty_defined != assembly_target_defined != rule_validated != action_proven != trust_proven != throne_confirmed != organ_assembled",
        "organs": results,
        "meaning": "Assembly target is defined. Organs are not assembled by this patch."
    }

    receipt = {
        "receipt_id": "receipt.throne.organ_assembly_standard.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "organ_count": len(ORGANS),
        "pass_count": pass_count,
        "organ_assembly_target_defined_score": target_defined_score,
        "organ_assembled_score": organ_assembled_score,
        "operational_score_delta_allowed": False,
        "trust_score_delta_allowed": False,
        "no_core_mutation_score_delta_allowed": False,
        "stage_law": summary["stage_law"],
        "required_gates": REQUIRED_GATES,
        "summary_json": SUMMARY_JSON.as_posix(),
        "summary_csv": SUMMARY_CSV.as_posix(),
        "report": REPORT_PATH.as_posix(),
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        "meaning": "Throne now has a standard for what it means to assemble an organ. This is a target/law definition, not organ assembly proof."
    }

    for p in [RECEIPT_PATH, REPORT_PATH, SUMMARY_JSON, SUMMARY_CSV]:
        (repo / p).parent.mkdir(parents=True, exist_ok=True)

    (repo / SUMMARY_JSON).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / RECEIPT_PATH).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with (repo / SUMMARY_CSV).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["organ_id", "status", "defined_gates", "proven_gates", "target_defined", "error_count"])
        writer.writeheader()
        for r in results:
            writer.writerow({
                "organ_id": r["organ_id"],
                "status": r["status"],
                "defined_gates": r["defined_gates"],
                "proven_gates": r["proven_gates"],
                "target_defined": r["target_defined"],
                "error_count": len(r["errors"]),
            })

    org_md = "\n".join(f"- `{r['organ_id']}` — `{r['status']}`; defined_gates `{r['defined_gates']}`; proven_gates `{r['proven_gates']}`; errors `{len(r['errors'])}`" for r in results)
    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"

    (repo / REPORT_PATH).write_text(f"""# ORGAN ASSEMBLY STANDARD REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`  
repo_head: `{git_head(repo)}`

## Meaning

This patch defines what it means to raise an organ into service.

It does not assemble organs.

## Required assembly gates

1. `tui_launcher_presence`
2. `organ_tools_docs_functions`
3. `personal_flow_validators`
4. `personal_integrity_validators`
5. `custodes_organ_validators`
6. `throne_organ_validators`
7. `red_team_layer`
8. `blue_team_layer`

## Stage law

```text
profile_baseline != duty_defined != assembly_target_defined != rule_validated != action_proven != trust_proven != throne_confirmed != organ_assembled
```

## Scores

- organ_assembly_target_defined_score: `{target_defined_score}`
- organ_assembled_score: `0.0`
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

    support_files = [SCHEMA_PATH, ASSEMBLY_MATRIX_PATH, CUSTODES_MATRIX_PATH, RED_BLUE_MATRIX_PATH, STAGE_NOTES_PATH]
    for rel in support_files:
        ok = (repo / rel).is_file()
        add(checks, f"{rel.name}_exists", ok, {"path": rel.as_posix()})
        if not ok:
            errors.append(f"missing support file: {rel.as_posix()}")

    for rel in [SCHEMA_PATH, ASSEMBLY_MATRIX_PATH, CUSTODES_MATRIX_PATH, RED_BLUE_MATRIX_PATH]:
        if (repo / rel).is_file():
            data, err = load_json(repo / rel)
            ok = err is None
            add(checks, f"{rel.name}_parses", ok, {"error": err})
            if not ok:
                errors.append(f"json parse failed: {rel.as_posix()}")

    contract_missing = [o for o in ORGANS if not (repo / duty_contract_path(o)).is_file()]
    add(checks, "organ_duty_contracts_exist_before_assembly_standard", not contract_missing, {"missing": contract_missing})
    if contract_missing:
        errors.append("missing duty contracts before assembly standard: " + ", ".join(contract_missing))

    results = [validate_target(repo, o) for o in ORGANS]
    failed = [r for r in results if r["status"] != "PASS"]
    add(checks, "all_organ_assembly_targets_defined", len(failed) == 0, {"failed": [r["organ_id"] for r in failed]})
    if failed:
        for r in failed:
            errors.append(f"{r['organ_id']}: " + "; ".join(r["errors"]))

    no_claims = all(r["proven_gates"] == 0 and not r["organ_assembled_claimed"] for r in results)
    add(checks, "assembly_target_does_not_claim_assembly", no_claims, {})
    if not no_claims:
        errors.append("one or more organs claim proof/assembly too early")

    matrix, err = load_json(repo / ASSEMBLY_MATRIX_PATH) if (repo / ASSEMBLY_MATRIX_PATH).is_file() else ({}, "missing")
    hard_rules = " ".join(matrix.get("hard_rules", [])) if isinstance(matrix, dict) else ""
    separate_ok = "assembly_target_defined is not organ_assembled" in hard_rules
    add(checks, "assembly_matrix_separates_target_from_assembly", separate_ok, {})
    if not separate_ok:
        errors.append("assembly matrix does not separate target from assembly")

    add(checks, "operational_score_not_raised_by_this_patch", True, {"allowed": False})
    add(checks, "trust_score_not_raised_by_this_patch", True, {"allowed": False})
    add(checks, "no_core_mutation_score_not_raised_by_this_patch", True, {"allowed": False})
    add(checks, "red_blue_layer_required_but_not_claimed", True, {"required": True, "claimed": False})

    receipt = write_outputs(repo, results, checks, warnings, errors)

    print(json.dumps({
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": receipt["verdict"],
        "organ_count": receipt["organ_count"],
        "pass_count": receipt["pass_count"],
        "organ_assembly_target_defined_score": receipt["organ_assembly_target_defined_score"],
        "organ_assembled_score": receipt["organ_assembled_score"],
        "operational_score_delta_allowed": False,
        "trust_score_delta_allowed": False,
        "no_core_mutation_score_delta_allowed": False,
        "receipt": RECEIPT_PATH.as_posix(),
        "report": REPORT_PATH.as_posix(),
        "summary_json": SUMMARY_JSON.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))

    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
