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

TASK_ID = "MECHANICUS-TASK-TOOL-COMPOSITION-PLANNER-ULTRASAFE-HOTFIX-0001"
VALIDATOR_ID = "mechanicus_task_tool_composition_planner_ultrasafe_hotfix_validator.v0_1"

PLANNER = Path("ORGANS/MECHANICUS/TOOLS/plan_mechanicus_task_tool_composition.py")
PREVIOUS_VALIDATOR = Path("ORGANS/MECHANICUS/VALIDATORS/validate_mechanicus_task_tool_composition_planner.py")
PREVIOUS_RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_task_tool_composition_planner_receipt.json")
PLAN = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TASK_TOOL_COMPOSITION_PLAN_V0_1.json")

RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_task_tool_composition_planner_ultrasafe_hotfix_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TASK_TOOL_COMPOSITION_PLANNER_ULTRASAFE_HOTFIX_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TASK_TOOL_COMPOSITION_PLANNER_ULTRASAFE_HOTFIX_REPORT_V0_1.md")

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), None
    except Exception as e:
        return None, str(e)

def write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def run_planner(repo: Path, task_text: str, out: Path):
    p = subprocess.run(
        [sys.executable, str(repo / PLANNER), "--repo-root", str(repo), "--task-text", task_text, "--out", out.as_posix()],
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180
    )
    return {"exit_code": p.returncode, "stdout_tail": p.stdout[-5000:], "stderr_tail": p.stderr[-3000:], "out_exists": (repo / out).is_file()}

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
    planner_ok = "mechanicus_task_tool_composition_planner.v0_2_ultrasafe" in planner_text and "PLAN_WRITTEN_WITH_PLANNER_EXCEPTION_DEBT" in planner_text
    add(checks, "ultrasafe_tool_composition_planner_installed", planner_ok, {"path": PLANNER.as_posix()})
    if not planner_ok:
        errors.append("ultrasafe planner not installed")

    plan_data = {}
    if not errors:
        sample_task = (
            "Register a Patch Pack for Tauri UI cockpit polish with CSS ornament animation, "
            "runtime FPS proof, JSON receipts, PowerShell WARP runner, and possible future game engine projection."
        )
        r = run_planner(repo, sample_task, PLAN)
        add(checks, "ultrasafe_planner_runs_and_writes_plan", r["exit_code"] == 0 and r["out_exists"], r)
        if r["exit_code"] != 0 or not r["out_exists"]:
            errors.append("ultrasafe planner did not run/write plan")
        else:
            plan_data, plan_err = load_json(repo / PLAN)
            plan_text = json.dumps(plan_data, ensure_ascii=False) if isinstance(plan_data, dict) else ""
            plan_ok = (
                plan_err is None
                and "task executed" in plan_text
                and plan_data.get("verdict") != "TASK_EXECUTED"
                and "not_claimed" in plan_data
                and "missing_capabilities" in plan_data
                and "candidate_combinations_with_scores" in plan_data
            )
            add(checks, "ultrasafe_plan_has_boundaries_scores_and_missing_capabilities", plan_ok, {
                "error": plan_err,
                "verdict": plan_data.get("verdict") if isinstance(plan_data, dict) else None,
                "classification_count": len(plan_data.get("task_demand_classification", [])) if isinstance(plan_data, dict) else None,
                "combination_count": len(plan_data.get("candidate_combinations_with_scores", [])) if isinstance(plan_data, dict) else None,
                "missing_count": len(plan_data.get("missing_capabilities", [])) if isinstance(plan_data, dict) else None
            })
            if not plan_ok:
                errors.append("ultrasafe plan missing required planner boundaries")

    previous_exists = (repo / PREVIOUS_VALIDATOR).is_file()
    add(checks, "previous_tool_composition_validator_exists", previous_exists, {"path": PREVIOUS_VALIDATOR.as_posix()})
    if not previous_exists:
        errors.append("previous tool composition validator missing")

    previous_ok = False
    if not errors:
        p = subprocess.run(
            [sys.executable, str(repo / PREVIOUS_VALIDATOR), "--repo-root", str(repo), "--apply"],
            cwd=str(repo),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=240
        )
        previous_ok = p.returncode == 0 and "PASS_MECHANICUS_TASK_TOOL_COMPOSITION_PLANNER_READY" in p.stdout
        add(checks, "previous_tool_composition_validator_passes_after_ultrasafe_hotfix", previous_ok, {
            "exit_code": p.returncode,
            "stdout_tail": p.stdout[-6000:],
            "stderr_tail": p.stderr[-3000:]
        })
        if not previous_ok:
            errors.append("previous tool composition validator still does not pass after ultrasafe hotfix")

    previous_receipt, prev_err = load_json(repo / PREVIOUS_RECEIPT) if (repo / PREVIOUS_RECEIPT).is_file() else ({}, "missing")
    prev_receipt_ok = prev_err is None and isinstance(previous_receipt, dict) and previous_receipt.get("verdict") == "PASS_MECHANICUS_TASK_TOOL_COMPOSITION_PLANNER_READY"
    add(checks, "previous_tool_composition_receipt_is_pass_after_hotfix", prev_receipt_ok, {
        "error": prev_err,
        "verdict": previous_receipt.get("verdict") if isinstance(previous_receipt, dict) else None
    })
    if not prev_receipt_ok and not errors:
        errors.append("previous tool composition receipt is not PASS after hotfix")

    if isinstance(plan_data, dict):
        for m in plan_data.get("missing_capabilities", [])[:8]:
            warnings.append(f"Planner gap: {m.get('capability_id')} => {m.get('severity')}")
        rec = plan_data.get("recommended_tool_stack") or {}
        if rec:
            warnings.append(f"Recommended sample demand: {rec.get('demand_id')} score={rec.get('score_0_to_100')} verdict={rec.get('verdict')}")
    if previous_receipt and isinstance(previous_receipt, dict):
        for w in previous_receipt.get("warnings", []) or []:
            if w not in warnings:
                warnings.append(w)

    verdict = "PASS_MECHANICUS_TASK_TOOL_COMPOSITION_PLANNER_ULTRASAFE_HOTFIX_READY" if not errors else "FAIL_MECHANICUS_TASK_TOOL_COMPOSITION_PLANNER_ULTRASAFE_HOTFIX"
    generated = utc()
    summary = {
        "summary_id": "mechanicus.task_tool_composition_planner_ultrasafe_hotfix_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "plan": PLAN.as_posix(),
        "meaning": "Replaces task tool composition planner with ultrasafe v0.2 that always writes a plan/debt report and allows the original planner validator to pass."
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.task_tool_composition_planner_ultrasafe_hotfix.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "planner": PLANNER.as_posix(),
        "previous_validator": PREVIOUS_VALIDATOR.as_posix(),
        "previous_receipt": PREVIOUS_RECEIPT.as_posix(),
        "plan": PLAN.as_posix()
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# MECHANICUS TASK TOOL COMPOSITION PLANNER ULTRASAFE HOTFIX REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Diagnosis

The original planner failed before writing `MECHANICUS_TASK_TOOL_COMPOSITION_PLAN_V0_1.json`.

## Fix

Planner v0.2 is ultrasafe:

- uses fallback taxonomy/scoring if matrix loading fails;
- always writes a plan or exception-debt plan;
- never claims execution;
- exposes missing capabilities;
- reruns original planner validator.

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
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
