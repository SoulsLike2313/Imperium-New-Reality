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

TASK_ID = "MECHANICUS-TOOL-ACCUMULATION-AND-ADMISSION-GATE-0001"
VALIDATOR_ID = "mechanicus_tool_accumulation_and_admission_gate_validator.v0_1"

LAW = Path("ORGANS/MECHANICUS/LAWS/MECHANICUS_TOOL_ACCUMULATION_AND_ADMISSION_LAW_V0_1.json")
SCHEMA = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_TOOL_REGISTRY_SCHEMA_V0_1.json")
ADMISSION = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_TOOL_ADMISSION_GATE_MATRIX_V0_1.json")
CUSTODES = Path("ORGANS/CUSTODES/MATRICES/CUSTODES_MECHANICUS_TOOL_ADMISSION_PROSECUTOR_MATRIX_V0_1.json")
THRONE = Path("ORGANS/THRONE/MATRICES/THRONE_MECHANICUS_TOOL_ADMISSION_CROWN_GATE_MATRIX_V0_1.json")
TOOL = Path("ORGANS/MECHANICUS/TOOLS/scan_mechanicus_tool_inventory.py")

INVENTORY = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_INVENTORY_V0_1.json")
RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_tool_accumulation_and_admission_gate_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_ACCUMULATION_AND_ADMISSION_GATE_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_ACCUMULATION_AND_ADMISSION_GATE_REPORT_V0_1.md")

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

def has_all(text: str, needles: List[str]) -> bool:
    return all(n in text for n in needles)

def run_tool(repo: Path):
    p = subprocess.run(
        [sys.executable, str(repo / TOOL), "--repo-root", str(repo), "--out", INVENTORY.as_posix()],
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=240
    )
    return {"exit_code": p.returncode, "stdout_tail": p.stdout[-4000:], "stderr_tail": p.stderr[-3000:], "out_exists": (repo / INVENTORY).is_file()}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    for name, path, needles in [
        ("tool_accumulation_law", LAW, ["Mechanicus must accumulate tools", "REWORK_REQUIRED_WITHIN_TASK", "No dirty helper may become hidden infrastructure"]),
        ("tool_registry_schema", SCHEMA, ["external_tool", "internal_tool", "required_tool_record_fields", "dirty_rejection_reasons"]),
        ("tool_admission_gate_matrix", ADMISSION, ["score_total", "REJECTED_REWORK_REQUIRED", "executor_promotes_rejected_tool"]),
        ("custodes_tool_admission_matrix", CUSTODES, ["prosecutor_not_helper", "servitor_generated_tool_auto_accepted", "dirty_tool_promoted"]),
        ("throne_tool_admission_matrix", THRONE, ["No tool may become global Imperium infrastructure", "No rejected tool may be promoted"]),
    ]:
        data, err = load_json(repo / path) if (repo / path).is_file() else ({}, "missing")
        text = json.dumps(data, ensure_ascii=False) if isinstance(data, dict) else ""
        ok = err is None and has_all(text, needles)
        add(checks, f"{name}_exists_and_declares_required_boundaries", ok, {"path": path.as_posix(), "error": err})
        if not ok:
            errors.append(f"{name} missing or incomplete")

    admission, admission_err = load_json(repo / ADMISSION) if (repo / ADMISSION).is_file() else ({}, "missing")
    dims = admission.get("dimensions", []) if isinstance(admission, dict) else []
    weight_sum = sum(int(d.get("weight", 0)) for d in dims if isinstance(d, dict))
    add(checks, "tool_admission_gate_weights_sum_to_100", admission_err is None and weight_sum == 100, {"weight_sum": weight_sum, "error": admission_err})
    if admission_err is not None or weight_sum != 100:
        errors.append("tool admission gate weights do not sum to 100")

    tool_ok = (repo / TOOL).is_file()
    add(checks, "tool_inventory_scanner_exists", tool_ok, {"path": TOOL.as_posix()})
    if not tool_ok:
        errors.append("tool inventory scanner missing")

    inventory_data = {}
    if not errors:
        r = run_tool(repo)
        add(checks, "tool_inventory_scanner_runs_and_writes_report", r["exit_code"] == 0 and r["out_exists"], r)
        if r["exit_code"] != 0 or not r["out_exists"]:
            errors.append("tool inventory scanner did not run/write report")
        else:
            inventory_data, inv_err = load_json(repo / INVENTORY)
            counts = inventory_data.get("counts_by_class", {}) if isinstance(inventory_data, dict) else {}
            inv_ok = inv_err is None and counts.get("external_tool", 0) > 0 and counts.get("internal_tool", 0) > 0
            add(checks, "tool_inventory_contains_external_and_internal_tools", inv_ok, {"error": inv_err, "counts_by_class": counts})
            if not inv_ok:
                errors.append("tool inventory does not contain both external and internal tools")
            states = inventory_data.get("counts_by_state", {}) if isinstance(inventory_data, dict) else {}
            state_ok = any(k in states for k in ["ADMITTED_BASELINE", "CANDIDATE", "REJECTED_REWORK_REQUIRED"])
            add(checks, "tool_inventory_declares_admission_states", state_ok, {"counts_by_state": states})
            if not state_ok:
                errors.append("tool inventory does not declare admission states")

    if isinstance(inventory_data, dict):
        states = inventory_data.get("counts_by_state", {})
        if states.get("CANDIDATE"):
            warnings.append(f"Tool candidates visible: {states.get('CANDIDATE')}")
        if states.get("REJECTED_REWORK_REQUIRED"):
            warnings.append(f"Tools requiring rework visible: {states.get('REJECTED_REWORK_REQUIRED')}")
        warnings.extend(inventory_data.get("warnings", [])[:5])

    verdict = "PASS_MECHANICUS_TOOL_ACCUMULATION_AND_ADMISSION_GATE_READY" if not errors else "FAIL_MECHANICUS_TOOL_ACCUMULATION_AND_ADMISSION_GATE"
    generated = utc()
    summary = {
        "summary_id": "mechanicus.tool_accumulation_and_admission_gate_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "tool_inventory": INVENTORY.as_posix(),
        "counts_by_class": inventory_data.get("counts_by_class", {}) if isinstance(inventory_data, dict) else {},
        "counts_by_state": inventory_data.get("counts_by_state", {}) if isinstance(inventory_data, dict) else {},
        "meaning": "Mechanicus now accumulates external/internal tools and defines admission/rejection/rework gates."
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.tool_accumulation_and_admission_gate.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "law": LAW.as_posix(),
        "schema": SCHEMA.as_posix(),
        "admission_matrix": ADMISSION.as_posix(),
        "tool_inventory": INVENTORY.as_posix()
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    class_md = "\n".join(f"- `{k}`: `{v}`" for k, v in (inventory_data.get("counts_by_class", {}) if isinstance(inventory_data, dict) else {}).items()) or "- none"
    state_md = "\n".join(f"- `{k}`: `{v}`" for k, v in (inventory_data.get("counts_by_state", {}) if isinstance(inventory_data, dict) else {}).items()) or "- none"

    (repo / REPORT).write_text(f"""# MECHANICUS TOOL ACCUMULATION AND ADMISSION GATE REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

Mechanicus is not just a writer of tools. It is the organ that accumulates, classifies, admits, rejects, quarantines and tracks tools.

External tools are host/language/library/engine capabilities.  
Internal tools are validators, scanners, runners, adapters and task-created helpers.

## Executor loop law

```text
If an internal tool created during a task fails admission, the task should not silently stop.
The executor must fix the tool inside the task loop or declare an Owner-visible blocker.
The rejected tool cannot be promoted or used as accepted infrastructure.
```

## Counts by class

{class_md}

## Counts by state

{state_md}

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
        "tool_inventory": INVENTORY.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
