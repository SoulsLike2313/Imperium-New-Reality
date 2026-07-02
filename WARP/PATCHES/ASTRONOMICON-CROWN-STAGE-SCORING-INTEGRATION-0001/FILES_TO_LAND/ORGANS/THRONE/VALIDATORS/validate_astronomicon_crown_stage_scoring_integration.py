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

TASK_ID = "ASTRONOMICON-CROWN-STAGE-SCORING-INTEGRATION-0001"
VALIDATOR_ID = "astronomicon_crown_stage_scoring_integration_validator.v0_1"

INTEGRATION_TOOL = Path("ORGANS/THRONE/TOOLS/astronomicon_crown_stage_scoring_integration.py")
READOUT_TOOL = Path("ORGANS/THRONE/TOOLS/post_astronomicon_score_readout.py")
MATRIX = Path("ORGANS/THRONE/MATRICES/ASTRONOMICON_CROWN_STAGE_SCORING_INTEGRATION_MATRIX_V0_1.json")

RECEIPT = Path("ORGANS/THRONE/RECEIPTS/astronomicon_crown_stage_scoring_integration_validation_receipt.json")
SUMMARY = Path("ORGANS/THRONE/REPORTS/ASTRONOMICON_CROWN_STAGE_SCORING_INTEGRATION_VALIDATION_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/THRONE/REPORTS/ASTRONOMICON_CROWN_STAGE_SCORING_INTEGRATION_VALIDATION_REPORT_V0_1.md")

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

def run_py(repo: Path, script: Path) -> Tuple[int, str, str]:
    p = subprocess.run([sys.executable, str(repo / script), "--repo-root", str(repo)], cwd=str(repo), capture_output=True, text=True, timeout=180, encoding="utf-8", errors="replace")
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

    for rel in [INTEGRATION_TOOL, READOUT_TOOL, MATRIX]:
        ok = (repo / rel).is_file()
        add(checks, f"{rel.name}_exists", ok, {"path": rel.as_posix()})
        if not ok:
            errors.append(f"missing {rel.as_posix()}")

    matrix, matrix_err = load_json(repo / MATRIX) if (repo / MATRIX).is_file() else ({}, "missing")
    add(checks, "integration_matrix_parses", matrix_err is None, {"error": matrix_err})
    if matrix_err:
        errors.append("integration matrix parse failed")

    code, out, err = run_py(repo, INTEGRATION_TOOL)
    add(checks, "integration_tool_runs", code == 0, {"exit_code": code, "stdout_tail": out[-2000:], "stderr_tail": err[-1200:]})
    if code != 0:
        errors.append("integration tool failed")

    integ, integ_err = load_json(repo / "ORGANS/THRONE/REPORTS/ASTRONOMICON_CROWN_STAGE_SCORING_INTEGRATION_SUMMARY_V0_1.json")
    add(checks, "integration_summary_parses", integ_err is None, {"error": integ_err})
    if integ_err:
        errors.append("integration summary parse failed")
        integ = {}

    scores = integ.get("crown_aware_scores", {}) if isinstance(integ, dict) else {}
    add(checks, "one_organ_weight_integrated", (
        integ.get("integrated_organ_count") == 1 and
        integ.get("per_organ_weight") == 10.0 and
        scores.get("red_team_score") == 10.0 and
        scores.get("blue_team_score") == 10.0
    ), {
        "integrated_organ_count": integ.get("integrated_organ_count") if isinstance(integ, dict) else None,
        "per_organ_weight": integ.get("per_organ_weight") if isinstance(integ, dict) else None,
        "red": scores.get("red_team_score"),
        "blue": scores.get("blue_team_score")
    })
    if not isinstance(integ, dict) or scores.get("red_team_score") != 10.0 or scores.get("blue_team_score") != 10.0:
        errors.append("one-organ red/blue weight not integrated")

    add(checks, "assembled_and_self_validation_remain_zero", (
        scores.get("organ_assembled_score") == 0.0 and
        integ.get("conditions", {}).get("throne_self_validation_score") == 0.0 and
        integ.get("conditions", {}).get("astronomicon_assembled_score") == 0.0
    ), {
        "organ_assembled_score": scores.get("organ_assembled_score"),
        "conditions": integ.get("conditions") if isinstance(integ, dict) else None
    })
    if scores.get("organ_assembled_score") != 0.0:
        errors.append("organ assembled score must remain zero")

    code, out, err = run_py(repo, READOUT_TOOL)
    add(checks, "post_readout_tool_runs_after_integration", code == 0, {"exit_code": code, "stdout_tail": out[-2000:], "stderr_tail": err[-1200:]})
    if code != 0:
        errors.append("post readout tool failed after integration")

    readout, readout_err = load_json(repo / "ORGANS/THRONE/REPORTS/POST_ASTRONOMICON_SCORE_READOUT_SUMMARY_V0_1.json")
    add(checks, "post_readout_summary_parses", readout_err is None, {"error": readout_err})
    if readout_err:
        errors.append("post readout summary parse failed")
        readout = {}

    add(checks, "post_readout_reports_crown_overlay_integration", (
        isinstance(readout, dict) and
        readout.get("stage_integrates_local_crown") is True and
        readout.get("stage_integration_mode") == "CROWN_AWARE_OVERLAY" and
        readout.get("crown_aware_scores", {}).get("red_team_score") == 10.0 and
        readout.get("crown_aware_scores", {}).get("blue_team_score") == 10.0
    ), {
        "stage_integrates_local_crown": readout.get("stage_integrates_local_crown") if isinstance(readout, dict) else None,
        "stage_integration_mode": readout.get("stage_integration_mode") if isinstance(readout, dict) else None,
        "crown_aware_scores": readout.get("crown_aware_scores") if isinstance(readout, dict) else None,
    })
    if not isinstance(readout, dict) or readout.get("stage_integrates_local_crown") is not True:
        errors.append("post readout does not report crown overlay integration")

    verdict = "PASS_ASTRONOMICON_CROWN_STAGE_SCORING_INTEGRATION_READY" if not errors else "FAIL_ASTRONOMICON_CROWN_STAGE_SCORING_INTEGRATION"
    generated = utc()
    summary = {
        "summary_id": "throne.astronomicon_crown_stage_scoring_integration_validation_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "not_claimed": ["Great Nine assembled", "Core v1 ready", "Astronomicon assembled", "Throne self-validation"]
    }
    receipt = {
        "receipt_id": "receipt.throne.astronomicon_crown_stage_scoring_integration_validation.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Validated Astronomicon Crown stage scoring integration overlay."
    }

    for rel in [SUMMARY, RECEIPT, REPORT]:
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / SUMMARY).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# ASTRONOMICON CROWN STAGE SCORING INTEGRATION VALIDATION REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

Astronomicon's local Crown order is integrated into a crown-aware global stage overlay as one confirmed organ out of ten.

This is not organ assembled and not Great Nine assembled.

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
