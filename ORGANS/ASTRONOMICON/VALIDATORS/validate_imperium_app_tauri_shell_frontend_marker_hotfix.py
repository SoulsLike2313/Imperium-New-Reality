#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

TASK_ID = "IMPERIUM-APP-TAURI-SHELL-FRONTEND-MARKER-HOTFIX-0001"
VALIDATOR_ID = "imperium_app_tauri_shell_frontend_marker_hotfix_validator.v0_1"

FOUNDATION_VALIDATOR = Path("ORGANS/ASTRONOMICON/VALIDATORS/validate_imperium_app_tauri_shell_foundation.py")
MAIN_JS = Path("SUPPORT/APP_TAURI/src/main.js")
RECEIPT = Path("ORGANS/ASTRONOMICON/RECEIPTS/imperium_app_tauri_shell_frontend_marker_hotfix_receipt.json")
SUMMARY = Path("ORGANS/ASTRONOMICON/REPORTS/IMPERIUM_APP_TAURI_SHELL_FRONTEND_MARKER_HOTFIX_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/ASTRONOMICON/REPORTS/IMPERIUM_APP_TAURI_SHELL_FRONTEND_MARKER_HOTFIX_REPORT_V0_1.md")

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

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

    main_path = repo / MAIN_JS
    text = main_path.read_text(encoding="utf-8", errors="replace") if main_path.is_file() else ""

    add(checks, "main_js_exists", main_path.is_file(), {"path": MAIN_JS.as_posix()})
    if not main_path.is_file():
        errors.append("main.js missing")

    marker_ok = "IMPERIUM_TAURI_SHELL" in text and "const IMPERIUM_TAURI_SHELL" in text
    add(checks, "frontend_shell_marker_present_in_main_js", marker_ok, {
        "marker": "IMPERIUM_TAURI_SHELL",
        "path": MAIN_JS.as_posix()
    })
    if not marker_ok:
        errors.append("frontend shell marker still missing from main.js")

    foundation_ok = False
    foundation_stdout = ""
    foundation_stderr = ""
    foundation_code = None
    if (repo / FOUNDATION_VALIDATOR).is_file():
        p = subprocess.run(
            ["python", str(repo / FOUNDATION_VALIDATOR), "--repo-root", str(repo), "--apply"],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=240,
            encoding="utf-8",
            errors="replace",
        )
        foundation_code = p.returncode
        foundation_stdout = p.stdout[-3000:]
        foundation_stderr = p.stderr[-2000:]
        foundation_ok = p.returncode == 0 and "PASS_IMPERIUM_APP_TAURI_SHELL_FOUNDATION_READY" in p.stdout
    else:
        errors.append("foundation validator missing")

    add(checks, "foundation_validator_passes_after_marker_hotfix", foundation_ok, {
        "exit_code": foundation_code,
        "stdout_tail": foundation_stdout,
        "stderr_tail": foundation_stderr,
    })
    if not foundation_ok:
        errors.append("foundation validator still does not pass after marker hotfix")

    verdict = "PASS_IMPERIUM_APP_TAURI_SHELL_FRONTEND_MARKER_HOTFIX_READY" if not errors else "FAIL_IMPERIUM_APP_TAURI_SHELL_FRONTEND_MARKER_HOTFIX"
    generated = utc()
    summary = {
        "summary_id": "astronomicon.imperium_app_tauri_shell_frontend_marker_hotfix_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Fixes false foundation failure by placing IMPERIUM_TAURI_SHELL marker in main.js, where the validator checks frontend markers."
    }
    receipt = {
        "receipt_id": "receipt.astronomicon.imperium_app_tauri_shell_frontend_marker_hotfix.v0_1",
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
    (repo / REPORT).write_text(f"""# IMPERIUM APP TAURI SHELL FRONTEND MARKER HOTFIX REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

Foundation validator checks frontend markers only inside `src/main.js` + `src/styles.css`.

The marker `IMPERIUM_TAURI_SHELL` was present in `index.html`, but not in the checked frontend text.

This hotfix places the marker in `src/main.js` and reruns the original foundation validator.

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
