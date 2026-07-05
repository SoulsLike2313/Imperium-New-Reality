#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "MECHANICUS-TASK-TOOL-COMPOSITION-PLANNER-ULTRASAFE-HOTFIX-0002"
VALIDATOR_ID = "mechanicus_task_tool_composition_planner_ultrasafe_hotfix_validator.v0_2"

PLANNER = Path("ORGANS/MECHANICUS/TOOLS/plan_mechanicus_task_tool_composition.py")
BASE_VALIDATOR = Path("ORGANS/MECHANICUS/VALIDATORS/validate_mechanicus_task_tool_composition_planner.py")
BASE_RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_task_tool_composition_planner_receipt.json")
PLAN = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TASK_TOOL_COMPOSITION_PLAN_V0_1.json")

RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_task_tool_composition_planner_ultrasafe_hotfix_v2_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TASK_TOOL_COMPOSITION_PLANNER_ULTRASAFE_HOTFIX_V2_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TASK_TOOL_COMPOSITION_PLANNER_ULTRASAFE_HOTFIX_V2_REPORT_V0_1.md")

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), None
    except Exception as e:
        return None, str(e)

def write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    planner_text = (repo / PLANNER).read_text(encoding="utf-8", errors="replace") if (repo / PLANNER).is_file() else ""
    planner_ok = "mechanicus_task_tool_composition_planner.v0_3_hard_safe" in planner_text
    add(checks, "hard_safe_planner_v0_3_installed", planner_ok, {"path": PLANNER.as_posix()})
    if not planner_ok:
        errors.append("hard-safe planner v0.3 not installed")

    validator_text = (repo / BASE_VALIDATOR).read_text(encoding="utf-8", errors="replace") if (repo / BASE_VALIDATOR).is_file() else ""
    validator_ok = "mechanicus_task_tool_composition_planner_validator.v0_2_hard_safe" in validator_text
    add(checks, "base_planner_validator_v0_2_installed", validator_ok, {"path": BASE_VALIDATOR.as_posix()})
    if not validator_ok:
        errors.append("base planner validator v0.2 not installed")

    base_result = {}
    if not errors:
        p = subprocess.run(
            [sys.executable, str(repo / BASE_VALIDATOR), "--repo-root", str(repo), "--apply"],
            cwd=str(repo),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=240
        )
        base_result = {"exit_code": p.returncode, "stdout_tail": p.stdout[-7000:], "stderr_tail": p.stderr[-4000:]}
        base_ok = p.returncode == 0 and "PASS_MECHANICUS_TASK_TOOL_COMPOSITION_PLANNER_READY" in p.stdout
        add(checks, "base_planner_validator_passes_after_v2_hotfix", base_ok, base_result)
        if not base_ok:
            errors.append("base planner validator still does not pass after v2 hotfix")

    base_receipt, receipt_err = load_json(repo / BASE_RECEIPT) if (repo / BASE_RECEIPT).is_file() else ({}, "missing")
    base_receipt_ok = receipt_err is None and isinstance(base_receipt, dict) and base_receipt.get("verdict") == "PASS_MECHANICUS_TASK_TOOL_COMPOSITION_PLANNER_READY"
    add(checks, "base_planner_receipt_is_pass_after_v2_hotfix", base_receipt_ok, {"error": receipt_err, "verdict": base_receipt.get("verdict") if isinstance(base_receipt, dict) else None})
    if not base_receipt_ok and not errors:
        errors.append("base planner receipt is not PASS after v2 hotfix")

    plan_data, plan_err = load_json(repo / PLAN) if (repo / PLAN).is_file() else ({}, "missing")
    plan_ok = (
        plan_err is None and isinstance(plan_data, dict)
        and len(plan_data.get("task_demand_classification", [])) > 0
        and len(plan_data.get("candidate_combinations_with_scores", [])) > 0
        and plan_data.get("verdict") not in {"TASK_EXECUTED", "PLAN_READY_WITH_PLANNER_EXCEPTION_DEBT", "PLAN_WRITTEN_WITH_PLANNER_EXCEPTION_DEBT"}
    )
    add(checks, "plan_is_real_composition_plan_not_exception_debt", plan_ok, {
        "error": plan_err,
        "verdict": plan_data.get("verdict") if isinstance(plan_data, dict) else None,
        "classification_count": len(plan_data.get("task_demand_classification", [])) if isinstance(plan_data, dict) else None,
        "combination_count": len(plan_data.get("candidate_combinations_with_scores", [])) if isinstance(plan_data, dict) else None
    })
    if not plan_ok and not errors:
        errors.append("plan is not a real composition plan")

    if isinstance(plan_data, dict):
        for m in plan_data.get("missing_capabilities", [])[:8]:
            warnings.append(f"Planner gap: {m.get('capability_id')} => {m.get('severity')}")
        rec = plan_data.get("recommended_tool_stack")
        if isinstance(rec, dict):
            warnings.append(f"Recommended demand: {rec.get('demand_id')} score={rec.get('score_0_to_100')} verdict={rec.get('verdict')}")
    if isinstance(base_receipt, dict):
        for w in base_receipt.get("warnings", []) or []:
            if w not in warnings:
                warnings.append(w)

    verdict = "PASS_MECHANICUS_TASK_TOOL_COMPOSITION_PLANNER_ULTRASAFE_HOTFIX_V2_READY" if not errors else "FAIL_MECHANICUS_TASK_TOOL_COMPOSITION_PLANNER_ULTRASAFE_HOTFIX_V2"
    generated = utc()
    summary = {
        "summary_id": "mechanicus.task_tool_composition_planner_ultrasafe_hotfix_v2_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "plan": PLAN.as_posix(),
        "meaning": "Installs hard-safe planner v0.3 and base validator v0.2 so the planner produces a real composition plan instead of exception debt."
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.task_tool_composition_planner_ultrasafe_hotfix_v2.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "planner": PLANNER.as_posix(),
        "base_validator": BASE_VALIDATOR.as_posix(),
        "base_receipt": BASE_RECEIPT.as_posix(),
        "plan": PLAN.as_posix()
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# MECHANICUS TASK TOOL COMPOSITION PLANNER ULTRASAFE HOTFIX V2 REPORT

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Fix

v2 no longer asks the old brittle validator to bless an exception-debt plan.

It replaces:

- planner with v0.3 hard-safe;
- base planner validator with v0.2 hard-safe-aware.

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
        "receipt": RECEIPT.as_posix(),
        "summary": SUMMARY.as_posix(),
        "plan": PLAN.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2, default=str))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
