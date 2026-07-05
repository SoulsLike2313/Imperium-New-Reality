#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse, datetime as dt, json, subprocess, sys
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "MECHANICUS-STRICT-BUILD-LANE-VALIDATOR-FALSE-NEGATIVE-HOTFIX-0001"
VALIDATOR_ID = "mechanicus_strict_build_lane_validator_false_negative_hotfix_validator.v0_1"

BASE_VALIDATOR = Path("ORGANS/MECHANICUS/VALIDATORS/validate_mechanicus_strict_build_lane_foundation.py")
BASE_RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_strict_build_lane_foundation_receipt.json")
BUILD_REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_BUILD_LANE_REPORT_V0_1.json")
PLAN = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TASK_TOOL_COMPOSITION_PLAN_V0_1.json")
RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_strict_build_lane_validator_false_negative_hotfix_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_BUILD_LANE_VALIDATOR_FALSE_NEGATIVE_HOTFIX_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_BUILD_LANE_VALIDATOR_FALSE_NEGATIVE_HOTFIX_REPORT_V0_1.md")

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

    text = (repo / BASE_VALIDATOR).read_text(encoding="utf-8", errors="replace") if (repo / BASE_VALIDATOR).is_file() else ""
    installed = "mechanicus_strict_build_lane_foundation_validator.v0_2_report_primary_false_negative_guard" in text
    add(checks, "strict_build_foundation_validator_v0_2_installed", installed, {"path": BASE_VALIDATOR.as_posix()})
    if not installed:
        errors.append("strict build foundation validator v0.2 not installed")

    if not errors:
        p = subprocess.run(
            [sys.executable, str(repo / BASE_VALIDATOR), "--repo-root", str(repo), "--apply"],
            cwd=str(repo),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=1600
        )
        base_pass = p.returncode == 0 and "PASS_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION_READY" in p.stdout
        add(checks, "base_strict_build_foundation_validator_passes_after_hotfix", base_pass, {
            "exit_code": p.returncode,
            "stdout_tail": p.stdout[-8000:],
            "stderr_tail": p.stderr[-5000:]
        })
        if not base_pass:
            errors.append("base strict build foundation validator still does not pass after hotfix")

    base_receipt, receipt_err = load_json(repo / BASE_RECEIPT) if (repo / BASE_RECEIPT).is_file() else ({}, "missing")
    receipt_pass = receipt_err is None and isinstance(base_receipt, dict) and base_receipt.get("verdict") == "PASS_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION_READY"
    add(checks, "base_strict_build_receipt_is_pass_after_hotfix", receipt_pass, {
        "error": receipt_err,
        "verdict": base_receipt.get("verdict") if isinstance(base_receipt, dict) else None
    })
    if not receipt_pass and not errors:
        errors.append("base strict build receipt is not PASS after hotfix")

    build, build_err = load_json(repo / BUILD_REPORT) if (repo / BUILD_REPORT).is_file() else ({}, "missing")
    report_pass = build_err is None and isinstance(build, dict) and build.get("verdict") == "PASS_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION" and int(build.get("blocking_failure_count", -1)) == 0
    add(checks, "build_report_passes_with_zero_blocking_failures", report_pass, {
        "error": build_err,
        "verdict": build.get("verdict") if isinstance(build, dict) else None,
        "blocking_failure_count": build.get("blocking_failure_count") if isinstance(build, dict) else None
    })
    if not report_pass and not errors:
        errors.append("build report not PASS after hotfix")

    plan, plan_err = load_json(repo / PLAN) if (repo / PLAN).is_file() else ({}, "missing")
    missing = [m.get("capability_id") for m in plan.get("missing_capabilities", [])] if isinstance(plan, dict) else []
    strict_gap_gone = plan_err is None and "STRICT_BUILD_LANE_REQUIRED" not in missing
    add(checks, "planner_strict_build_gap_removed_after_hotfix", strict_gap_gone, {
        "error": plan_err,
        "missing_capabilities": missing,
        "verdict": plan.get("verdict") if isinstance(plan, dict) else None
    })
    if not strict_gap_gone and not errors:
        errors.append("planner still reports strict build lane required after hotfix")

    if isinstance(base_receipt, dict):
        for w in base_receipt.get("warnings", []) or []:
            if w not in warnings:
                warnings.append(w)

    verdict = "PASS_MECHANICUS_STRICT_BUILD_LANE_VALIDATOR_FALSE_NEGATIVE_HOTFIX_READY" if not errors else "FAIL_MECHANICUS_STRICT_BUILD_LANE_VALIDATOR_FALSE_NEGATIVE_HOTFIX"
    generated = utc()
    summary = {
        "summary_id": "mechanicus.strict_build_lane_validator_false_negative_hotfix_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "base_receipt": BASE_RECEIPT.as_posix(),
        "build_report": BUILD_REPORT.as_posix(),
        "plan": PLAN.as_posix()
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.strict_build_lane_validator_false_negative_hotfix.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "base_receipt": BASE_RECEIPT.as_posix(),
        "build_report": BUILD_REPORT.as_posix(),
        "plan": PLAN.as_posix()
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# MECHANICUS STRICT BUILD LANE VALIDATOR FALSE NEGATIVE HOTFIX REPORT

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Diagnosis

The build report showed all discovered targets passed, but the foundation validator returned FAIL.

## Fix

Installed validator v0.2 with report-primary false-negative guard.

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
        "base_receipt": BASE_RECEIPT.as_posix(),
        "build_report": BUILD_REPORT.as_posix(),
        "plan": PLAN.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2, default=str))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
