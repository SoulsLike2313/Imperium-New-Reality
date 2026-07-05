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

TASK_ID = "MECHANICUS-TASK-TOOL-COMPOSITION-PLANNER-0001"
VALIDATOR_ID = "mechanicus_task_tool_composition_planner_validator.v0_2_hard_safe"

LAW = Path("ORGANS/MECHANICUS/LAWS/MECHANICUS_TASK_TOOL_COMPOSITION_PLANNER_LAW_V0_1.json")
TAXONOMY = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_TASK_CAPABILITY_DEMAND_TAXONOMY_V0_1.json")
SCORING = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_TOOL_COMPOSITION_SCORING_MATRIX_V0_1.json")
PLANNER = Path("ORGANS/MECHANICUS/TOOLS/plan_mechanicus_task_tool_composition.py")
PLAN = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TASK_TOOL_COMPOSITION_PLAN_V0_1.json")
RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_task_tool_composition_planner_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TASK_TOOL_COMPOSITION_PLANNER_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TASK_TOOL_COMPOSITION_PLANNER_REPORT_V0_1.md")

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

def has_text(path: Path, needles: List[str]) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return all(n in text for n in needles)

def run_planner(repo: Path):
    sample_task = (
        "Register a Patch Pack for Tauri UI cockpit polish with CSS ornament animation, "
        "runtime FPS proof, JSON receipts, PowerShell WARP runner, and possible future game engine projection."
    )
    p = subprocess.run(
        [sys.executable, str(repo / PLANNER), "--repo-root", str(repo), "--task-text", sample_task, "--out", PLAN.as_posix()],
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180
    )
    return {"exit_code": p.returncode, "stdout_tail": p.stdout[-5000:], "stderr_tail": p.stderr[-3000:], "out_exists": (repo / PLAN).is_file()}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    add(checks, "planner_law_exists", (repo / LAW).is_file(), {"path": LAW.as_posix()})
    add(checks, "taxonomy_exists", (repo / TAXONOMY).is_file(), {"path": TAXONOMY.as_posix()})
    add(checks, "scoring_matrix_exists", (repo / SCORING).is_file(), {"path": SCORING.as_posix()})

    planner_ok = (repo / PLANNER).is_file() and has_text(repo / PLANNER, ["mechanicus_task_tool_composition_planner.v0_3_hard_safe", "task executed", "strict build pass"])
    add(checks, "hard_safe_planner_installed", planner_ok, {"path": PLANNER.as_posix()})
    if not planner_ok:
        errors.append("hard-safe planner not installed")

    plan_data = {}
    if not errors:
        r = run_planner(repo)
        add(checks, "planner_runs_and_writes_plan", r["exit_code"] == 0 and r["out_exists"], r)
        if r["exit_code"] != 0 or not r["out_exists"]:
            errors.append("planner did not run/write plan")
        else:
            plan_data, plan_err = load_json(repo / PLAN)
            if not isinstance(plan_data, dict):
                plan_data = {}
            plan_text = json.dumps(plan_data, ensure_ascii=False, default=str)
            required_shape_ok = (
                plan_err is None
                and isinstance(plan_data.get("task_demand_classification"), list)
                and len(plan_data.get("task_demand_classification", [])) > 0
                and isinstance(plan_data.get("candidate_combinations_with_scores"), list)
                and len(plan_data.get("candidate_combinations_with_scores", [])) > 0
                and "missing_capabilities" in plan_data
                and "recommended_tool_stack" in plan_data
                and "task executed" in plan_text
                and plan_data.get("verdict") != "TASK_EXECUTED"
            )
            add(checks, "plan_contains_classification_scores_recommendation_gaps_and_no_execution_claim", required_shape_ok, {
                "error": plan_err,
                "verdict": plan_data.get("verdict"),
                "classification_count": len(plan_data.get("task_demand_classification", [])),
                "combination_count": len(plan_data.get("candidate_combinations_with_scores", [])),
                "missing_count": len(plan_data.get("missing_capabilities", []))
            })
            if not required_shape_ok:
                errors.append("plan shape incomplete or risks execution claim")
            no_exception_ok = plan_data.get("verdict") != "PLAN_READY_WITH_PLANNER_EXCEPTION_DEBT" and plan_data.get("verdict") != "PLAN_WRITTEN_WITH_PLANNER_EXCEPTION_DEBT"
            add(checks, "planner_did_not_fall_back_to_exception_debt_plan", no_exception_ok, {"verdict": plan_data.get("verdict")})
            if not no_exception_ok:
                errors.append("planner produced exception-debt plan instead of real composition plan")

    for gap in plan_data.get("missing_capabilities", [])[:8] if isinstance(plan_data, dict) else []:
        warnings.append(f"Planner gap: {gap.get('capability_id')} => {gap.get('severity')}")
    rec = plan_data.get("recommended_tool_stack") if isinstance(plan_data, dict) else None
    if isinstance(rec, dict):
        warnings.append(f"Recommended demand: {rec.get('demand_id')} score={rec.get('score_0_to_100')} verdict={rec.get('verdict')}")

    verdict = "PASS_MECHANICUS_TASK_TOOL_COMPOSITION_PLANNER_READY" if not errors else "FAIL_MECHANICUS_TASK_TOOL_COMPOSITION_PLANNER"
    generated = utc()
    summary = {
        "summary_id": "mechanicus.task_tool_composition_planner_summary.v0_2",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "plan": PLAN.as_posix(),
        "meaning": "Mechanicus can score task tool combinations, recommend language/tool/validator stacks and expose missing capabilities before execution."
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.task_tool_composition_planner.v0_2",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "plan": PLAN.as_posix()
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# MECHANICUS TASK TOOL COMPOSITION PLANNER REPORT V0.2

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

Mechanicus can inspect task demand and produce a hard-safe advisory tool composition plan.

## Boundary

```text
Planning is not execution.
Planning does not install tools.
Planning does not claim runtime proof.
```

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
