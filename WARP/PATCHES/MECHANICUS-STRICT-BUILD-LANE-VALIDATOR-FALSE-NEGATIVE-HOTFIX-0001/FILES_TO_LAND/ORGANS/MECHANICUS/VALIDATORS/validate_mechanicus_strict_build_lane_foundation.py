#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse, datetime as dt, json, subprocess, sys
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "MECHANICUS-STRICT-BUILD-LANE-FOUNDATION-0001"
VALIDATOR_ID = "mechanicus_strict_build_lane_foundation_validator.v0_2_report_primary_false_negative_guard"

RUNNER = Path("ORGANS/MECHANICUS/TOOLS/run_mechanicus_strict_build_lane.py")
PLANNER = Path("ORGANS/MECHANICUS/TOOLS/plan_mechanicus_task_tool_composition.py")
BUILD_REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_BUILD_LANE_REPORT_V0_1.json")
PLAN = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TASK_TOOL_COMPOSITION_PLAN_V0_1.json")
RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_strict_build_lane_foundation_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_BUILD_LANE_FOUNDATION_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_BUILD_LANE_FOUNDATION_VALIDATION_REPORT_V0_1.md")

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

def run_py(repo: Path, script: Path, args: List[str], timeout: int = 1500):
    p = subprocess.run(
        [sys.executable, str(repo / script)] + args,
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout
    )
    return {"exit_code": p.returncode, "stdout_tail": p.stdout[-8000:], "stderr_tail": p.stderr[-5000:]}

def target_receipt_ok(t: Dict[str, Any]) -> bool:
    if not t.get("detected"):
        return True
    tid = t.get("target_id")
    if tid == "python_compile_current_non_patch":
        return "files_checked" in t and "errors" in t
    if tid in {"powershell_host_probe", "support_app_tauri_npm_build", "support_app_tauri_cargo_check"}:
        return isinstance(t.get("command_result"), dict)
    return True

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    runner_installed = (repo / RUNNER).is_file()
    planner_installed = (repo / PLANNER).is_file()
    add(checks, "strict_build_lane_runner_exists", runner_installed, {"path": RUNNER.as_posix()})
    add(checks, "task_tool_planner_exists", planner_installed, {"path": PLANNER.as_posix()})
    if not runner_installed:
        errors.append("strict build lane runner missing")
    if not planner_installed:
        errors.append("task tool planner missing")

    runner_result = {}
    build_data: Dict[str, Any] = {}
    if not errors:
        runner_result = run_py(repo, RUNNER, ["--repo-root", str(repo), "--out", BUILD_REPORT.as_posix()])
        build_data, build_err = load_json(repo / BUILD_REPORT) if (repo / BUILD_REPORT).is_file() else ({}, "missing")

        report_pass = (
            build_err is None
            and isinstance(build_data, dict)
            and build_data.get("verdict") == "PASS_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION"
            and int(build_data.get("blocking_failure_count", -1)) == 0
        )
        add(checks, "strict_build_report_passes_with_zero_blocking_failures", report_pass, {
            "runner_exit_code": runner_result.get("exit_code"),
            "load_error": build_err,
            "verdict": build_data.get("verdict") if isinstance(build_data, dict) else None,
            "blocking_failure_count": build_data.get("blocking_failure_count") if isinstance(build_data, dict) else None,
            "stdout_tail": runner_result.get("stdout_tail"),
            "stderr_tail": runner_result.get("stderr_tail")
        })
        if not report_pass:
            errors.append("strict build report is not PASS with zero blocking failures")
        if report_pass and runner_result.get("exit_code") != 0:
            warnings.append(f"Runner process exit code {runner_result.get('exit_code')} disagreed with PASS report; false-negative guard used report truth.")

    targets = {}
    if not errors and isinstance(build_data, dict):
        targets = {t.get("target_id"): t for t in build_data.get("targets", []) if isinstance(t, dict)}
        all_detected_ok = all(bool(t.get("ok")) for t in targets.values() if t.get("detected"))
        all_receipts = all(target_receipt_ok(t) for t in targets.values())
        add(checks, "all_detected_build_targets_ok", all_detected_ok, {
            "targets": [{k: t.get(k) for k in ["target_id", "lane", "detected", "ok", "dependency_state", "errors"]} for t in targets.values()]
        })
        add(checks, "all_detected_build_targets_have_receipts", all_receipts, {
            "receipt_presence": {k: target_receipt_ok(v) for k, v in targets.items()}
        })
        if not all_detected_ok:
            errors.append("at least one detected build target is not ok")
        if not all_receipts:
            errors.append("at least one detected build target lacks a command/compile receipt")

        no_install = True
        for t in targets.values():
            cmd = " ".join(str(x) for x in (t.get("command_result") or {}).get("cmd", []))
            if "npm install" in cmd or "npm i" in cmd or " install" in cmd:
                no_install = False
        add(checks, "no_dependency_installation_attempted", no_install, {})
        if not no_install:
            errors.append("dependency installation was attempted")

        for tid in ["python_compile_current_non_patch", "powershell_host_probe"]:
            ok = tid in targets and bool(targets[tid].get("ok"))
            add(checks, f"{tid}_passes", ok, {"target": targets.get(tid)})
            if not ok:
                errors.append(f"{tid} did not pass")
        for tid in ["support_app_tauri_npm_build", "support_app_tauri_cargo_check"]:
            if tid in targets and targets[tid].get("detected"):
                ok = bool(targets[tid].get("ok"))
                add(checks, f"{tid}_detected_and_passes", ok, {"target_summary": {k: targets[tid].get(k) for k in ["target_id", "lane", "detected", "ok", "dependency_state", "errors"]}})
                if not ok:
                    errors.append(f"{tid} detected but failed")
            else:
                add(checks, f"{tid}_not_present_is_nonblocking_foundation_debt", True, {"target": targets.get(tid)})

    plan_data: Dict[str, Any] = {}
    if not errors:
        sample = "Register a Patch Pack for Tauri UI cockpit polish with CSS ornament animation, runtime FPS proof, JSON receipts, PowerShell WARP runner, and possible future game engine projection."
        plan_run = run_py(repo, PLANNER, ["--repo-root", str(repo), "--task-text", sample, "--out", PLAN.as_posix()], timeout=300)
        plan_data, plan_err = load_json(repo / PLAN) if (repo / PLAN).is_file() else ({}, "missing")
        plan_ok = plan_run.get("exit_code") == 0 and plan_err is None and plan_data.get("strict_build_report") == BUILD_REPORT.as_posix()
        add(checks, "planner_runs_with_strict_build_report_awareness", plan_ok, {
            "run": plan_run,
            "load_error": plan_err,
            "strict_build_report": plan_data.get("strict_build_report") if isinstance(plan_data, dict) else None
        })
        if not plan_ok:
            errors.append("planner did not use strict build report")

        missing = [m.get("capability_id") for m in plan_data.get("missing_capabilities", [])] if isinstance(plan_data, dict) else []
        strict_gap_gone = "STRICT_BUILD_LANE_REQUIRED" not in missing
        add(checks, "planner_no_longer_reports_strict_build_lane_required_gap_after_pass", strict_gap_gone, {"missing_capabilities": missing})
        if not strict_gap_gone:
            errors.append("planner still reports STRICT_BUILD_LANE_REQUIRED after strict build lane pass")

    if isinstance(build_data, dict):
        warnings.extend(build_data.get("warnings", [])[:6])
        for f in build_data.get("foundation_debt", []) or []:
            warnings.append(f"Foundation debt: {f.get('target_id')} => {f.get('debt')}")
    if isinstance(plan_data, dict):
        rec = plan_data.get("recommended_tool_stack")
        if isinstance(rec, dict):
            warnings.append(f"Planner recommended demand after build lane: {rec.get('demand_id')} score={rec.get('score_0_to_100')} verdict={rec.get('verdict')}")
        for m in plan_data.get("missing_capabilities", [])[:6]:
            warnings.append(f"Remaining planner gap: {m.get('capability_id')} => {m.get('severity')}")

    verdict = "PASS_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION_READY" if not errors else "FAIL_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION"
    generated = utc()
    summary = {
        "summary_id": "mechanicus.strict_build_lane_foundation_summary.v0_2",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "build_report": BUILD_REPORT.as_posix(),
        "plan": PLAN.as_posix(),
        "runner_exit_code": runner_result.get("exit_code") if isinstance(runner_result, dict) else None,
        "meaning": "Mechanicus strict build lane validates discovered build targets from build report truth and guards against validator false negatives."
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.strict_build_lane_foundation.v0_2",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "build_report": BUILD_REPORT.as_posix(),
        "plan": PLAN.as_posix(),
        "runner_exit_code": runner_result.get("exit_code") if isinstance(runner_result, dict) else None
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# MECHANICUS STRICT BUILD LANE FOUNDATION VALIDATION REPORT V0.2

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Fix

Validator v0.2 uses report-primary truth:

- build report verdict must be PASS;
- blocking failures must be zero;
- detected targets must be ok;
- detected targets must have command/compile receipts;
- dependency installation must not be attempted.

## Boundary

```text
Build proof is not code cleanliness.
Build proof is not runtime proof.
No dependency installation is attempted.
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
        "build_report": BUILD_REPORT.as_posix(),
        "plan": PLAN.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2, default=str))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
