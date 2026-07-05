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
VALIDATOR_ID = "mechanicus_task_tool_composition_planner_validator.v0_1"

LAW = Path("ORGANS/MECHANICUS/LAWS/MECHANICUS_TASK_TOOL_COMPOSITION_PLANNER_LAW_V0_1.json")
TAXONOMY = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_TASK_CAPABILITY_DEMAND_TAXONOMY_V0_1.json")
SCORING = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_TOOL_COMPOSITION_SCORING_MATRIX_V0_1.json")
CUSTODES = Path("ORGANS/CUSTODES/MATRICES/CUSTODES_MECHANICUS_TOOL_COMPOSITION_PROSECUTOR_MATRIX_V0_1.json")
THRONE = Path("ORGANS/THRONE/MATRICES/THRONE_MECHANICUS_TOOL_COMPOSITION_CROWN_GATE_MATRIX_V0_1.json")
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
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def has_all(text: str, needles: List[str]) -> bool:
    return all(n in text for n in needles)

def run_plan(repo: Path, task_text: str):
    p = subprocess.run(
        [sys.executable, str(repo / PLANNER), "--repo-root", str(repo), "--task-text", task_text, "--out", PLAN.as_posix()],
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

    for name, path, needles in [
        ("tool_composition_law", LAW, ["Mechanicus must mathematically evaluate tool combinations", "Tool composition plans do not execute the task"]),
        ("capability_demand_taxonomy", TAXONOMY, ["tauri_app_or_cockpit", "game_engine_or_procedural_world", "external_repo_product_work"]),
        ("tool_composition_scoring_matrix", SCORING, ["score_total", "requirement_fit", "missing_capability_rules"]),
        ("custodes_tool_composition_matrix", CUSTODES, ["prosecutor_not_helper", "unscored_tool_choice", "planner_claimed_execution"]),
        ("throne_tool_composition_matrix", THRONE, ["A tool composition plan cannot become execution proof", "skip tool admission gate"]),
    ]:
        data, err = load_json(repo / path) if (repo / path).is_file() else ({}, "missing")
        text = json.dumps(data, ensure_ascii=False) if isinstance(data, dict) else ""
        ok = err is None and has_all(text, needles)
        add(checks, f"{name}_exists_and_declares_required_boundaries", ok, {"path": path.as_posix(), "error": err})
        if not ok:
            errors.append(f"{name} missing or incomplete")

    scoring, scoring_err = load_json(repo / SCORING) if (repo / SCORING).is_file() else ({}, "missing")
    dims = scoring.get("dimensions", []) if isinstance(scoring, dict) else []
    weight_sum = sum(int(d.get("weight", 0)) for d in dims if isinstance(d, dict))
    add(checks, "tool_composition_scoring_weights_sum_to_100", scoring_err is None and weight_sum == 100, {"weight_sum": weight_sum, "error": scoring_err})
    if scoring_err is not None or weight_sum != 100:
        errors.append("tool composition scoring weights do not sum to 100")

    planner_exists = (repo / PLANNER).is_file()
    add(checks, "tool_composition_planner_exists", planner_exists, {"path": PLANNER.as_posix()})
    if not planner_exists:
        errors.append("tool composition planner missing")

    plan_data = {}
    if not errors:
        sample_task = (
            "Register a Patch Pack for Tauri UI cockpit polish with CSS ornament animation, "
            "runtime FPS proof, JSON receipts, PowerShell WARP runner, and possible future game engine projection."
        )
        r = run_plan(repo, sample_task)
        add(checks, "tool_composition_planner_runs_and_writes_plan", r["exit_code"] == 0 and r["out_exists"], r)
        if r["exit_code"] != 0 or not r["out_exists"]:
            errors.append("tool composition planner did not run/write plan")
        else:
            plan_data, plan_err = load_json(repo / PLAN)
            plan_text = json.dumps(plan_data, ensure_ascii=False) if isinstance(plan_data, dict) else ""
            plan_ok = (
                plan_err is None
                and bool(plan_data.get("task_demand_classification"))
                and bool(plan_data.get("candidate_combinations_with_scores"))
                and "missing_capabilities" in plan_data
                and "task executed" in plan_text
                and plan_data.get("verdict") != "TASK_EXECUTED"
            )
            add(checks, "composition_plan_contains_scores_stack_validators_missing_and_no_execution_claim", plan_ok, {
                "error": plan_err,
                "verdict": plan_data.get("verdict") if isinstance(plan_data, dict) else None,
                "classified": [x.get("demand_id") for x in plan_data.get("task_demand_classification", [])] if isinstance(plan_data, dict) else [],
                "missing_count": len(plan_data.get("missing_capabilities", [])) if isinstance(plan_data, dict) else None
            })
            if not plan_ok:
                errors.append("composition plan incomplete or risks execution claim")

    if isinstance(plan_data, dict):
        missing = plan_data.get("missing_capabilities", [])
        if missing:
            warnings.append(f"Planner exposed missing/capability gaps: {len(missing)}")
            for m in missing[:6]:
                warnings.append(f"Capability gap: {m.get('capability_id')} => {m.get('severity')}")
        rec = plan_data.get("recommended_tool_stack") or {}
        if rec:
            warnings.append(f"Recommended primary demand: {rec.get('demand_id')} score={rec.get('score_0_to_100')} verdict={rec.get('verdict')}")

    verdict = "PASS_MECHANICUS_TASK_TOOL_COMPOSITION_PLANNER_READY" if not errors else "FAIL_MECHANICUS_TASK_TOOL_COMPOSITION_PLANNER"
    generated = utc()
    summary = {
        "summary_id": "mechanicus.task_tool_composition_planner_summary.v0_1",
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
        "receipt_id": "receipt.mechanicus.task_tool_composition_planner.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "law": LAW.as_posix(),
        "taxonomy": TAXONOMY.as_posix(),
        "scoring_matrix": SCORING.as_posix(),
        "plan": PLAN.as_posix()
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    rec = plan_data.get("recommended_tool_stack", {}) if isinstance(plan_data, dict) else {}
    rec_md = f"- demand: `{rec.get('demand_id')}`\n- score: `{rec.get('score_0_to_100')}`\n- verdict: `{rec.get('verdict')}`" if rec else "- none"

    (repo / REPORT).write_text(f"""# MECHANICUS TASK TOOL COMPOSITION PLANNER REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

Mechanicus can now inspect a Patch Pack / Task Pack demand and produce an advisory tool composition plan:

- required language lanes;
- recommended tools;
- required validators;
- scored candidate combinations;
- missing capabilities;
- Owner-visible blockers.

## Recommended sample stack

{rec_md}

## Boundary

```text
This is planning, not execution.
This does not install tools.
This does not claim runtime proof.
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
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
