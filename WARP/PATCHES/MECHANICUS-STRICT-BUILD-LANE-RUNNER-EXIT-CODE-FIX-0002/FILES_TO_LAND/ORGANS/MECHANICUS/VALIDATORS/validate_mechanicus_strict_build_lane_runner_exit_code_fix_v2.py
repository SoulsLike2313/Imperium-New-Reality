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

TASK_ID = "MECHANICUS-STRICT-BUILD-LANE-RUNNER-EXIT-CODE-FIX-0002"
VALIDATOR_ID = "mechanicus_strict_build_lane_runner_exit_code_fix_validator.v0_2_full_replacement"

RUNNER = Path("ORGANS/MECHANICUS/TOOLS/run_mechanicus_strict_build_lane.py")
BASE_VALIDATOR = Path("ORGANS/MECHANICUS/VALIDATORS/validate_mechanicus_strict_build_lane_foundation.py")
BASE_RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_strict_build_lane_foundation_receipt.json")
BUILD_REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_BUILD_LANE_REPORT_V0_1.json")
PLAN = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TASK_TOOL_COMPOSITION_PLAN_V0_1.json")

RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_strict_build_lane_runner_exit_code_fix_v2_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_BUILD_LANE_RUNNER_EXIT_CODE_FIX_V2_SUMMARY_V0_1.json")
REPORT_MD = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_BUILD_LANE_RUNNER_EXIT_CODE_FIX_V2_REPORT_V0_1.md")

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

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    runner_text = (repo / RUNNER).read_text(encoding="utf-8", errors="replace") if (repo / RUNNER).is_file() else ""
    markers_ok = (
        "mechanicus_strict_build_lane_foundation_runner.v0_2_exit_code_consistent" in runner_text
        and "mechanicus_strict_build_lane_foundation_runner.v0_1" in runner_text
        and "LEGACY_VALIDATOR_MARKER" in runner_text
        and "ensure_ascii=True" in runner_text
        and "configure_stdout()" in runner_text
        and "exit_code_contract" in runner_text
    )
    add(checks, "runner_v0_2_full_replacement_installed_with_legacy_marker", markers_ok, {"path": RUNNER.as_posix()})
    if not markers_ok:
        errors.append("runner v0.2 full replacement markers missing")

    build_report = {}
    if not errors:
        runner_run = run_py(repo, RUNNER, ["--repo-root", str(repo), "--out", BUILD_REPORT.as_posix()], timeout=1500)
        build_report, build_err = load_json(repo / BUILD_REPORT) if (repo / BUILD_REPORT).is_file() else ({}, "missing")
        report_pass = build_err is None and isinstance(build_report, dict) and build_report.get("verdict") == "PASS_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION" and int(build_report.get("blocking_failure_count", -1)) == 0
        exit_zero = runner_run.get("exit_code") == 0
        add(checks, "runner_exit_code_zero_when_report_passes", report_pass and exit_zero, {
            "runner_exit_code": runner_run.get("exit_code"),
            "report_verdict": build_report.get("verdict") if isinstance(build_report, dict) else None,
            "blocking_failure_count": build_report.get("blocking_failure_count") if isinstance(build_report, dict) else None,
            "stdout_tail": runner_run.get("stdout_tail"),
            "stderr_tail": runner_run.get("stderr_tail")
        })
        if not (report_pass and exit_zero):
            errors.append("runner still returns nonzero or report is not PASS")

    if not errors and isinstance(build_report, dict):
        targets_ok = all(bool(t.get("ok")) for t in build_report.get("targets", []) if isinstance(t, dict) and t.get("detected"))
        add(checks, "all_detected_build_targets_still_pass", targets_ok, {
            "targets": [
                {"target_id": t.get("target_id"), "lane": t.get("lane"), "detected": t.get("detected"), "ok": t.get("ok"), "dependency_state": t.get("dependency_state")}
                for t in build_report.get("targets", []) if isinstance(t, dict)
            ]
        })
        if not targets_ok:
            errors.append("detected build targets no longer all pass")

    base_receipt = {}
    if not errors:
        base_run = run_py(repo, BASE_VALIDATOR, ["--repo-root", str(repo), "--apply"], timeout=1500)
        base_receipt, receipt_err = load_json(repo / BASE_RECEIPT) if (repo / BASE_RECEIPT).is_file() else ({}, "missing")
        base_pass = base_run.get("exit_code") == 0 and receipt_err is None and isinstance(base_receipt, dict) and base_receipt.get("verdict") == "PASS_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION_READY"
        add(checks, "base_strict_build_validator_passes_after_runner_exit_fix", base_pass, {
            "base_exit_code": base_run.get("exit_code"),
            "receipt_error": receipt_err,
            "base_verdict": base_receipt.get("verdict") if isinstance(base_receipt, dict) else None,
            "base_runner_exit_code": base_receipt.get("runner_exit_code") if isinstance(base_receipt, dict) else None,
            "stdout_tail": base_run.get("stdout_tail"),
            "stderr_tail": base_run.get("stderr_tail")
        })
        if not base_pass:
            errors.append("base strict build validator did not pass after runner fix")

        base_warnings = [str(w) for w in base_receipt.get("warnings", [])] if isinstance(base_receipt, dict) else []
        false_warning_gone = not any(("false-negative guard" in w.lower() or "exit code 1 disagreed" in w.lower()) for w in base_warnings)
        add(checks, "false_negative_warning_removed", false_warning_gone, {"base_warnings": base_warnings})
        if not false_warning_gone:
            errors.append("false-negative warning still present")

    plan = {}
    if not errors:
        plan, plan_err = load_json(repo / PLAN) if (repo / PLAN).is_file() else ({}, "missing")
        missing = [m.get("capability_id") for m in plan.get("missing_capabilities", [])] if isinstance(plan, dict) else []
        strict_gap_gone = plan_err is None and "STRICT_BUILD_LANE_REQUIRED" not in missing
        add(checks, "planner_still_has_no_strict_build_required_gap", strict_gap_gone, {"missing_capabilities": missing, "plan_error": plan_err})
        if not strict_gap_gone:
            errors.append("planner strict build gap returned")

    if isinstance(build_report, dict):
        warnings.extend(build_report.get("warnings", [])[:5])
    if isinstance(base_receipt, dict):
        for w in base_receipt.get("warnings", []) or []:
            if w not in warnings:
                warnings.append(w)
    if isinstance(plan, dict):
        rec = plan.get("recommended_tool_stack")
        if isinstance(rec, dict):
            warnings.append(f"Planner recommended demand after runner fix v2: {rec.get('demand_id')} score={rec.get('score_0_to_100')} verdict={rec.get('verdict')}")
        for m in plan.get("missing_capabilities", [])[:6]:
            warnings.append(f"Remaining planner gap: {m.get('capability_id')} => {m.get('severity')}")

    verdict = "PASS_MECHANICUS_STRICT_BUILD_LANE_RUNNER_EXIT_CODE_FIX_V2_READY" if not errors else "FAIL_MECHANICUS_STRICT_BUILD_LANE_RUNNER_EXIT_CODE_FIX_V2"
    generated = utc()
    summary = {
        "summary_id": "mechanicus.strict_build_lane_runner_exit_code_fix_v2_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "build_report": BUILD_REPORT.as_posix(),
        "base_receipt": BASE_RECEIPT.as_posix(),
        "plan": PLAN.as_posix(),
        "meaning": "Strict build runner was fully replaced with v0.2 exit-code-consistent implementation."
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.strict_build_lane_runner_exit_code_fix_v2.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "build_report": BUILD_REPORT.as_posix(),
        "base_receipt": BASE_RECEIPT.as_posix(),
        "plan": PLAN.as_posix()
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT_MD).write_text(f"""# MECHANICUS STRICT BUILD LANE RUNNER EXIT CODE FIX V2 REPORT

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Fix

V1 attempted a fragile text patch. V2 replaces the runner file entirely.

The runner now follows this contract:

```text
PASS report + blocking_failure_count 0 => process exit 0
FAIL report or blocking failures      => process exit 1
```

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}
""", encoding="utf-8")

    print(json.dumps({"task_id": TASK_ID, "validator_id": VALIDATOR_ID, "verdict": verdict, "receipt": RECEIPT.as_posix(), "summary": SUMMARY.as_posix(), "errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2, default=str))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
