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

TASK_ID = "CUSTODES-ASTRONOMICON-VALIDATION-INVOKE-CONTRACT-FIX-0001"
VALIDATOR_ID = "custodes_astronomicon_validation_invoke_contract_fix_validator.v0_1"

AUDIT = Path("ORGANS/CUSTODES/TOOLS/custodes_audit_astronomicon.py")
MATRIX = Path("ORGANS/CUSTODES/MATRICES/CUSTODES_VALIDATOR_INVOKE_CONTRACTS_V0_1.json")
RECEIPT = Path("ORGANS/CUSTODES/RECEIPTS/custodes_astronomicon_validation_receipt.json")
SUMMARY = Path("ORGANS/CUSTODES/REPORTS/CUSTODES_ASTRONOMICON_VALIDATION_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/CUSTODES/REPORTS/CUSTODES_ASTRONOMICON_VALIDATION_REPORT_V0_1.md")

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

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    checks = []
    errors = []
    warnings = []

    for rel in [AUDIT, MATRIX]:
        ok = (repo / rel).is_file()
        add(checks, f"{rel.name}_exists", ok, {"path": rel.as_posix()})
        if not ok: errors.append(f"missing {rel.as_posix()}")

    matrix, matrix_err = load_json(repo / MATRIX) if (repo / MATRIX).is_file() else ({}, "missing")
    add(checks, "invoke_contract_matrix_parses", matrix_err is None, {"error": matrix_err})
    if matrix_err: errors.append("invoke contract matrix parse failed")
    contracts = matrix.get("validator_contracts", []) if isinstance(matrix, dict) else []
    add(checks, "invoke_contracts_include_lifecycle_foundation_validator", any("lifecycle_validation_foundation" in c.get("path","") for c in contracts), {"contract_count": len(contracts)})
    if not any("lifecycle_validation_foundation" in c.get("path","") for c in contracts):
        errors.append("lifecycle foundation validator invoke contract missing")

    p = subprocess.run([sys.executable, str(repo / AUDIT), "--repo-root", str(repo)], cwd=str(repo), capture_output=True, text=True, timeout=300)
    add(checks, "custodes_audit_tool_runs", p.returncode == 0, {"exit_code": p.returncode, "stderr_tail": p.stderr[-2000:], "stdout_tail": p.stdout[-2000:]})
    if p.returncode != 0:
        errors.append("Custodes audit tool failed")

    audit, audit_err = load_json(repo / "ORGANS/CUSTODES/REPORTS/CUSTODES_ASTRONOMICON_PROSECUTOR_AUDIT_SUMMARY_V0_1.json")
    add(checks, "custodes_audit_summary_parses", audit_err is None, {"error": audit_err})
    if audit_err:
        errors.append("Custodes audit summary parse failed")
        audit = {}

    add(checks, "custodes_audit_verdict_pass", isinstance(audit, dict) and str(audit.get("verdict","")).startswith("PASS"), {"verdict": audit.get("verdict") if isinstance(audit, dict) else None})
    if not isinstance(audit, dict) or not str(audit.get("verdict","")).startswith("PASS"):
        errors.append("Custodes audit verdict is not PASS")

    validators = audit.get("validators_tested", []) if isinstance(audit, dict) else []
    failed = [v for v in validators if v.get("status") != "PASS"]
    add(checks, "all_astronomicon_validators_pass_under_custodes", not failed and len(validators) >= 7, {"failed": failed, "validator_count": len(validators)})
    if failed or len(validators) < 7:
        errors.append("some Astronomicon validators failed under Custodes")

    add(checks, "custodes_indictments_absent", not audit.get("indictments") if isinstance(audit, dict) else False, {"indictments": audit.get("indictments") if isinstance(audit, dict) else None})
    if isinstance(audit, dict) and audit.get("indictments"):
        errors.append("Custodes indictments exist")

    add(checks, "throne_confirmation_score_remains_zero", isinstance(audit, dict) and audit.get("throne_confirmation_score") == 0.0, {"score": audit.get("throne_confirmation_score") if isinstance(audit, dict) else None})
    if not isinstance(audit, dict) or audit.get("throne_confirmation_score") != 0.0:
        errors.append("Throne confirmation score must remain zero")

    score = audit.get("custodes_validation_score") if isinstance(audit, dict) else None
    verdict = "PASS_CUSTODES_ASTRONOMICON_VALIDATION_READY" if not errors and isinstance(score, (int,float)) and score >= 85 else "FAIL_CUSTODES_ASTRONOMICON_VALIDATION"
    generated = utc()
    summary = {
        "summary_id": "custodes.astronomicon_validation_summary.v0_2",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "custodes_validation_score": score,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "audit_summary": "ORGANS/CUSTODES/REPORTS/CUSTODES_ASTRONOMICON_PROSECUTOR_AUDIT_SUMMARY_V0_1.json",
        "not_claimed": ["Throne verdict", "organ assembled"]
    }
    receipt = {
        "receipt_id": "receipt.custodes.astronomicon_validation.v0_2",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Custodes Astronomicon validation fixed for validator invocation contracts."
    }

    for rel in [SUMMARY, RECEIPT, REPORT]:
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / SUMMARY).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    (repo / REPORT).write_text(f"""# CUSTODES ASTRONOMICON VALIDATION REPORT V0.2

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`  
custodes_validation_score: `{score}`

## Meaning

Custodes now prosecutes Astronomicon validators through explicit/adaptive invocation contracts.

This fixes false indictment caused by calling a validator with the wrong CLI shape.

## Checks

{checks_md}

## Errors

{errors_md}

## Not claimed

- Throne verdict
- organ assembled
""", encoding="utf-8")

    print(json.dumps({
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "custodes_validation_score": score,
        "receipt": RECEIPT.as_posix(),
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
