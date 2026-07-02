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

TASK_ID = "POST-ASTRONOMICON-SCORE-READOUT-0001"
VALIDATOR_ID = "post_astronomicon_score_readout_validator.v0_1"

TOOL = Path("ORGANS/THRONE/TOOLS/post_astronomicon_score_readout.py")
MATRIX = Path("ORGANS/THRONE/MATRICES/POST_ASTRONOMICON_SCORE_READOUT_MATRIX_V0_1.json")
RECEIPT = Path("ORGANS/THRONE/RECEIPTS/post_astronomicon_score_readout_validation_receipt.json")
SUMMARY = Path("ORGANS/THRONE/REPORTS/POST_ASTRONOMICON_SCORE_READOUT_VALIDATION_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/THRONE/REPORTS/POST_ASTRONOMICON_SCORE_READOUT_VALIDATION_REPORT_V0_1.md")

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
    add(checks, "score_readout_matrix_parses", matrix_err is None, {"error": matrix_err})
    if matrix_err:
        errors.append("score readout matrix parse failed")
        matrix = {}

    p = subprocess.run([sys.executable, str(repo / TOOL), "--repo-root", str(repo)], cwd=str(repo), capture_output=True, text=True, timeout=180, encoding="utf-8", errors="replace")
    add(checks, "score_readout_tool_runs", p.returncode == 0, {"exit_code": p.returncode, "stdout_tail": p.stdout[-2000:], "stderr_tail": p.stderr[-1200:]})
    if p.returncode != 0:
        errors.append("score readout tool failed")

    readout, readout_err = load_json(repo / "ORGANS/THRONE/REPORTS/POST_ASTRONOMICON_SCORE_READOUT_SUMMARY_V0_1.json")
    add(checks, "score_readout_summary_parses", readout_err is None, {"error": readout_err})
    if readout_err:
        errors.append("score readout summary parse failed")
        readout = {}

    current = readout.get("current_scores", {}) if isinstance(readout, dict) else {}

    add(checks, "astronomicon_chain_is_clean", isinstance(readout, dict) and readout.get("astronomicon_chain_ok") is True, {
        "astronomicon_chain_ok": readout.get("astronomicon_chain_ok") if isinstance(readout, dict) else None
    })
    if not isinstance(readout, dict) or readout.get("astronomicon_chain_ok") is not True:
        errors.append("Astronomicon chain is not clean")

    add(checks, "throne_self_validation_stays_zero", current.get("throne_self_validation_score") == 0.0, {"score": current.get("throne_self_validation_score")})
    if current.get("throne_self_validation_score") != 0.0:
        errors.append("Throne self-validation score must remain zero")

    add(checks, "astronomicon_assembled_stays_zero", current.get("astronomicon_assembled_score") == 0.0, {"score": current.get("astronomicon_assembled_score")})
    if current.get("astronomicon_assembled_score") != 0.0:
        errors.append("Astronomicon assembled score must remain zero")

    add(checks, "readout_contains_global_scores", all(k in current for k in [
        "core_readiness_score", "great_nine_readiness_score", "organ_truth_maturity_score", "organ_assembled_score"
    ]), {"current_keys": sorted(current.keys())})
    if not all(k in current for k in ["core_readiness_score", "great_nine_readiness_score", "organ_truth_maturity_score", "organ_assembled_score"]):
        errors.append("readout missing global scores")

    verdict = "PASS_POST_ASTRONOMICON_SCORE_READOUT_READY" if not errors else "FAIL_POST_ASTRONOMICON_SCORE_READOUT"
    generated = utc()
    summary = {
        "summary_id": "throne.post_astronomicon_score_readout_validation_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "readout_summary": "ORGANS/THRONE/REPORTS/POST_ASTRONOMICON_SCORE_READOUT_SUMMARY_V0_1.json",
        "not_claimed": ["Great Nine assembled", "Core v1 ready", "visual work resumed"]
    }
    receipt = {
        "receipt_id": "receipt.throne.post_astronomicon_score_readout_validation.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Validated score readout after Astronomicon chain."
    }

    for rel in [SUMMARY, RECEIPT, REPORT]:
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / SUMMARY).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# POST ASTRONOMICON SCORE READOUT VALIDATION REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

This validator confirms that the post-Astronomicon score readout exists, parses, and preserves core honesty boundaries.

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
