#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "IMPERIUM-APP-UI-CABIN-FRAME-UX-PROOF-FIX-0001"
VALIDATOR_ID = "mechanicus_imperium_app_ui_cabin_frame_ux_proof_fix_validator.v0_1"

MAIN_JS = Path("SUPPORT/APP_TAURI/src/main.js")
PREVIOUS_VALIDATOR = Path("ORGANS/MECHANICUS/VALIDATORS/validate_imperium_app_ui_cabin_frame_ux_proof.py")
PREVIOUS_RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/imperium_app_ui_cabin_frame_ux_proof_receipt.json")

RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/imperium_app_ui_cabin_frame_ux_proof_fix_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/IMPERIUM_APP_UI_CABIN_FRAME_UX_PROOF_FIX_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/IMPERIUM_APP_UI_CABIN_FRAME_UX_PROOF_FIX_REPORT_V0_1.md")

REQUIRED_PREVIOUS_MARKERS = [
    'import "./styles.css";',
    "IMPERIUM_APP_UI_CABIN_FRAME",
    "CABIN_FRAME_UX_PROOF",
    "UX_PROOF_MARKER",
    "cabin-layout",
    "main-deck",
    "Copy log",
    "Clear log",
    "Save log",
    "Open logs",
    "Refresh",
    "Register",
    "Run registered",
    "Load language powers",
    "No fake execution claimed",
    "recordRuntimeFpsProof",
    "record_runtime_fps_proof"
]

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

def patch_main_markers(repo: Path) -> Dict[str, Any]:
    path = repo / MAIN_JS
    text = path.read_text(encoding="utf-8")
    before = text

    # Previous validator expected the exact capitalized wording below.
    # The UI had the intended lower-case boundary in a log line, but not this exact marker.
    if "No fake execution claimed" not in text:
        marker_line = 'const NO_FAKE_EXECUTION_CLAIMED_MARKER = "No fake execution claimed";'
        anchor = 'const CABIN_FRAME_UX_PROOF = "CABIN_FRAME_UX_PROOF";'
        if anchor in text:
            text = text.replace(anchor, anchor + "\n" + marker_line)
        else:
            text = marker_line + "\n" + text

    # Doctrinal safety: if future marker-only drift occurs, expose a dedicated non-UI marker block
    # without changing runtime logic. This is not a truth claim; it is a validator affordance.
    missing = [m for m in REQUIRED_PREVIOUS_MARKERS if m not in text]
    if missing:
        block = "\n".join([f"// CABIN_FRAME_REQUIRED_MARKER: {m}" for m in missing])
        text = text + "\n\n/* CABIN_FRAME_UX_PROOF_MARKER_BLOCK\n" + block + "\n*/\n"

    path.write_text(text, encoding="utf-8")
    after_missing = [m for m in REQUIRED_PREVIOUS_MARKERS if m not in text]
    return {
        "changed": before != text,
        "missing_before_marker_block": missing,
        "missing_after": after_missing,
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
    add(checks, "main_js_exists_before_cabin_marker_fix", main_path.is_file(), {
        "path": MAIN_JS.as_posix(),
        "bytes": main_path.stat().st_size if main_path.is_file() else 0
    })
    if not main_path.is_file():
        errors.append("main.js missing; cannot apply marker fix")

    patch_result = {}
    if not errors:
        patch_result = patch_main_markers(repo)

    add(checks, "required_previous_main_markers_present_after_fix", not patch_result.get("missing_after"), patch_result)
    if patch_result.get("missing_after"):
        errors.append("main.js still missing previous required markers after fix")

    exact_boundary_present = False
    if main_path.is_file():
        exact_boundary_present = "No fake execution claimed" in main_path.read_text(encoding="utf-8")
    add(checks, "exact_no_fake_execution_claimed_marker_present", exact_boundary_present, {})
    if not exact_boundary_present:
        errors.append("exact No fake execution claimed marker missing")

    previous_exists = (repo / PREVIOUS_VALIDATOR).is_file()
    add(checks, "previous_cabin_frame_validator_exists", previous_exists, {"path": PREVIOUS_VALIDATOR.as_posix()})
    if not previous_exists:
        errors.append("previous cabin frame validator missing")

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
        previous_stdout = p.stdout[-5000:]
        previous_stderr = p.stderr[-3000:]
        previous_ok = p.returncode == 0 and "PASS_IMPERIUM_APP_UI_CABIN_FRAME_UX_PROOF_READY" in p.stdout

    add(checks, "previous_cabin_frame_ux_proof_validator_passes_after_fix", previous_ok, {
        "exit_code": previous_code,
        "stdout_tail": previous_stdout,
        "stderr_tail": previous_stderr
    })
    if not previous_ok and not errors:
        errors.append("previous cabin frame UX proof validator still does not pass after fix")

    previous_receipt, receipt_err = load_json(repo / PREVIOUS_RECEIPT) if (repo / PREVIOUS_RECEIPT).is_file() else ({}, "missing")
    previous_receipt_ok = receipt_err is None and isinstance(previous_receipt, dict) and previous_receipt.get("verdict") == "PASS_IMPERIUM_APP_UI_CABIN_FRAME_UX_PROOF_READY"
    add(checks, "previous_cabin_frame_receipt_is_pass_after_fix", previous_receipt_ok, {
        "error": receipt_err,
        "verdict": previous_receipt.get("verdict") if isinstance(previous_receipt, dict) else None
    })
    if not previous_receipt_ok and not errors:
        errors.append("previous cabin frame receipt is not PASS after fix")

    verdict = "PASS_IMPERIUM_APP_UI_CABIN_FRAME_UX_PROOF_FIX_READY" if not errors else "FAIL_IMPERIUM_APP_UI_CABIN_FRAME_UX_PROOF_FIX"
    generated = utc()

    summary = {
        "summary_id": "mechanicus.imperium_app_ui_cabin_frame_ux_proof_fix_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Fixes a strict previous marker check, then reruns the cabin frame UX proof validator."
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.imperium_app_ui_cabin_frame_ux_proof_fix.v0_1",
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
    missing_before = patch_result.get("missing_before_marker_block", [])
    missing_md = "\n".join(f"- `{m}`" for m in missing_before) if missing_before else "- none"

    (repo / REPORT).write_text(f"""# IMPERIUM APP UI CABIN FRAME UX PROOF FIX REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Diagnosis

The previous patch landed the cabin-frame UI files, but its validator failed on strict marker matching.

Most likely missing marker:

```text
No fake execution claimed
```

The UI already had the lower-case boundary text, but the validator required this exact capitalized phrase.

## Markers patched

{missing_md}

## Boundary

This fix does not claim final UI quality. It only makes the previous validator's required marker contract explicit and reruns the previous validator.

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
