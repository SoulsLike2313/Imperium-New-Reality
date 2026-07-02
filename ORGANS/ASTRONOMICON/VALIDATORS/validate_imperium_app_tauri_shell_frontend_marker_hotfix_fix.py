#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "IMPERIUM-APP-TAURI-SHELL-FRONTEND-MARKER-HOTFIX-FIX-0001"
VALIDATOR_ID = "imperium_app_tauri_shell_frontend_marker_hotfix_fix_validator.v0_1"

FOUNDATION_VALIDATOR = Path("ORGANS/ASTRONOMICON/VALIDATORS/validate_imperium_app_tauri_shell_foundation.py")
MAIN_JS = Path("SUPPORT/APP_TAURI/src/main.js")

RECEIPT = Path("ORGANS/ASTRONOMICON/RECEIPTS/imperium_app_tauri_shell_frontend_marker_hotfix_fix_receipt.json")
SUMMARY = Path("ORGANS/ASTRONOMICON/REPORTS/IMPERIUM_APP_TAURI_SHELL_FRONTEND_MARKER_HOTFIX_FIX_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/ASTRONOMICON/REPORTS/IMPERIUM_APP_TAURI_SHELL_FRONTEND_MARKER_HOTFIX_FIX_REPORT_V0_1.md")

MARKER_BLOCK = """
// IMPERIUM_TAURI_SHELL
// Frontend identity marker required by Imperium Tauri foundation validator.
// Do not remove: the shell contract deliberately binds the web frontend to the Imperium app identity.
const IMPERIUM_TAURI_SHELL = "IMPERIUM_TAURI_SHELL";
""".strip() + "\n\n"

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def insert_after_imports(text: str, block: str) -> str:
    # Preserve ES module validity: imports must stay before executable statements.
    lines = text.splitlines(keepends=True)
    idx = 0
    while idx < len(lines):
        stripped = lines[idx].strip()
        if stripped.startswith("import "):
            idx += 1
            continue
        if stripped == "":
            idx += 1
            continue
        break
    return "".join(lines[:idx]) + block + "".join(lines[idx:])

def ensure_marker(repo: Path, apply: bool) -> Dict[str, Any]:
    path = repo / MAIN_JS
    if not path.is_file():
        return {"ok": False, "changed": False, "error": f"missing {MAIN_JS.as_posix()}"}

    text = path.read_text(encoding="utf-8", errors="replace")
    before_has_token = "IMPERIUM_TAURI_SHELL" in text
    before_has_const = re.search(r"\bconst\s+IMPERIUM_TAURI_SHELL\s*=", text) is not None

    changed = False
    new_text = text

    if not before_has_const:
        # If the token exists only in index.html or a comment elsewhere, still add the actual JS constant.
        new_text = insert_after_imports(new_text, MARKER_BLOCK)
        changed = True
    elif not before_has_token:
        # Defensive branch; practically const implies token.
        new_text = insert_after_imports(new_text, MARKER_BLOCK)
        changed = True

    # Add a harmless runtime log after renderShell only if both marker and log are absent.
    if "Shell marker:" not in new_text and "renderShell();" in new_text and "function log(" in new_text:
        new_text = new_text.replace(
            "renderShell();",
            "renderShell();\nlog(`Shell marker: ${IMPERIUM_TAURI_SHELL}`, \"auth\");",
            1,
        )
        changed = True

    if changed and apply:
        path.write_text(new_text, encoding="utf-8")

    final_text = new_text if changed else text
    return {
        "ok": ("IMPERIUM_TAURI_SHELL" in final_text and re.search(r"\bconst\s+IMPERIUM_TAURI_SHELL\s*=", final_text) is not None),
        "changed": changed,
        "before_has_token": before_has_token,
        "before_has_const": before_has_const,
        "after_has_token": "IMPERIUM_TAURI_SHELL" in final_text,
        "after_has_const": re.search(r"\bconst\s+IMPERIUM_TAURI_SHELL\s*=", final_text) is not None,
        "path": MAIN_JS.as_posix(),
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

    patch_result = ensure_marker(repo, args.apply)
    add(checks, "main_js_shell_marker_applied_or_present", bool(patch_result.get("ok")), patch_result)
    if not patch_result.get("ok"):
        errors.append("frontend shell marker still missing from main.js after in-place fix")

    # Verify exact checked frontend text after write.
    text = (repo / MAIN_JS).read_text(encoding="utf-8", errors="replace") if (repo / MAIN_JS).is_file() else ""
    exact_ok = "IMPERIUM_TAURI_SHELL" in text and re.search(r"\bconst\s+IMPERIUM_TAURI_SHELL\s*=", text) is not None
    add(checks, "main_js_exact_marker_verification", exact_ok, {"contains_token": "IMPERIUM_TAURI_SHELL" in text})
    if not exact_ok:
        errors.append("exact marker verification failed")

    foundation_ok = False
    foundation_stdout = ""
    foundation_stderr = ""
    foundation_code = None
    if not errors:
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
            foundation_stdout = p.stdout[-4000:]
            foundation_stderr = p.stderr[-2000:]
            foundation_ok = p.returncode == 0 and "PASS_IMPERIUM_APP_TAURI_SHELL_FOUNDATION_READY" in p.stdout
        else:
            errors.append("foundation validator missing")

    add(checks, "foundation_validator_passes_after_in_place_marker_fix", foundation_ok, {
        "exit_code": foundation_code,
        "stdout_tail": foundation_stdout,
        "stderr_tail": foundation_stderr,
    })
    if not foundation_ok and not errors:
        errors.append("foundation validator still does not pass after in-place marker fix")

    verdict = "PASS_IMPERIUM_APP_TAURI_SHELL_FRONTEND_MARKER_HOTFIX_FIX_READY" if not errors else "FAIL_IMPERIUM_APP_TAURI_SHELL_FRONTEND_MARKER_HOTFIX_FIX"
    generated = utc()
    summary = {
        "summary_id": "astronomicon.imperium_app_tauri_shell_frontend_marker_hotfix_fix_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Robust in-place fix for main.js marker. Keeps ES imports valid, then reruns original Tauri foundation validator."
    }
    receipt = {
        "receipt_id": "receipt.astronomicon.imperium_app_tauri_shell_frontend_marker_hotfix_fix.v0_1",
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
    (repo / REPORT).write_text(f"""# IMPERIUM APP TAURI SHELL FRONTEND MARKER HOTFIX FIX REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

The previous marker hotfix could still fail if `main.js` in the working tree was not overwritten as expected.

This fix patches `SUPPORT/APP_TAURI/src/main.js` in-place and inserts the frontend identity marker after ES import lines, preserving module syntax.

Then it reruns the original foundation validator.

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
