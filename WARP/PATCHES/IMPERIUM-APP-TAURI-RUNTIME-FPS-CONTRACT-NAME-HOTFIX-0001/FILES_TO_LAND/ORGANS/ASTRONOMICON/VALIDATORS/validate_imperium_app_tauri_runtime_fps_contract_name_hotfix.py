#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "IMPERIUM-APP-TAURI-RUNTIME-FPS-CONTRACT-NAME-HOTFIX-0001"
VALIDATOR_ID = "imperium_app_tauri_runtime_fps_contract_name_hotfix_validator.v0_1"

EXPECTED_CONTRACT = Path("SUPPORT/APP_TAURI/contracts/IMPERIUM_TAURI_RUNTIME_WINDOW_FPS_PROOF_CONTRACT_V0_1.json")
OLD_CONTRACT = Path("SUPPORT/APP_TAURI/contracts/IMPERIUM_TAURI_RUNTIME_FPS_PROOF_CONTRACT_V0_1.json")
RUNTIME_VALIDATOR = Path("ORGANS/ASTRONOMICON/VALIDATORS/validate_imperium_app_tauri_runtime_window_fps_proof.py")
RUNTIME_RECEIPT = Path("ORGANS/ASTRONOMICON/RECEIPTS/imperium_app_tauri_runtime_window_fps_proof_receipt.json")

RECEIPT = Path("ORGANS/ASTRONOMICON/RECEIPTS/imperium_app_tauri_runtime_fps_contract_name_hotfix_receipt.json")
SUMMARY = Path("ORGANS/ASTRONOMICON/REPORTS/IMPERIUM_APP_TAURI_RUNTIME_FPS_CONTRACT_NAME_HOTFIX_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/ASTRONOMICON/REPORTS/IMPERIUM_APP_TAURI_RUNTIME_FPS_CONTRACT_NAME_HOTFIX_REPORT_V0_1.md")

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

    contract_path = repo / EXPECTED_CONTRACT
    old_path = repo / OLD_CONTRACT

    data, err = load_json(contract_path) if contract_path.is_file() else ({}, "missing")
    contract_ok = err is None and isinstance(data, dict) and data.get("contract_id") == "IMPERIUM_TAURI_RUNTIME_WINDOW_FPS_PROOF_CONTRACT_V0_1"
    add(checks, "expected_runtime_window_fps_contract_exists_and_parses", contract_ok, {
        "path": EXPECTED_CONTRACT.as_posix(),
        "error": err,
        "contract_id": data.get("contract_id") if isinstance(data, dict) else None,
        "bytes": contract_path.stat().st_size if contract_path.is_file() else 0
    })
    if not contract_ok:
        errors.append("expected runtime window FPS contract file is missing or invalid")

    old_exists = old_path.is_file()
    add(checks, "old_short_contract_name_may_exist_but_is_not_required", True, {
        "old_path": OLD_CONTRACT.as_posix(),
        "exists": old_exists
    })
    if old_exists:
        warnings.append("old short contract filename still exists; harmless, but canonical validator requires the WINDOW filename")

    runtime_ok = False
    runtime_code = None
    runtime_stdout = ""
    runtime_stderr = ""
    if not errors:
        p = subprocess.run(
            ["python", str(repo / RUNTIME_VALIDATOR), "--repo-root", str(repo), "--apply"],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=420,
            encoding="utf-8",
            errors="replace",
        )
        runtime_code = p.returncode
        runtime_stdout = p.stdout[-5000:]
        runtime_stderr = p.stderr[-4000:]
        runtime_ok = p.returncode == 0 and "PASS_IMPERIUM_APP_TAURI_RUNTIME_WINDOW_FPS_PROOF_READY" in p.stdout

    add(checks, "runtime_window_fps_validator_rerun_after_contract_name_fix", runtime_ok, {
        "exit_code": runtime_code,
        "stdout_tail": runtime_stdout,
        "stderr_tail": runtime_stderr
    })
    if not runtime_ok and not errors:
        errors.append("runtime window FPS validator still does not pass after contract filename hotfix")

    runtime_receipt, runtime_err = load_json(repo / RUNTIME_RECEIPT) if (repo / RUNTIME_RECEIPT).is_file() else ({}, "missing")
    runtime_receipt_ok = runtime_err is None and isinstance(runtime_receipt, dict) and str(runtime_receipt.get("verdict", "")).startswith("PASS")
    add(checks, "runtime_window_fps_receipt_is_pass_after_contract_name_fix", runtime_receipt_ok, {
        "error": runtime_err,
        "verdict": runtime_receipt.get("verdict") if isinstance(runtime_receipt, dict) else None
    })
    if not runtime_receipt_ok and not errors:
        errors.append("runtime window FPS receipt is not PASS after contract filename hotfix")

    verdict = "PASS_IMPERIUM_APP_TAURI_RUNTIME_FPS_CONTRACT_NAME_HOTFIX_READY" if not errors else "FAIL_IMPERIUM_APP_TAURI_RUNTIME_FPS_CONTRACT_NAME_HOTFIX"
    generated = utc()

    summary = {
        "summary_id": "astronomicon.imperium_app_tauri_runtime_fps_contract_name_hotfix_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Fixes runtime FPS proof contract filename mismatch and reruns the runtime FPS proof validator."
    }
    receipt = {
        "receipt_id": "receipt.astronomicon.imperium_app_tauri_runtime_fps_contract_name_hotfix.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# IMPERIUM APP TAURI RUNTIME FPS CONTRACT NAME HOTFIX REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

The runtime FPS patch failed before opening Tauri because a required file was missing.

Root cause:

```text
validator expected:
SUPPORT/APP_TAURI/contracts/IMPERIUM_TAURI_RUNTIME_WINDOW_FPS_PROOF_CONTRACT_V0_1.json

previous patch wrote:
SUPPORT/APP_TAURI/contracts/IMPERIUM_TAURI_RUNTIME_FPS_PROOF_CONTRACT_V0_1.json
```

This hotfix adds the canonical expected filename and reruns the runtime window FPS validator.

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
        "report": REPORT.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
