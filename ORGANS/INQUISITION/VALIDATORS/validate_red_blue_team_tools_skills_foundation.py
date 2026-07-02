#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

TASK_ID = "RED-BLUE-TEAM-TOOLS-AND-SKILLS-FOUNDATION-0001"
VALIDATOR_ID = "red_blue_team_tools_skills_foundation_validator.v0_1"

MATRIX = Path("ORGANS/DOCTRINARIUM/MATRICES/ORGAN_RED_BLUE_TEAM_SKILLS_MATRIX_V0_1.json")
DOCTRINE = Path("ORGANS/DOCTRINARIUM/DOCTRINE/RED_BLUE_TEAM_TOOLS_AND_SKILLS_FOUNDATION_V0_1.md")
SCAN = Path("ORGANS/INQUISITION/TOOLS/red_blue_team_skills_scan.py")

RECEIPT = Path("ORGANS/INQUISITION/RECEIPTS/red_blue_team_tools_skills_foundation_receipt.json")
REPORT = Path("ORGANS/INQUISITION/REPORTS/RED_BLUE_TEAM_TOOLS_SKILLS_FOUNDATION_REPORT_V0_1.md")
SUMMARY = Path("ORGANS/INQUISITION/REPORTS/RED_BLUE_TEAM_TOOLS_SKILLS_FOUNDATION_SUMMARY_V0_1.json")

ORGANS = ["ASTRONOMICON","ADMINISTRATUM","DOCTRINARIUM","MECHANICUS","INQUISITION","CUSTODES","STRATEGIUM","SCHOLA_IMPERIALIS","OFFICIO_AGENTIS","THRONE"]
FORBIDDEN_CLAIMS = ["RED_TEAM_PROVEN","BLUE_TEAM_PROVEN","CUSTODES_TRUST","THRONE_VERDICT","ORGAN_ASSEMBLED","EXECUTION_ALLOWED"]

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

def git_head(repo: Path) -> str:
    try:
        p = subprocess.run(["git","rev-parse","HEAD"], cwd=str(repo), capture_output=True, text=True, timeout=15)
        return p.stdout.strip() if p.returncode == 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"

def load_json(path: Path) -> Tuple[Any, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), None
    except Exception as e:
        return None, str(e)

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def run_py(repo: Path, script: Path, args: List[str]) -> Tuple[int, str, str]:
    p = subprocess.run([sys.executable, str(repo / script)] + args, cwd=str(repo), capture_output=True, text=True, timeout=120)
    return p.returncode, p.stdout, p.stderr

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    for rel in [MATRIX, DOCTRINE, SCAN]:
        ok = (repo / rel).is_file()
        add(checks, f"{rel.name}_exists", ok, {"path": rel.as_posix()})
        if not ok:
            errors.append(f"missing {rel.as_posix()}")

    matrix, err = load_json(repo / MATRIX) if (repo / MATRIX).is_file() else ({}, "missing")
    add(checks, "red_blue_matrix_parses", err is None, {"error": err})
    if err:
        errors.append("red/blue matrix parse failed")
        matrix = {}

    required = matrix.get("required_per_organ_fields", []) if isinstance(matrix, dict) else []
    for field in ["red_team", "blue_team", "red_skills", "blue_skills", "proof_state", "required_future_validators"]:
        add(checks, f"matrix_requires_{field}", field in required, {"required": required})
        if field not in required:
            errors.append(f"matrix does not require {field}")

    missing_contracts = []
    bad_contracts = []
    for organ in ORGANS:
        path = repo / "ORGANS" / organ / "RED_BLUE" / "ORGAN_RED_BLUE_SKILLS_V0_1.json"
        if not path.is_file():
            missing_contracts.append(organ)
            continue
        data, e = load_json(path)
        if e or not isinstance(data, dict):
            bad_contracts.append({"organ": organ, "error": e})
            continue
        if data.get("organ_id") != organ:
            bad_contracts.append({"organ": organ, "error": "organ_id mismatch"})
        if data.get("proof_state") != "DEFINED_NOT_PROVEN":
            bad_contracts.append({"organ": organ, "error": "proof_state not DEFINED_NOT_PROVEN"})
        if len(data.get("red_team", {}).get("skills", [])) < 3:
            bad_contracts.append({"organ": organ, "error": "less than 3 red skills"})
        if len(data.get("blue_team", {}).get("skills", [])) < 3:
            bad_contracts.append({"organ": organ, "error": "less than 3 blue skills"})
        for claim in FORBIDDEN_CLAIMS:
            if claim not in data.get("forbidden_claims", []):
                bad_contracts.append({"organ": organ, "error": f"missing forbidden claim {claim}"})

    add(checks, "all_organs_have_red_blue_contracts", not missing_contracts, {"missing": missing_contracts})
    add(checks, "all_red_blue_contracts_valid_shape", not bad_contracts, {"bad": bad_contracts[:20]})
    if missing_contracts:
        errors.append("missing red/blue contracts: " + ", ".join(missing_contracts))
    if bad_contracts:
        errors.append("bad red/blue contract shapes")

    code, out, errout = run_py(repo, SCAN, ["--repo-root", str(repo)])
    add(checks, "red_blue_scan_tool_runs", code == 0, {"stderr": errout[-1000:]})
    if code != 0:
        errors.append("red/blue scan tool failed")

    scan_summary, scan_err = load_json(repo / "ORGANS/INQUISITION/REPORTS/RED_BLUE_TEAM_SKILLS_SCAN_SUMMARY_V0_1.json")
    add(checks, "red_blue_scan_summary_parses", scan_err is None, {"error": scan_err})
    if scan_err:
        errors.append("red/blue scan summary parse failed")
        scan_summary = {}

    add(checks, "red_blue_defined_scores_are_100", scan_summary.get("red_team_defined_score") == 100.0 and scan_summary.get("blue_team_defined_score") == 100.0, {"red": scan_summary.get("red_team_defined_score"), "blue": scan_summary.get("blue_team_defined_score")})
    add(checks, "red_blue_proof_scores_remain_zero", scan_summary.get("red_team_proven_score") == 0.0 and scan_summary.get("blue_team_proven_score") == 0.0, {"red_proven": scan_summary.get("red_team_proven_score"), "blue_proven": scan_summary.get("blue_team_proven_score")})
    if scan_summary.get("red_team_defined_score") != 100.0 or scan_summary.get("blue_team_defined_score") != 100.0:
        errors.append("red/blue definition scores not 100")
    if scan_summary.get("red_team_proven_score") != 0.0 or scan_summary.get("blue_team_proven_score") != 0.0:
        errors.append("red/blue proof scores should remain zero")

    verdict = "PASS_RED_BLUE_TEAM_TOOLS_SKILLS_FOUNDATION_READY" if not errors else "FAIL_RED_BLUE_TEAM_TOOLS_SKILLS_FOUNDATION"
    generated = utc()
    summary = {
        "summary_id": "inquisition.red_blue_team_tools_skills_foundation_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "organ_count": len(ORGANS),
        "red_team_defined_score": scan_summary.get("red_team_defined_score"),
        "blue_team_defined_score": scan_summary.get("blue_team_defined_score"),
        "red_team_proven_score": scan_summary.get("red_team_proven_score"),
        "blue_team_proven_score": scan_summary.get("blue_team_proven_score"),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "not_claimed": ["Custodes trust", "Throne verdict", "organ assembled"]
    }
    receipt = {
        "receipt_id": "receipt.inquisition.red_blue_team_tools_skills_foundation.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Every organ has Red/Blue skill definitions. Proof remains zero."
    }

    for p in [SUMMARY, RECEIPT, REPORT]:
        (repo / p).parent.mkdir(parents=True, exist_ok=True)
    (repo / SUMMARY).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# RED + BLUE TEAM TOOLS AND SKILLS FOUNDATION REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`  
repo_head: `{git_head(repo)}`

## Meaning

Every organ now has Red Team and Blue Team skill definitions.

This is not proof. It is a foundation.

## Scores

- red_team_defined_score: `{scan_summary.get("red_team_defined_score")}`
- blue_team_defined_score: `{scan_summary.get("blue_team_defined_score")}`
- red_team_proven_score: `{scan_summary.get("red_team_proven_score")}`
- blue_team_proven_score: `{scan_summary.get("blue_team_proven_score")}`

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}
""", encoding="utf-8")

    print(json.dumps({
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "organ_count": len(ORGANS),
        "red_team_defined_score": scan_summary.get("red_team_defined_score"),
        "blue_team_defined_score": scan_summary.get("blue_team_defined_score"),
        "red_team_proven_score": scan_summary.get("red_team_proven_score"),
        "blue_team_proven_score": scan_summary.get("blue_team_proven_score"),
        "receipt": RECEIPT.as_posix(),
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
