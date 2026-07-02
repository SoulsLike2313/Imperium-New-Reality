#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

TASK_ID = "THRONE-ASTRONOMICON-STRICT-GATES-ANTI-SELF-DECEPTION-FIX-0001"
VALIDATOR_ID = "throne_astronomicon_anti_self_deception_validator.v0_1"

TOOL = Path("ORGANS/THRONE/TOOLS/throne_astronomicon_strict_gate.py")
MATRIX = Path("ORGANS/THRONE/MATRICES/THRONE_ASTRONOMICON_STRICT_GATES_ANTI_SELF_DECEPTION_MATRIX_V0_2.json")
RECEIPT = Path("ORGANS/THRONE/RECEIPTS/throne_astronomicon_anti_self_deception_validation_receipt.json")
SUMMARY = Path("ORGANS/THRONE/REPORTS/THRONE_ASTRONOMICON_ANTI_SELF_DECEPTION_VALIDATION_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/THRONE/REPORTS/THRONE_ASTRONOMICON_ANTI_SELF_DECEPTION_VALIDATION_REPORT_V0_1.md")

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def git_head(repo: Path) -> str:
    try:
        p = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo), capture_output=True, text=True, timeout=15)
        return p.stdout.strip() if p.returncode == 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"

def load_json(path: Path) -> Tuple[Any, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), None
    except Exception as e:
        return None, str(e)

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

    for rel in [TOOL, MATRIX]:
        ok = (repo / rel).is_file()
        add(checks, f"{rel.name}_exists", ok, {"path": rel.as_posix()})
        if not ok:
            errors.append(f"missing {rel.as_posix()}")

    matrix, matrix_err = load_json(repo / MATRIX) if (repo / MATRIX).is_file() else ({}, "missing")
    add(checks, "anti_self_deception_matrix_parses", matrix_err is None, {"error": matrix_err})
    if matrix_err:
        errors.append("anti-self-deception matrix parse failed")
        matrix = {}

    law = matrix.get("crown_witness_law", []) if isinstance(matrix, dict) else []
    add(checks, "matrix_separates_crown_order_from_self_validation", any("self-validation score must remain zero" in x.lower() for x in law), {"law": law})
    if not any("self-validation score must remain zero" in x.lower() for x in law):
        errors.append("matrix does not require self-validation score zero")

    p = subprocess.run([sys.executable, str(repo / TOOL), "--repo-root", str(repo)], cwd=str(repo), capture_output=True, text=True, timeout=180)
    add(checks, "throne_strict_gate_tool_runs", p.returncode == 0, {"exit_code": p.returncode, "stderr_tail": p.stderr[-1200:], "stdout_tail": p.stdout[-1200:]})
    if p.returncode != 0:
        errors.append("Throne strict gate anti-self-deception tool failed")

    gate_summary, gate_err = load_json(repo / "ORGANS/THRONE/REPORTS/THRONE_ASTRONOMICON_STRICT_GATES_SUMMARY_V0_1.json")
    add(checks, "throne_summary_parses", gate_err is None, {"error": gate_err})
    if gate_err:
        errors.append("Throne summary parse failed")
        gate_summary = {}

    add(checks, "crown_order_passes_but_self_validation_zero", (
        isinstance(gate_summary, dict) and
        str(gate_summary.get("verdict", "")).startswith("PASS") and
        gate_summary.get("astronomicon_crown_order_score") == 100.0 and
        gate_summary.get("throne_self_validation_score") == 0.0 and
        gate_summary.get("external_witness_for_throne_score") == 0.0
    ), {
        "verdict": gate_summary.get("verdict") if isinstance(gate_summary, dict) else None,
        "crown_order": gate_summary.get("astronomicon_crown_order_score") if isinstance(gate_summary, dict) else None,
        "self_validation": gate_summary.get("throne_self_validation_score") if isinstance(gate_summary, dict) else None,
        "external_witness": gate_summary.get("external_witness_for_throne_score") if isinstance(gate_summary, dict) else None,
    })
    if not isinstance(gate_summary, dict) or gate_summary.get("throne_self_validation_score") != 0.0:
        errors.append("Throne self-validation score must be zero")

    add(checks, "truth_state_is_not_self_proven", isinstance(gate_summary, dict) and gate_summary.get("crown_order_truth_state") == "CROWN_ORDER_ISSUED_NOT_THRONE_SELF_PROVEN", {"truth_state": gate_summary.get("crown_order_truth_state") if isinstance(gate_summary, dict) else None})
    if not isinstance(gate_summary, dict) or gate_summary.get("crown_order_truth_state") != "CROWN_ORDER_ISSUED_NOT_THRONE_SELF_PROVEN":
        errors.append("truth state does not deny Throne self-proof")

    add(checks, "astronomicon_assembled_remains_zero", isinstance(gate_summary, dict) and gate_summary.get("astronomicon_assembled_score") == 0.0, {"assembled": gate_summary.get("astronomicon_assembled_score") if isinstance(gate_summary, dict) else None})
    if not isinstance(gate_summary, dict) or gate_summary.get("astronomicon_assembled_score") != 0.0:
        errors.append("Astronomicon assembled score must remain zero")

    not_claimed = gate_summary.get("not_claimed", []) if isinstance(gate_summary, dict) else []
    add(checks, "not_claimed_includes_throne_self_validation", "Throne self-validation" in not_claimed, {"not_claimed": not_claimed})
    if "Throne self-validation" not in not_claimed:
        errors.append("not_claimed missing Throne self-validation")

    gates = gate_summary.get("gates", []) if isinstance(gate_summary, dict) else []
    failed = [g for g in gates if g.get("status") != "PASS"]
    add(checks, "all_evidence_crown_gates_still_pass", not failed and len(gates) >= 10, {"gate_count": len(gates), "failed": failed})
    if failed or len(gates) < 10:
        errors.append("not all Crown evidence gates passed")

    verdict = "PASS_THRONE_ASTRONOMICON_ANTI_SELF_DECEPTION_READY" if not errors else "FAIL_THRONE_ASTRONOMICON_ANTI_SELF_DECEPTION"
    generated = utc()
    summary = {
        "summary_id": "throne.astronomicon_anti_self_deception_validation_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "gate_summary": "ORGANS/THRONE/REPORTS/THRONE_ASTRONOMICON_STRICT_GATES_SUMMARY_V0_1.json",
        "not_claimed": ["Throne self-validation", "global organ assembled", "Core v1 ready", "Great Nine complete"]
    }
    receipt = {
        "receipt_id": "receipt.throne.astronomicon_anti_self_deception_validation.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Throne Crown order is separated from forbidden Throne self-validation."
    }

    for rel in [SUMMARY, RECEIPT, REPORT]:
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / SUMMARY).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# THRONE ASTRONOMICON ANTI SELF-DECEPTION VALIDATION REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

The Throne strict gate now distinguishes local Crown order from forbidden Throne self-validation.

A local Crown order can be issued for Astronomicon while `throne_self_validation_score` remains `0`.

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}

## Not claimed

- Throne self-validation
- global organ assembled
- Core v1 ready
- Great Nine complete
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
