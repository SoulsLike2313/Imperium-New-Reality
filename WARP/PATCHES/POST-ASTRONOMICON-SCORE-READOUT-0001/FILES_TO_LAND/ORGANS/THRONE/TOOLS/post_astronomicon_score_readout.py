#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

PATCH_ID = "POST-ASTRONOMICON-SCORE-READOUT-0001"
MATRIX = Path("ORGANS/THRONE/MATRICES/POST_ASTRONOMICON_SCORE_READOUT_MATRIX_V0_1.json")
SUMMARY = Path("ORGANS/THRONE/REPORTS/POST_ASTRONOMICON_SCORE_READOUT_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/THRONE/REPORTS/POST_ASTRONOMICON_SCORE_READOUT_REPORT_V0_1.md")
RECEIPT = Path("ORGANS/THRONE/RECEIPTS/post_astronomicon_score_readout_receipt.json")

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def git_head(repo: Path) -> str:
    try:
        p = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(repo), capture_output=True, text=True, timeout=15)
        return p.stdout.strip() if p.returncode == 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"

def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None

def write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def pick(data: Dict[str, Any], *names: str) -> Any:
    cur = data
    for n in names:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(n)
    return cur

def delta(current: Any, base: Any) -> Any:
    if isinstance(current, (int, float)) and isinstance(base, (int, float)):
        return round(float(current) - float(base), 2)
    return None

def load_required(repo: Path, matrix: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    out = {}
    errors = []
    for key, rel in matrix.get("required_current_inputs", {}).items():
        p = repo / rel
        exists = p.exists()
        data = load_json(p) if exists and p.suffix.lower() == ".json" else None
        out[key] = {"path": rel, "exists": exists, "data": data}
        if not exists:
            errors.append(f"missing required input {key}: {rel}")
        elif data is None and p.suffix.lower() == ".json":
            errors.append(f"invalid json input {key}: {rel}")
    return out, errors

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    matrix = load_json(repo / MATRIX)
    errors: List[str] = []
    warnings: List[str] = []
    if not isinstance(matrix, dict):
        matrix = {}
        errors.append("score readout matrix missing or invalid")

    inputs, input_errors = load_required(repo, matrix)
    errors.extend(input_errors)

    baseline = matrix.get("baseline", {})
    pop_receipt = pick(inputs, "population_receipt", "data") or {}
    gap = pick(inputs, "throne_gap_receipt", "data") or {}
    stage_summary = pick(inputs, "stage_scoring_summary", "data") or {}
    stage_receipt = pick(inputs, "stage_scoring_receipt", "data") or {}
    astro = pick(inputs, "astronomicon_hardening", "data") or {}
    custodes = pick(inputs, "custodes_audit", "data") or {}
    throne = pick(inputs, "throne_crown", "data") or {}

    stage_scores = {}
    if isinstance(stage_summary.get("scores"), dict):
        stage_scores = stage_summary.get("scores")
    elif isinstance(stage_receipt.get("scores"), dict):
        stage_scores = stage_receipt.get("scores")

    current_scores = {
        "population_total": pop_receipt.get("population_total"),
        "tracked_file_count": pop_receipt.get("tracked_file_count"),
        "owner_coverage_score": pop_receipt.get("owner_coverage_score"),
        "classification_coverage_score": pop_receipt.get("classification_coverage_score"),
        "status_coverage_score": pop_receipt.get("status_coverage_score"),

        "core_readiness_score": gap.get("core_readiness_score"),
        "throne_readiness_score": gap.get("throne_readiness_score"),
        "great_nine_readiness_score": gap.get("great_nine_readiness_score"),
        "lowest_organ_readiness_score": gap.get("lowest_organ_readiness_score"),
        "great_nine_profile_baseline_score": gap.get("great_nine_profile_baseline_score"),
        "great_nine_structural_score": gap.get("great_nine_structural_score"),
        "great_nine_operational_score": gap.get("great_nine_operational_score"),
        "great_nine_trust_score": gap.get("great_nine_trust_score"),

        "profile_baseline_score": stage_scores.get("profile_baseline_score"),
        "duty_defined_score": stage_scores.get("duty_defined_score"),
        "assembly_target_defined_score": stage_scores.get("assembly_target_defined_score"),
        "red_team_score": stage_scores.get("red_team_score"),
        "blue_team_score": stage_scores.get("blue_team_score"),
        "organ_truth_maturity_score": stage_scores.get("organ_truth_maturity_score"),
        "organ_assembled_score": stage_scores.get("organ_assembled_score"),

        "astronomicon_red_local_hardening_score": astro.get("red_local_hardening_score"),
        "astronomicon_blue_local_hardening_score": astro.get("blue_local_hardening_score"),
        "custodes_astronomicon_validation_score": custodes.get("custodes_validation_score"),
        "custodes_astronomicon_indictment_count": len(custodes.get("indictments", [])) if isinstance(custodes.get("indictments"), list) else None,
        "astronomicon_crown_order_score": throne.get("astronomicon_crown_order_score"),
        "astronomicon_crown_gate_score": throne.get("astronomicon_crown_gate_score"),
        "astronomicon_throne_confirmed_score": throne.get("astronomicon_throne_confirmed_score"),
        "throne_self_validation_score": throne.get("throne_self_validation_score"),
        "external_witness_for_throne_score": throne.get("external_witness_for_throne_score"),
        "astronomicon_assembled_score": throne.get("astronomicon_assembled_score"),
    }

    deltas = {k: delta(v, baseline.get(k)) for k, v in current_scores.items() if k in baseline}

    chain_ok = (
        astro.get("red_local_hardening_score") == 100.0 and
        astro.get("blue_local_hardening_score") == 100.0 and
        custodes.get("custodes_validation_score") == 100.0 and
        (len(custodes.get("indictments", [])) == 0 if isinstance(custodes.get("indictments"), list) else False) and
        throne.get("astronomicon_crown_order_score") == 100.0 and
        throne.get("throne_self_validation_score") == 0.0 and
        throne.get("astronomicon_assembled_score") == 0.0
    )

    if not chain_ok:
        warnings.append("Astronomicon/Custodes/Throne local chain is not fully clean according to readout rules.")

    stage_integrates_local_crown = (
        stage_scores.get("red_team_score", 0) and stage_scores.get("red_team_score", 0) > 0
    ) or (
        stage_scores.get("blue_team_score", 0) and stage_scores.get("blue_team_score", 0) > 0
    )
    integration_note = (
        "Global stage scorer appears to reflect some Red/Blue progress."
        if stage_integrates_local_crown else
        "Global stage scorer still appears not to consume the local Astronomicon Crown order; this is expected until a later stage-score integration patch."
    )

    verdict = "PASS_POST_ASTRONOMICON_SCORE_READOUT_READY" if not errors else "FAIL_POST_ASTRONOMICON_SCORE_READOUT"
    generated = utc()
    summary = {
        "summary_id": "throne.post_astronomicon_score_readout_summary.v0_1",
        "task_id": PATCH_ID,
        "validator_id": "post_astronomicon_score_readout.v0_1",
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "baseline": baseline,
        "current_scores": current_scores,
        "deltas_vs_baseline": deltas,
        "astronomicon_chain_ok": chain_ok,
        "stage_integrates_local_crown": bool(stage_integrates_local_crown),
        "integration_note": integration_note,
        "input_paths": {k: v.get("path") for k, v in inputs.items()},
        "errors": errors,
        "warnings": warnings,
        "not_claimed": matrix.get("not_claimed", [])
    }
    receipt = {
        "receipt_id": "receipt.throne.post_astronomicon_score_readout.v0_1",
        "task_id": PATCH_ID,
        "validator_id": "post_astronomicon_score_readout.v0_1",
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "errors": errors,
        "warnings": warnings,
        "meaning": "Current score readout after Astronomicon -> Custodes -> Throne cycle."
    }

    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    def row(label: str, key: str) -> str:
        cur = current_scores.get(key)
        base = baseline.get(key)
        d = deltas.get(key)
        if base is None:
            return f"| {label} | `{cur}` | — | — |"
        return f"| {label} | `{cur}` | `{base}` | `{d}` |"

    lines = [
        "# POST ASTRONOMICON SCORE READOUT V0.1",
        "",
        f"verdict: `{verdict}`  ",
        f"generated_at_utc: `{generated}`  ",
        f"repo_head: `{git_head(repo)}`",
        "",
        "## Meaning",
        "",
        "This report reads the current measured state after the Astronomicon local Red/Blue hardening, Custodes prosecutor validation, and Throne anti-self-deception Crown order.",
        "",
        "It does not claim Great Nine assembled, Core v1 ready, or visual work resumed.",
        "",
        "## Astronomicon local chain",
        "",
        f"- Astronomicon red local hardening: `{current_scores.get('astronomicon_red_local_hardening_score')}`",
        f"- Astronomicon blue local hardening: `{current_scores.get('astronomicon_blue_local_hardening_score')}`",
        f"- Custodes validation score: `{current_scores.get('custodes_astronomicon_validation_score')}`",
        f"- Custodes indictments: `{current_scores.get('custodes_astronomicon_indictment_count')}`",
        f"- Astronomicon Crown order score: `{current_scores.get('astronomicon_crown_order_score')}`",
        f"- Throne self-validation score: `{current_scores.get('throne_self_validation_score')}`",
        f"- Astronomicon assembled score: `{current_scores.get('astronomicon_assembled_score')}`",
        f"- Chain OK: `{chain_ok}`",
        "",
        "## Global measured scores",
        "",
        "| Metric | Current | Baseline | Delta |",
        "|---|---:|---:|---:|",
        row("population_total", "population_total"),
        row("tracked_file_count", "tracked_file_count"),
        row("core_readiness_score", "core_readiness_score"),
        row("throne_readiness_score", "throne_readiness_score"),
        row("great_nine_readiness_score", "great_nine_readiness_score"),
        row("lowest_organ_readiness_score", "lowest_organ_readiness_score"),
        row("great_nine_operational_score", "great_nine_operational_score"),
        row("great_nine_trust_score", "great_nine_trust_score"),
        row("red_team_score", "red_team_score"),
        row("blue_team_score", "blue_team_score"),
        row("organ_truth_maturity_score", "organ_truth_maturity_score"),
        row("organ_assembled_score", "organ_assembled_score"),
        "",
        "## Integration note",
        "",
        integration_note,
        "",
        "## Warnings",
        "",
    ]
    lines += [f"- {w}" for w in warnings] if warnings else ["- none"]
    lines += ["", "## Errors", ""]
    lines += [f"- {e}" for e in errors] if errors else ["- none"]
    lines += ["", "## Not claimed", ""]
    lines += [f"- {x}" for x in matrix.get("not_claimed", [])]
    (repo / REPORT).parent.mkdir(parents=True, exist_ok=True)
    (repo / REPORT).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "task_id": PATCH_ID,
        "validator_id": "post_astronomicon_score_readout.v0_1",
        "verdict": verdict,
        "astronomicon_chain_ok": chain_ok,
        "stage_integrates_local_crown": bool(stage_integrates_local_crown),
        "current_scores": current_scores,
        "deltas_vs_baseline": deltas,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "receipt": RECEIPT.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
