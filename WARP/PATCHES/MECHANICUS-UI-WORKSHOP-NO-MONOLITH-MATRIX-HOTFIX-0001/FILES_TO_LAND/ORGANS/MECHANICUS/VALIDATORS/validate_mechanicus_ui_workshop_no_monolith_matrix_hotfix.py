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

TASK_ID = "MECHANICUS-UI-WORKSHOP-NO-MONOLITH-MATRIX-HOTFIX-0001"
VALIDATOR_ID = "mechanicus_ui_workshop_no_monolith_matrix_hotfix_validator.v0_1"

MATRIX = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_NO_MONOLITH_ARCHITECTURE_MATRIX_V0_1.json")
PREVIOUS_VALIDATOR = Path("ORGANS/MECHANICUS/VALIDATORS/validate_mechanicus_ui_workshop_and_no_monolith_law.py")
PREVIOUS_RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_ui_workshop_and_no_monolith_law_receipt.json")

RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_ui_workshop_no_monolith_matrix_hotfix_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_UI_WORKSHOP_NO_MONOLITH_MATRIX_HOTFIX_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_UI_WORKSHOP_NO_MONOLITH_MATRIX_HOTFIX_REPORT_V0_1.md")

REQUIRED_BLOCKERS = [
    "single_file_contains_state_render_commands_data_and_events",
    "bitmap_reference_mode_claimed_as_live_ui",
    "backend_multi_domain_monolith",
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

def patch_matrix(repo: Path) -> Dict[str, Any]:
    path = repo / MATRIX
    matrix, err = load_json(path)
    if err:
        return {"ok": False, "error": err, "changed": False}

    blockers = matrix.setdefault("blocking_findings", [])
    before = list(blockers)
    aliases = {
        "backend_command_file_contains_unrelated_policy_domains": "backend_multi_domain_monolith"
    }

    for old, new in aliases.items():
        if old in blockers and new not in blockers:
            blockers.append(new)

    for req in REQUIRED_BLOCKERS:
        if req not in blockers:
            blockers.append(req)

    weights_sum = sum(int(d.get("weight", 0)) for d in matrix.get("dimensions", []) if isinstance(d, dict))
    write_json(path, matrix)
    return {
        "ok": True,
        "changed": blockers != before,
        "weights_sum": weights_sum,
        "before_blockers": before,
        "after_blockers": blockers,
        "required_present": all(x in blockers for x in REQUIRED_BLOCKERS)
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

    matrix_exists = (repo / MATRIX).is_file()
    add(checks, "no_monolith_architecture_matrix_exists_before_hotfix", matrix_exists, {
        "path": MATRIX.as_posix()
    })
    if not matrix_exists:
        errors.append("No-monolith architecture matrix missing; cannot hotfix")

    patch_result: Dict[str, Any] = {}
    if not errors:
        patch_result = patch_matrix(repo)

    add(checks, "matrix_contains_required_backend_multi_domain_blocker_after_hotfix", bool(patch_result.get("required_present")), patch_result)
    if not patch_result.get("required_present"):
        errors.append("Matrix still missing required backend_multi_domain_monolith blocker after hotfix")

    add(checks, "matrix_weights_still_sum_to_100_after_hotfix", patch_result.get("weights_sum") == 100, patch_result)
    if patch_result.get("weights_sum") != 100:
        errors.append("Matrix weights do not sum to 100 after hotfix")

    previous_exists = (repo / PREVIOUS_VALIDATOR).is_file()
    add(checks, "previous_mechanicus_ui_workshop_validator_exists", previous_exists, {
        "path": PREVIOUS_VALIDATOR.as_posix()
    })
    if not previous_exists:
        errors.append("Previous Mechanicus UI workshop validator missing")

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
            timeout=180
        )
        previous_code = p.returncode
        previous_stdout = p.stdout[-6000:]
        previous_stderr = p.stderr[-3000:]
        previous_ok = p.returncode == 0 and "PASS_MECHANICUS_UI_WORKSHOP_AND_NO_MONOLITH_LAW_READY" in p.stdout

    add(checks, "previous_mechanicus_ui_workshop_validator_passes_after_hotfix", previous_ok, {
        "exit_code": previous_code,
        "stdout_tail": previous_stdout,
        "stderr_tail": previous_stderr
    })
    if not previous_ok and not errors:
        errors.append("Previous Mechanicus UI workshop/no-monolith validator still does not pass after hotfix")

    previous_receipt, receipt_err = load_json(repo / PREVIOUS_RECEIPT) if (repo / PREVIOUS_RECEIPT).is_file() else ({}, "missing")
    previous_receipt_ok = receipt_err is None and isinstance(previous_receipt, dict) and previous_receipt.get("verdict") == "PASS_MECHANICUS_UI_WORKSHOP_AND_NO_MONOLITH_LAW_READY"
    add(checks, "previous_mechanicus_ui_workshop_receipt_is_pass_after_hotfix", previous_receipt_ok, {
        "error": receipt_err,
        "verdict": previous_receipt.get("verdict") if isinstance(previous_receipt, dict) else None
    })
    if not previous_receipt_ok and not errors:
        errors.append("Previous Mechanicus UI workshop/no-monolith receipt is not PASS after hotfix")

    if previous_receipt_ok:
        for warning in previous_receipt.get("warnings", []) or []:
            if warning not in warnings:
                warnings.append(warning)

    verdict = "PASS_MECHANICUS_UI_WORKSHOP_NO_MONOLITH_MATRIX_HOTFIX_READY" if not errors else "FAIL_MECHANICUS_UI_WORKSHOP_NO_MONOLITH_MATRIX_HOTFIX"
    generated = utc()

    summary = {
        "summary_id": "mechanicus.ui_workshop_no_monolith_matrix_hotfix_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Adds the required backend_multi_domain_monolith blocker to the no-monolith architecture matrix, then reruns the original Mechanicus UI workshop validator."
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.ui_workshop_no_monolith_matrix_hotfix.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "matrix": MATRIX.as_posix(),
        "previous_validator": PREVIOUS_VALIDATOR.as_posix(),
        "previous_receipt": PREVIOUS_RECEIPT.as_posix()
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# MECHANICUS UI WORKSHOP NO-MONOLITH MATRIX HOTFIX REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Diagnosis

The original law patch failed because the validator required the blocker:

```text
backend_multi_domain_monolith
```

The matrix contained the same intent under a different phrase:

```text
backend_command_file_contains_unrelated_policy_domains
```

The hotfix adds the canonical blocker phrase and reruns the original validator.

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
