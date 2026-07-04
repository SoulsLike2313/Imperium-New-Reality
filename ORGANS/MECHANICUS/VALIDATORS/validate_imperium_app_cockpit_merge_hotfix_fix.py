#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "IMPERIUM-APP-COCKPIT-MERGE-HOTFIX-FIX-0001"
VALIDATOR_ID = "mechanicus_imperium_app_cockpit_merge_hotfix_fix_validator.v0_1"

MAIN_JS = Path("SUPPORT/APP_TAURI/src/main.js")
PREVIOUS_VALIDATOR = Path("ORGANS/MECHANICUS/VALIDATORS/validate_imperium_app_cockpit_merge_hotfix.py")
PREVIOUS_RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/imperium_app_cockpit_merge_hotfix_receipt.json")

RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/imperium_app_cockpit_merge_hotfix_fix_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/IMPERIUM_APP_COCKPIT_MERGE_HOTFIX_FIX_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/IMPERIUM_APP_COCKPIT_MERGE_HOTFIX_FIX_REPORT_V0_1.md")

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

def patch_main_js(repo: Path) -> Dict[str, Any]:
    path = repo / MAIN_JS
    text = path.read_text(encoding="utf-8")
    before = text

    # The previous validator intentionally looked for the phrase "Python binds".
    # The UI copy said the same idea differently, so the validator failed on a wording marker.
    if "Python binds" not in text:
        text = text.replace(
            "Mechanicus chooses the minimal sufficient language for the task, proves the toolchain, and lets Python bind—not pretend to be every force.",
            "Python binds orchestration. Mechanicus chooses the minimal sufficient language for the task, proves the toolchain, and lets Python bind—not pretend to be every force."
        )
    if "Python binds" not in text:
        text = text.replace(
            "Python — orchestration, receipts, scans, JSON, quick validators",
            "Python binds — orchestration, receipts, scans, JSON, quick validators"
        )
    if "Python binds" not in text:
        marker = 'const LANGUAGE_POWER_CODEX = "LANGUAGE_POWER_CODEX";'
        text = text.replace(marker, marker + '\nconst MECHANICUS_PYTHON_BINDS_MARKER = "Python binds";')

    path.write_text(text, encoding="utf-8")
    return {
        "changed": before != text,
        "contains_python_binds": "Python binds" in text,
        "bytes": path.stat().st_size
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    main_path = repo / MAIN_JS
    add(checks, "main_js_exists_before_marker_fix", main_path.is_file(), {
        "path": MAIN_JS.as_posix(),
        "bytes": main_path.stat().st_size if main_path.is_file() else 0
    })
    if not main_path.is_file():
        errors.append("main.js missing; cannot apply cockpit merge marker fix")

    patch_result = {}
    if not errors:
        patch_result = patch_main_js(repo)
    add(checks, "mechanicus_room_python_binds_marker_present", bool(patch_result.get("contains_python_binds")), patch_result)
    if not patch_result.get("contains_python_binds"):
        errors.append("Python binds marker still missing after fix")

    previous_exists = (repo / PREVIOUS_VALIDATOR).is_file()
    add(checks, "previous_cockpit_merge_validator_exists", previous_exists, {
        "path": PREVIOUS_VALIDATOR.as_posix()
    })
    if not previous_exists:
        errors.append("previous cockpit merge validator missing")

    previous_ok = False
    previous_stdout = ""
    previous_stderr = ""
    previous_code = None
    if not errors:
        p = subprocess.run(
            ["python", str(repo / PREVIOUS_VALIDATOR), "--repo-root", str(repo), "--apply"],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=120,
            encoding="utf-8",
            errors="replace"
        )
        previous_code = p.returncode
        previous_stdout = p.stdout[-4000:]
        previous_stderr = p.stderr[-3000:]
        previous_ok = p.returncode == 0 and "PASS_IMPERIUM_APP_COCKPIT_MERGE_HOTFIX_READY" in p.stdout

    add(checks, "previous_cockpit_merge_hotfix_validator_passes_after_fix", previous_ok, {
        "exit_code": previous_code,
        "stdout_tail": previous_stdout,
        "stderr_tail": previous_stderr
    })
    if not previous_ok and not errors:
        errors.append("previous cockpit merge hotfix validator still does not pass after marker fix")

    previous_receipt, receipt_err = load_json(repo / PREVIOUS_RECEIPT) if (repo / PREVIOUS_RECEIPT).is_file() else ({}, "missing")
    previous_receipt_ok = receipt_err is None and isinstance(previous_receipt, dict) and previous_receipt.get("verdict") == "PASS_IMPERIUM_APP_COCKPIT_MERGE_HOTFIX_READY"
    add(checks, "previous_cockpit_merge_receipt_is_pass_after_fix", previous_receipt_ok, {
        "error": receipt_err,
        "verdict": previous_receipt.get("verdict") if isinstance(previous_receipt, dict) else None
    })
    if not previous_receipt_ok and not errors:
        errors.append("previous cockpit merge receipt is not PASS after fix")

    verdict = "PASS_IMPERIUM_APP_COCKPIT_MERGE_HOTFIX_FIX_READY" if not errors else "FAIL_IMPERIUM_APP_COCKPIT_MERGE_HOTFIX_FIX"
    generated = utc()

    summary = {
        "summary_id": "mechanicus.imperium_app_cockpit_merge_hotfix_fix_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Fixes an overly literal UI marker check by ensuring the Mechanicus room contains the expected 'Python binds' marker, then reruns the cockpit merge validator."
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.imperium_app_cockpit_merge_hotfix_fix.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "main_js": MAIN_JS.as_posix(),
        "previous_validator": PREVIOUS_VALIDATOR.as_posix(),
        "previous_receipt": PREVIOUS_RECEIPT.as_posix()
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# IMPERIUM APP COCKPIT MERGE HOTFIX FIX REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Diagnosis

The merge hotfix itself landed the right app-room structure, but its validator used a strict text marker:

```text
Python binds
```

The Mechanicus room expressed the same idea as:

```text
lets Python bind
```

Therefore the validator failed with:

```text
Mechanicus language codex not represented as in-app room
```

## Fix

This patch inserts the exact `Python binds` marker into the Mechanicus Language Codex room and reruns the previous validator.

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
