#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

PATCH_ID = "POST-ASTRONOMICON-SCORE-READOUT-GAP-FIELDS-HOTFIX-0001"
MATRIX_V2 = Path("ORGANS/THRONE/MATRICES/POST_ASTRONOMICON_SCORE_READOUT_GAP_FIELDS_HOTFIX_MATRIX_V0_2.json")
MATRIX_V1 = Path("ORGANS/THRONE/MATRICES/POST_ASTRONOMICON_SCORE_READOUT_MATRIX_V0_1.json")
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

def deep_find(data: Any, key: str) -> Any:
    if isinstance(data, dict):
        if key in data:
            return data[key]
        # Common wrapper names first.
        for preferred in ["scores", "current_scores", "summary", "receipt", "result", "data", "payload"]:
            if preferred in data:
                found = deep_find(data[preferred], key)
                if found is not None:
                    return found
        for v in data.values():
            found = deep_find(v, key)
            if found is not None:
                return found
    elif isinstance(data, list):
        for item in data:
            found = deep_find(item, key)
            if found is not None:
                return found
    return None

def first_found(sources: List[Any], key: str) -> Any:
    for src in sources:
        found = deep_find(src, key)
        if found is not None:
            return found
    return None

def as_num(v: Any) -> Any:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return float(v) if isinstance(v, float) else v
    try:
        if isinstance(v, str) and v.strip() != "":
            f = float(v.replace(",", "."))
            return int(f) if f.is_integer() else f
    except Exception:
        return v
    return v

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

    matrix = load_json(repo / MATRIX_V2)
    if not isinstance(matrix, dict):
        matrix = load_json(repo / MATRIX_V1)
    errors: List[str] = []
    warnings: List[str] = []
    if not isinstance(matrix, dict):
        matrix = {}
        errors.append("score readout matrix missing or invalid")

    inputs, input_errors = load_required(repo, matrix)
    errors.extend(input_errors)

    baseline = matrix.get("baseline", {})
    source_objects = [v.get("data") for v in inputs.values() if isinstance(v.get("data"), dict)]

    stage_summary = inputs.get("stage_scoring_summary", {}).get("data") or {}
    stage_receipt = inputs.get("stage_scoring_receipt", {}).get("data") or {}
    astro = inputs.get("astronomicon_hardening", {}).get("data") or {}
    custodes = inputs.get("custodes_audit", {}).get("data") or {}
    throne = inputs.get("throne_crown", {}).get("data") or {}

    def f(key: str) -> Any:
        return as_num(first_found(source_objects, key))

    current_scores = {
        "population_total": f("population_total"),
        "tracked_file_count": f("tracked_file_count"),
        "owner_coverage_score": f("owner_coverage_score"),
        "classification_coverage_score": f("classification_coverage_score"),
        "status_coverage_score": f("status_coverage_score"),

        "core_readiness_score": f("core_readiness_score"),
        "throne_readiness_score": f("throne_readiness_score"),
        "great_nine_readiness_score": f("great_nine_readiness_score"),
        "lowest_organ_readiness_score": f("lowest_organ_readiness_score"),
        "great_nine_profile_baseline_score": f("great_nine_profile_baseline_score"),
        "great_nine_structural_score": f("great_nine_structural_score"),
        "great_nine_operational_score": f("great_nine_operational_score"),
        "great_nine_trust_score": f("great_nine_trust_score"),

        "profile_baseline_score": f("profile_baseline_score"),
        "duty_defined_score": f("duty_defined_score"),
        "assembly_target_defined_score": f("assembly_target_defined_score"),
        "red_team_score": f("red_team_score"),
        "blue_team_score": f("blue_team_score"),
        "organ_truth_maturity_score": f("organ_truth_maturity_score"),
        "organ_assembled_score": f("organ_assembled_score"),

        "astronomicon_red_local_hardening_score": as_num(astro.get("red_local_hardening_score")),
        "astronomicon_blue_local_hardening_score": as_num(astro.get("blue_local_hardening_score")),
        "custodes_astronomicon_validation_score": as_num(custodes.get("custodes_validation_score")),
        "custodes_astronomicon_indictment_count": len(custodes.get("indictments", [])) if isinstance(custodes.get("indictments"), list) else None,
        "astronomicon_crown_order_score": as_num(throne.get("astronomicon_crown_order_score")),
        "astronomicon_crown_gate_score": as_num(throne.get("astronomicon_crown_gate_score")),
        "astronomicon_throne_confirmed_score": as_num(throne.get("astronomicon_throne_confirmed_score")),
        "throne_self_validation_score": as_num(throne.get("throne_self_validation_score")),
        "external_witness_for_throne_score": as_num(throne.get("external_witness_for_throne_score")),
        "astronomicon_assembled_score": as_num(throne.get("astronomicon_assembled_score")),
    }

    required_non_null = matrix.get("required_non_null_current_scores", [])
    missing_scores = [k for k in required_non_null if current_scores.get(k) is None]
    if missing_scores:
        errors.append("missing required current score fields: " + ", ".join(missing_scores))

    deltas = {k: delta(v, baseline.get(k)) for k, v in current_scores.items() if k in baseline}

    chain_ok = (
        current_scores.get("astronomicon_red_local_hardening_score") == 100.0 and
        current_scores.get("astronomicon_blue_local_hardening_score") == 100.0 and
        current_scores.get("custodes_astronomicon_validation_score") == 100.0 and
        current_scores.get("custodes_astronomicon_indictment_count") == 0 and
        current_scores.get("astronomicon_crown_order_score") == 100.0 and
        current_scores.get("throne_self_validation_score") == 0.0 and
        current_scores.get("astronomicon_assembled_score") == 0.0
    )

    if not chain_ok:
        warnings.append("Astronomicon/Custodes/Throne local chain is not fully clean according to readout rules.")

    stage_integrates_local_crown = (
        isinstance(current_scores.get("red_team_score"), (int, float)) and current_scores.get("red_team_score") > 0
    ) or (
        isinstance(current_scores.get("blue_team_score"), (int, float)) and current_scores.get("blue_team_score") > 0
    )

    integration_note = (
        "Global stage scorer appears to reflect some Red/Blue progress."
        if stage_integrates_local_crown else
        "Global stage scorer still does not consume the local Astronomicon Crown order; next required work is explicit stage-score integration."
    )

    verdict = "PASS_POST_ASTRONOMICON_SCORE_READOUT_READY" if not errors else "FAIL_POST_ASTRONOMICON_SCORE_READOUT"
    generated = utc()
    summary = {
        "summary_id": "throne.post_astronomicon_score_readout_summary.v0_2_gap_fields_hotfix",
        "task_id": PATCH_ID,
        "validator_id": "post_astronomicon_score_readout.v0_2_gap_fields_hotfix",
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "baseline": baseline,
        "current_scores": current_scores,
        "deltas_vs_baseline": deltas,
        "astronomicon_chain_ok": chain_ok,
        "stage_integrates_local_crown": bool(stage_integrates_local_crown),
        "integration_note": integration_note,
        "missing_required_current_scores": missing_scores,
        "input_paths": {k: v.get("path") for k, v in inputs.items()},
        "errors": errors,
        "warnings": warnings,
        "not_claimed": matrix.get("not_claimed", [])
    }
    receipt = {
        "receipt_id": "receipt.throne.post_astronomicon_score_readout.v0_2_gap_fields_hotfix",
        "task_id": PATCH_ID,
        "validator_id": "post_astronomicon_score_readout.v0_2_gap_fields_hotfix",
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "errors": errors,
        "warnings": warnings,
        "meaning": "Current score readout after Astronomicon cycle with hardened non-null gap field extraction."
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
        "# POST ASTRONOMICON SCORE READOUT V0.2 — GAP FIELDS HOTFIX",
        "",
        f"verdict: `{verdict}`  ",
        f"generated_at_utc: `{generated}`  ",
        f"repo_head: `{git_head(repo)}`",
        "",
        "## Meaning",
        "",
        "This report reads current measured state after the Astronomicon local Red/Blue hardening, Custodes prosecutor validation, and Throne anti-self-deception Crown order.",
        "",
        "This hotfix forbids fake-green readout where current core/great-nine fields silently become `None`.",
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
        "## Missing required current scores",
        "",
    ]
    lines += [f"- {m}" for m in missing_scores] if missing_scores else ["- none"]
    lines += ["", "## Warnings", ""]
    lines += [f"- {w}" for w in warnings] if warnings else ["- none"]
    lines += ["", "## Errors", ""]
    lines += [f"- {e}" for e in errors] if errors else ["- none"]
    lines += ["", "## Not claimed", ""]
    lines += [f"- {x}" for x in matrix.get("not_claimed", [])]
    (repo / REPORT).parent.mkdir(parents=True, exist_ok=True)
    (repo / REPORT).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "task_id": PATCH_ID,
        "validator_id": "post_astronomicon_score_readout.v0_2_gap_fields_hotfix",
        "verdict": verdict,
        "astronomicon_chain_ok": chain_ok,
        "stage_integrates_local_crown": bool(stage_integrates_local_crown),
        "current_scores": current_scores,
        "deltas_vs_baseline": deltas,
        "missing_required_current_scores": missing_scores,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "receipt": RECEIPT.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
