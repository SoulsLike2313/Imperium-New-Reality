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

TASK_ID = "THRONE-ASTRONOMICON-STRICT-GATES-0001"
VALIDATOR_ID = "throne_astronomicon_strict_gates_validator.v0_1"

TOOL = Path("ORGANS/THRONE/TOOLS/throne_astronomicon_strict_gate.py")
MATRIX = Path("ORGANS/THRONE/MATRICES/THRONE_ASTRONOMICON_STRICT_GATES_MATRIX_V0_1.json")
RECEIPT = Path("ORGANS/THRONE/RECEIPTS/throne_astronomicon_strict_gates_validation_receipt.json")
SUMMARY = Path("ORGANS/THRONE/REPORTS/THRONE_ASTRONOMICON_STRICT_GATES_VALIDATION_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/THRONE/REPORTS/THRONE_ASTRONOMICON_STRICT_GATES_VALIDATION_REPORT_V0_1.md")

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

def run_py(repo: Path, script: Path, args: List[str]) -> Tuple[int, str, str]:
    p = subprocess.run([sys.executable, str(repo / script)] + args, cwd=str(repo), capture_output=True, text=True, timeout=180)
    return p.returncode, p.stdout, p.stderr

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
    add(checks, "strict_gate_matrix_parses", matrix_err is None, {"error": matrix_err})
    if matrix_err:
        errors.append("strict gate matrix parse failed")
        matrix = {}

    add(checks, "matrix_has_hard_forbidden_claims", len(matrix.get("hard_forbidden", [])) >= 5 if isinstance(matrix, dict) else False, {"hard_forbidden": matrix.get("hard_forbidden", []) if isinstance(matrix, dict) else []})
    if not isinstance(matrix, dict) or len(matrix.get("hard_forbidden", [])) < 5:
        errors.append("matrix hard_forbidden incomplete")

    code, out, err = run_py(repo, TOOL, ["--repo-root", str(repo)])
    add(checks, "throne_strict_gate_tool_runs", code == 0, {"exit_code": code, "stderr_tail": err[-1200:], "stdout_tail": out[-1200:]})
    if code != 0:
        errors.append("Throne Astronomicon strict gate tool failed")

    gate_summary, gate_err = load_json(repo / "ORGANS/THRONE/REPORTS/THRONE_ASTRONOMICON_STRICT_GATES_SUMMARY_V0_1.json")
    add(checks, "throne_strict_gate_summary_parses", gate_err is None, {"error": gate_err})
    if gate_err:
        errors.append("Throne strict gate summary parse failed")
        gate_summary = {}

    add(checks, "throne_strict_gate_verdict_pass", isinstance(gate_summary, dict) and str(gate_summary.get("verdict", "")).startswith("PASS"), {"verdict": gate_summary.get("verdict") if isinstance(gate_summary, dict) else None})
    if not isinstance(gate_summary, dict) or not str(gate_summary.get("verdict", "")).startswith("PASS"):
        errors.append("Throne strict gate verdict is not PASS")

    gates = gate_summary.get("gates", []) if isinstance(gate_summary, dict) else []
    failed = [g for g in gates if g.get("status") != "PASS"]
    add(checks, "all_crown_gates_pass", not failed and len(gates) >= 10, {"gate_count": len(gates), "failed": failed})
    if failed or len(gates) < 10:
        errors.append("not all Crown gates passed")

    add(checks, "astronomicon_crown_scores_are_strict", (
        gate_summary.get("astronomicon_crown_gate_score") == 100.0 and
        gate_summary.get("astronomicon_red_team_crown_score") == 100.0 and
        gate_summary.get("astronomicon_blue_team_crown_score") == 100.0 and
        gate_summary.get("astronomicon_throne_confirmed_score") == 100.0
    ), {
        "crown": gate_summary.get("astronomicon_crown_gate_score") if isinstance(gate_summary, dict) else None,
        "red": gate_summary.get("astronomicon_red_team_crown_score") if isinstance(gate_summary, dict) else None,
        "blue": gate_summary.get("astronomicon_blue_team_crown_score") if isinstance(gate_summary, dict) else None,
        "confirmed": gate_summary.get("astronomicon_throne_confirmed_score") if isinstance(gate_summary, dict) else None,
    })
    if not isinstance(gate_summary, dict) or gate_summary.get("astronomicon_throne_confirmed_score") != 100.0:
        errors.append("Astronomicon Throne confirmation score not strict 100")

    add(checks, "astronomicon_assembled_score_remains_zero", isinstance(gate_summary, dict) and gate_summary.get("astronomicon_assembled_score") == 0.0, {"assembled": gate_summary.get("astronomicon_assembled_score") if isinstance(gate_summary, dict) else None})
    if not isinstance(gate_summary, dict) or gate_summary.get("astronomicon_assembled_score") != 0.0:
        errors.append("Astronomicon assembled score must remain zero")

    add(checks, "custodes_score_was_required_100", isinstance(gate_summary, dict) and gate_summary.get("custodes_validation_score") == 100.0, {"custodes": gate_summary.get("custodes_validation_score") if isinstance(gate_summary, dict) else None})
    if not isinstance(gate_summary, dict) or gate_summary.get("custodes_validation_score") != 100.0:
        errors.append("Custodes score was not exact 100")

    verdict = "PASS_THRONE_ASTRONOMICON_STRICT_GATES_READY" if not errors else "FAIL_THRONE_ASTRONOMICON_STRICT_GATES"
    generated = utc()
    summary = {
        "summary_id": "throne.astronomicon_strict_gates_validation_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "gate_summary": "ORGANS/THRONE/REPORTS/THRONE_ASTRONOMICON_STRICT_GATES_SUMMARY_V0_1.json",
        "not_claimed": ["global organ assembled", "Core v1 ready", "Great Nine complete"]
    }
    receipt = {
        "receipt_id": "receipt.throne.astronomicon_strict_gates_validation.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Throne strict Crown gates validated Astronomicon after Custodes prosecution."
    }

    for rel in [SUMMARY, RECEIPT, REPORT]:
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / SUMMARY).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# THRONE ASTRONOMICON STRICT GATES VALIDATION REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

Throne validated the Astronomicon strict gate tool and confirmed that Crown scores are strict, evidence-bound, and non-global.

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}

## Not claimed

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
