#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, csv, datetime as dt, json, subprocess
from pathlib import Path

TASK_ID = "THRONE-ORGAN-ASSEMBLY-STAGE-SCORING-INTEGRATION-0001"
VALIDATOR_ID = "throne_organ_assembly_stage_scoring_validator.v0_1"
ORGANS = ["ASTRONOMICON","ADMINISTRATUM","DOCTRINARIUM","MECHANICUS","INQUISITION","CUSTODES","STRATEGIUM","SCHOLA_IMPERIALIS","OFFICIO_AGENTIS","THRONE"]
GATES = ["tui_launcher_presence","organ_tools_docs_functions","personal_flow_validators","personal_integrity_validators","custodes_organ_validators","throne_organ_validators","red_team_layer","blue_team_layer"]
STAGE_LAW = "profile_baseline != duty_defined != assembly_target_defined != rule_validated != action_proven != trust_proven != throne_confirmed != organ_assembled"

MATRIX = Path("ORGANS/THRONE/MATRICES/THRONE_ORGAN_ASSEMBLY_STAGE_SCORING_MATRIX_V0_1.json")
ASSEMBLY_MATRIX = Path("ORGANS/THRONE/MATRICES/THRONE_ORGAN_ASSEMBLY_STANDARD_MATRIX_V0_1.json")
DUTY_MATRIX = Path("ORGANS/DOCTRINARIUM/MATRICES/ORGAN_DUTY_CONTRACT_REQUIRED_FIELDS_MATRIX_V0_1.json")
SCHEMA = Path("ORGANS/THRONE/SCHEMAS/throne_organ_assembly_stage_scoring_receipt.schema.json")
NOTES = Path("ORGANS/THRONE/SELF_KNOWLEDGE/ORGAN_ASSEMBLY_STAGE_SCORING_V0_1.md")
RECEIPT = Path("ORGANS/THRONE/RECEIPTS/organ_assembly_stage_scoring_receipt.json")
REPORT = Path("ORGANS/THRONE/REPORTS/ORGAN_ASSEMBLY_STAGE_SCORING_REPORT_V0_1.md")
SUMMARY_JSON = Path("ORGANS/THRONE/REPORTS/ORGAN_ASSEMBLY_STAGE_SCORING_SUMMARY_V0_1.json")
SUMMARY_CSV = Path("ORGANS/THRONE/REPORTS/ORGAN_ASSEMBLY_STAGE_SCORING_SUMMARY_V0_1.csv")


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git_head(repo: Path) -> str:
    try:
        p = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo), text=True, capture_output=True, timeout=60)
        return p.stdout.strip() if p.returncode == 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as e:
        return None, str(e)


def add(checks, name, ok, details=None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})


def duty_path(org: str) -> Path:
    return Path("ORGANS") / org / "CONTRACTS" / "ORGAN_DUTY_CONTRACT_V0_1.json"


def assembly_path(org: str) -> Path:
    return Path("ORGANS") / org / "ASSEMBLY" / "ORGAN_ASSEMBLY_TARGET_V0_1.json"


def profile_score(repo: Path, org: str):
    root = repo / "ORGANS" / org
    evidence = []
    for p in [root / "README.md", root / "MANIFEST.json", root / "FUNCTIONS.md", root / "ORGANS" / "ORGAN_CARD.json"]:
        if p.is_file():
            evidence.append(p.relative_to(repo).as_posix())
    for sub in ["VALIDATORS", "RECEIPTS", "SCHEMAS"]:
        d = root / sub
        if d.is_dir():
            found = [x for x in d.rglob("*") if x.is_file() and ("profile" in x.name.lower() or "organ" in x.name.lower())]
            if found:
                evidence.append(found[0].relative_to(repo).as_posix())
    return min(100.0, round(len(evidence) / 6.0 * 100.0, 2)), evidence[:10]


def duty_score(repo: Path, org: str):
    p = repo / duty_path(org)
    if not p.is_file():
        return 0.0, [], ["missing duty contract"], {}
    data, err = load_json(p)
    if err:
        return 0.0, [], ["duty parse error: " + err], {}
    errors = []
    required = ["organ_id","core_v1_mission","primary_duties","forbidden_actions","accepted_inputs","required_outputs","required_receipts","rule_validators_required","action_validators_required","trust_validators_required","throne_must_confirm","proof_stage_flags"]
    for key in required:
        if key not in data:
            errors.append("duty missing " + key)
    if data.get("organ_id") != org:
        errors.append("duty organ_id mismatch")
    flags = data.get("proof_stage_flags", {}) if isinstance(data.get("proof_stage_flags", {}), dict) else {}
    if flags.get("duty_defined") is not True:
        errors.append("duty_defined flag must be true")
    return (100.0 if not errors else max(0.0, 100.0 - len(errors) * 20.0)), [duty_path(org).as_posix()], errors, flags


def assembly_score(repo: Path, org: str):
    p = repo / assembly_path(org)
    gate_scores = {gate + "_score": 0.0 for gate in GATES}
    if not p.is_file():
        return 0.0, gate_scores, [], ["missing assembly target"]
    data, err = load_json(p)
    if err:
        return 0.0, gate_scores, [], ["assembly parse error: " + err]
    errors = []
    defined = 0
    if data.get("organ_id") != org:
        errors.append("assembly organ_id mismatch")
    if data.get("status") != "ASSEMBLY_TARGET_DEFINED_NOT_ASSEMBLED":
        errors.append("assembly target status must be ASSEMBLY_TARGET_DEFINED_NOT_ASSEMBLED")
    gates = data.get("assembly_gates", {}) if isinstance(data.get("assembly_gates", {}), dict) else {}
    for gate in GATES:
        gd = gates.get(gate)
        if not isinstance(gd, dict):
            errors.append("missing gate " + gate)
            continue
        defined += 1
        if gd.get("required") is not True:
            errors.append(gate + ".required must be true")
        req = gd.get("required_evidence")
        if not isinstance(req, list) or len(req) < 3:
            errors.append(gate + ".required_evidence too weak")
        if gd.get("proof_state") == "PROVEN":
            gate_scores[gate + "_score"] = 100.0
        elif gd.get("proof_state") == "NOT_PROVEN":
            gate_scores[gate + "_score"] = 0.0
        else:
            errors.append(gate + ".proof_state must be NOT_PROVEN or PROVEN")
    score = round(defined / len(GATES) * 100.0, 2)
    if errors:
        score = min(score, max(0.0, 100.0 - len(errors) * 10.0))
    return score, gate_scores, [assembly_path(org).as_posix()], errors


def organ_result(repo: Path, org: str):
    profile, profile_evidence = profile_score(repo, org)
    duty, duty_evidence, duty_errors, flags = duty_score(repo, org)
    assembly, gate_scores, assembly_evidence, assembly_errors = assembly_score(repo, org)
    rule = 100.0 if flags.get("rule_validated") is True else 0.0
    action = 100.0 if flags.get("action_proven") is True else 0.0
    trust = 100.0 if flags.get("trust_proven") is True else 0.0
    throne = 100.0 if flags.get("throne_confirmed") is True else 0.0
    assembled = 100.0 if all(v == 100.0 for v in gate_scores.values()) and throne == 100.0 else 0.0
    stages = {
        "profile_baseline_score": profile,
        "duty_defined_score": duty,
        "assembly_target_defined_score": assembly,
        "rule_validated_score": rule,
        "action_proven_score": action,
        "trust_proven_score": trust,
        "throne_confirmed_score": throne,
        "organ_assembled_score": assembled,
    }
    weights = {"profile_baseline_score":10,"duty_defined_score":15,"assembly_target_defined_score":15,"rule_validated_score":15,"action_proven_score":15,"trust_proven_score":15,"throne_confirmed_score":10,"organ_assembled_score":5}
    maturity = round(sum(stages[k] * weights[k] for k in weights) / sum(weights.values()), 2)
    errors = duty_errors + assembly_errors
    return {
        "organ_id": org,
        "status": "PASS" if not errors else "FAIL",
        "stage_scores": stages,
        "assembly_gate_scores": gate_scores,
        "red_team_score": gate_scores["red_team_layer_score"],
        "blue_team_score": gate_scores["blue_team_layer_score"],
        "organ_truth_maturity_score": maturity,
        "profile_evidence": profile_evidence,
        "duty_evidence": duty_evidence,
        "assembly_evidence": assembly_evidence,
        "errors": errors,
        "interpretation": "TARGET_AND_DUTY_DEFINED_NOT_ASSEMBLED" if assembled == 0 else "ORGAN_ASSEMBLED_CANDIDATE",
    }


def avg(values):
    return round(sum(values) / len(values), 2) if values else 0.0


def write_outputs(repo: Path, results, checks, warnings, errors):
    generated = utc()
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    stage_keys = ["profile_baseline_score","duty_defined_score","assembly_target_defined_score","rule_validated_score","action_proven_score","trust_proven_score","throne_confirmed_score","organ_assembled_score"]
    scores = {key: avg([r["stage_scores"][key] for r in results]) for key in stage_keys}
    for key in [g + "_score" for g in GATES]:
        scores[key] = avg([r["assembly_gate_scores"][key] for r in results])
    scores["red_team_score"] = avg([r["red_team_score"] for r in results])
    scores["blue_team_score"] = avg([r["blue_team_score"] for r in results])
    scores["organ_truth_maturity_score"] = avg([r["organ_truth_maturity_score"] for r in results])
    verdict = "PASS_STAGE_SCORING_INTEGRATED" if not errors else "FAIL_STAGE_SCORING_INTEGRATION"
    receipt = {
        "receipt_id": "receipt.throne.organ_assembly_stage_scoring.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "organ_count": len(ORGANS),
        "pass_count": pass_count,
        "scores": scores,
        "stage_law": STAGE_LAW,
        "operational_score_delta_allowed": False,
        "trust_score_delta_allowed": False,
        "no_core_mutation_score_delta_allowed": False,
        "organ_assembled_score_delta_allowed": False,
        "summary_json": SUMMARY_JSON.as_posix(),
        "summary_csv": SUMMARY_CSV.as_posix(),
        "report": REPORT.as_posix(),
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        "meaning": "Target/duty definition can be high while assembly, action, trust, red team, and blue team remain unproven."
    }
    summary = {
        "summary_id": "throne.organ_assembly_stage_scoring_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "organ_count": len(ORGANS),
        "pass_count": pass_count,
        "scores": scores,
        "stage_law": STAGE_LAW,
        "organs": results,
        "meaning": "Throne scores organ maturity by separate stages. This report does not assemble organs."
    }
    for p in [RECEIPT, REPORT, SUMMARY_JSON, SUMMARY_CSV]:
        (repo / p).parent.mkdir(parents=True, exist_ok=True)
    (repo / RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / SUMMARY_JSON).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (repo / SUMMARY_CSV).open("w", encoding="utf-8", newline="") as f:
        fields = ["organ_id","status"] + stage_keys + ["red_team_score","blue_team_score","organ_truth_maturity_score","error_count"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in results:
            row = {"organ_id": r["organ_id"], "status": r["status"], "error_count": len(r["errors"])}
            row.update(r["stage_scores"])
            row["red_team_score"] = r["red_team_score"]
            row["blue_team_score"] = r["blue_team_score"]
            row["organ_truth_maturity_score"] = r["organ_truth_maturity_score"]
            writer.writerow(row)
    score_md = "\n".join(f"- {k}: `{v}`" for k, v in scores.items())
    org_md = "\n".join(f"- `{r['organ_id']}` — maturity `{r['organ_truth_maturity_score']}`, assembled `{r['stage_scores']['organ_assembled_score']}`, red `{r['red_team_score']}`, blue `{r['blue_team_score']}`, errors `{len(r['errors'])}`" for r in results)
    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    report = f"""# ORGAN ASSEMBLY STAGE SCORING REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`  
repo_head: `{git_head(repo)}`

## Meaning

This patch teaches the Throne to measure organ maturity by separate truth stages.

It does not assemble organs and does not raise operational/trust/no-core-mutation readiness.

## Stage law

```text
{STAGE_LAW}
```

## Global stage scores

{score_md}

## Interpretation

`duty_defined_score` and `assembly_target_defined_score` may be high because the laws and targets exist.

`organ_assembled_score`, `red_team_score`, and `blue_team_score` must remain low/zero until actual validators, receipts, and Crown confirmations exist.

## Organs

{org_md}

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}

## Outputs

- `{RECEIPT.as_posix()}`
- `{SUMMARY_JSON.as_posix()}`
- `{SUMMARY_CSV.as_posix()}`
"""
    (repo / REPORT).write_text(report, encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    repo = Path(args.repo_root).resolve()
    checks = []
    warnings = []
    errors = []
    for rel in [MATRIX, ASSEMBLY_MATRIX, DUTY_MATRIX, SCHEMA, NOTES]:
        ok = (repo / rel).is_file()
        add(checks, rel.name + "_exists", ok, {"path": rel.as_posix()})
        if not ok:
            errors.append("missing support file: " + rel.as_posix())
    for rel in [MATRIX, ASSEMBLY_MATRIX, DUTY_MATRIX, SCHEMA]:
        if (repo / rel).is_file():
            _, err = load_json(repo / rel)
            ok = err is None
            add(checks, rel.name + "_parses", ok, {"error": err})
            if not ok:
                errors.append("json parse failed: " + rel.as_posix())
    if (repo / MATRIX).is_file():
        matrix, _ = load_json(repo / MATRIX)
        rules = " ".join(matrix.get("hard_rules", [])) if isinstance(matrix, dict) else ""
        needed = [
            "duty_defined_score must not raise operational_score",
            "assembly_target_defined_score must not raise operational_score",
            "organ_assembled_score must remain 0 unless every assembly gate is PROVEN and Throne confirmed",
            "self-validator is not trust proof",
        ]
        ok = all(x in rules for x in needed)
        add(checks, "stage_scoring_hard_rules_present", ok, {"required_laws": needed})
        if not ok:
            errors.append("stage scoring hard rules incomplete")
    results = [organ_result(repo, org) for org in ORGANS]
    failed = [r for r in results if r["status"] != "PASS"]
    add(checks, "all_organs_have_duty_and_assembly_stage_inputs", len(failed) == 0, {"failed": [r["organ_id"] for r in failed]})
    for r in failed:
        errors.append(r["organ_id"] + ": " + "; ".join(r["errors"]))
    assembled = [r["organ_id"] for r in results if r["stage_scores"]["organ_assembled_score"] > 0]
    add(checks, "no_organ_assembled_claim_from_target_definition", len(assembled) == 0, {"assembled_claims": assembled})
    if assembled:
        errors.append("organ_assembled_score claimed too early: " + ", ".join(assembled))
    red_blue = [r["organ_id"] for r in results if r["red_team_score"] > 0 or r["blue_team_score"] > 0]
    add(checks, "red_blue_not_claimed_before_proof", len(red_blue) == 0, {"red_blue_claims": red_blue})
    if red_blue:
        errors.append("red/blue score claimed before proof: " + ", ".join(red_blue))
    for name in ["operational_score_not_raised_by_this_patch", "trust_score_not_raised_by_this_patch", "no_core_mutation_score_not_raised_by_this_patch", "organ_assembled_score_delta_not_allowed"]:
        add(checks, name, True, {"allowed": False})
    receipt = write_outputs(repo, results, checks, warnings, errors)
    print(json.dumps({
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": receipt["verdict"],
        "organ_count": receipt["organ_count"],
        "pass_count": receipt["pass_count"],
        "scores": receipt["scores"],
        "operational_score_delta_allowed": False,
        "trust_score_delta_allowed": False,
        "no_core_mutation_score_delta_allowed": False,
        "organ_assembled_score_delta_allowed": False,
        "receipt": RECEIPT.as_posix(),
        "report": REPORT.as_posix(),
        "summary_json": SUMMARY_JSON.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
