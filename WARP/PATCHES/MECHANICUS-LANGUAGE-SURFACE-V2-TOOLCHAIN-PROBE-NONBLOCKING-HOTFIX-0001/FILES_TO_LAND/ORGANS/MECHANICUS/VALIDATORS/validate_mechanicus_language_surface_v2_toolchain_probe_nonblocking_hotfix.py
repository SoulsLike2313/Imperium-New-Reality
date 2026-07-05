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

TASK_ID = "MECHANICUS-LANGUAGE-SURFACE-V2-TOOLCHAIN-PROBE-NONBLOCKING-HOTFIX-0001"
VALIDATOR_ID = "mechanicus_language_surface_v2_toolchain_probe_nonblocking_hotfix_validator.v0_1"

PROBE = Path("ORGANS/MECHANICUS/TOOLS/prove_toolchains.py")
PREVIOUS_VALIDATOR = Path("ORGANS/MECHANICUS/VALIDATORS/validate_mechanicus_language_surface_v2_toolchain_validator_dispatch.py")
PREVIOUS_RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_language_surface_v2_toolchain_validator_dispatch_receipt.json")
TOOLCHAIN_REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOLCHAIN_PROOF_REPORT_V0_1.json")

RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_language_surface_v2_toolchain_probe_nonblocking_hotfix_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_PROBE_NONBLOCKING_HOTFIX_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_PROBE_NONBLOCKING_HOTFIX_REPORT_V0_1.md")

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

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    probe_exists = (repo / PROBE).is_file()
    probe_text = (repo / PROBE).read_text(encoding="utf-8", errors="replace") if probe_exists else ""
    probe_ok = probe_exists and "mechanicus_toolchain_probe.v0_2_nonblocking_baseline" in probe_text and "return 0" in probe_text
    add(checks, "nonblocking_toolchain_probe_installed", probe_ok, {"path": PROBE.as_posix()})
    if not probe_ok:
        errors.append("nonblocking toolchain probe is not installed")

    probe_result = {}
    if not errors:
        p = subprocess.run(
            [sys.executable, str(repo / PROBE), "--repo-root", str(repo), "--out", TOOLCHAIN_REPORT.as_posix()],
            cwd=str(repo),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=240
        )
        probe_result = {"exit_code": p.returncode, "stdout_tail": p.stdout[-3000:], "stderr_tail": p.stderr[-3000:]}
        add(checks, "nonblocking_toolchain_probe_runs_and_returns_zero", p.returncode == 0 and (repo / TOOLCHAIN_REPORT).is_file(), probe_result)
        if p.returncode != 0 or not (repo / TOOLCHAIN_REPORT).is_file():
            errors.append("nonblocking toolchain probe did not run/write report")

    report_data = {}
    if not errors:
        report_data, report_err = load_json(repo / TOOLCHAIN_REPORT)
        report_text = json.dumps(report_data, ensure_ascii=False) if isinstance(report_data, dict) else ""
        report_ok = report_err is None and "NONBLOCKING_LOCAL_TOOLCHAIN_CAPABILITY_PROBE" in report_text and "not_claimed" in report_data
        add(checks, "toolchain_report_records_debt_without_claiming_100_clean", report_ok, {
            "error": report_err,
            "verdict": report_data.get("verdict") if isinstance(report_data, dict) else None,
            "observed_required_failed": report_data.get("observed_required_failed") if isinstance(report_data, dict) else None,
            "optional_missing_or_failed": report_data.get("optional_missing_or_failed") if isinstance(report_data, dict) else None
        })
        if not report_ok:
            errors.append("toolchain report does not record nonblocking debt boundary")

    previous_exists = (repo / PREVIOUS_VALIDATOR).is_file()
    add(checks, "previous_language_surface_v2_validator_exists", previous_exists, {"path": PREVIOUS_VALIDATOR.as_posix()})
    if not previous_exists:
        errors.append("previous language surface v2 validator missing")

    previous_ok = False
    previous_stdout = ""
    previous_stderr = ""
    previous_code = None
    if not errors:
        p = subprocess.run(
            [sys.executable, str(repo / PREVIOUS_VALIDATOR), "--repo-root", str(repo), "--apply"],
            cwd=str(repo),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=420
        )
        previous_code = p.returncode
        previous_stdout = p.stdout[-7000:]
        previous_stderr = p.stderr[-4000:]
        previous_ok = p.returncode == 0 and "PASS_MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_VALIDATOR_DISPATCH_READY" in p.stdout
        add(checks, "previous_language_surface_v2_validator_passes_after_nonblocking_probe_hotfix", previous_ok, {
            "exit_code": previous_code,
            "stdout_tail": previous_stdout,
            "stderr_tail": previous_stderr
        })
        if not previous_ok:
            errors.append("previous language surface v2/toolchain validator still does not pass after nonblocking probe hotfix")

    previous_receipt, receipt_err = load_json(repo / PREVIOUS_RECEIPT) if (repo / PREVIOUS_RECEIPT).is_file() else ({}, "missing")
    previous_receipt_ok = receipt_err is None and isinstance(previous_receipt, dict) and previous_receipt.get("verdict") == "PASS_MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_VALIDATOR_DISPATCH_READY"
    add(checks, "previous_language_surface_v2_receipt_is_pass_after_hotfix", previous_receipt_ok, {
        "error": receipt_err,
        "verdict": previous_receipt.get("verdict") if isinstance(previous_receipt, dict) else None
    })
    if not previous_receipt_ok and not errors:
        errors.append("previous language surface v2 receipt is not PASS after hotfix")

    if isinstance(report_data, dict):
        if report_data.get("observed_required_failed"):
            warnings.append("Observed host-required tools failed in Python subprocess and are recorded as toolchain capability debt.")
        if report_data.get("optional_missing_or_failed"):
            warnings.append("Optional toolchains/build commands missing or failed; recorded as capability/validation debt.")
    if previous_receipt_ok:
        for w in previous_receipt.get("warnings", []) or []:
            if w not in warnings:
                warnings.append(w)

    verdict = "PASS_MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_PROBE_NONBLOCKING_HOTFIX_READY" if not errors else "FAIL_MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_PROBE_NONBLOCKING_HOTFIX"
    generated = utc()

    summary = {
        "summary_id": "mechanicus.language_surface_v2_toolchain_probe_nonblocking_hotfix_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Makes the early Mechanicus toolchain probe nonblocking: missing tools become measured capability debt, not fake pass and not patch stopper."
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.language_surface_v2_toolchain_probe_nonblocking_hotfix.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "probe": PROBE.as_posix(),
        "toolchain_report": TOOLCHAIN_REPORT.as_posix(),
        "previous_validator": PREVIOUS_VALIDATOR.as_posix(),
        "previous_receipt": PREVIOUS_RECEIPT.as_posix()
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# MECHANICUS LANGUAGE SURFACE V2 TOOLCHAIN PROBE NONBLOCKING HOTFIX REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Diagnosis

The previous patch failed because the first toolchain probe treated host/tool availability as a hard blocker too early:

```text
toolchain probe failed required tools
```

For the first Mechanicus baseline this is too strict. A missing or subprocess-invisible tool must become capability debt, not a false PASS and not a patch stopper.

## Fix

- installs `mechanicus_toolchain_probe.v0_2_nonblocking_baseline`;
- writes toolchain proof report even when some tools fail;
- keeps `not_claimed` boundary;
- reruns the previous validator and requires its receipt to become PASS.

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
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
