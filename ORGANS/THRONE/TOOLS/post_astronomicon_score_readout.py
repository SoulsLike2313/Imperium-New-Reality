#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

PATCH_ID = "ASTRONOMICON-CROWN-STAGE-SCORING-INTEGRATION-0001"
MATRIX_V2 = Path("ORGANS/THRONE/MATRICES/POST_ASTRONOMICON_SCORE_READOUT_GAP_FIELDS_HOTFIX_MATRIX_V0_2.json")
SUMMARY = Path("ORGANS/THRONE/REPORTS/POST_ASTRONOMICON_SCORE_READOUT_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/THRONE/REPORTS/POST_ASTRONOMICON_SCORE_READOUT_REPORT_V0_1.md")
RECEIPT = Path("ORGANS/THRONE/RECEIPTS/post_astronomicon_score_readout_receipt.json")

CROWN_STAGE = Path("ORGANS/THRONE/REPORTS/ASTRONOMICON_CROWN_STAGE_SCORING_INTEGRATION_SUMMARY_V0_1.json")

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

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    matrix = load_json(repo / MATRIX_V2) or {}
    errors: List[str] = []
    warnings: List[str] = []
    if not isinstance(matrix, dict):
        matrix = {}
        errors.append("score readout matrix missing or invalid")

    required = matrix.get("required_current_inputs", {})
    inputs = {}
    for key, rel in required.items():
        p = repo / rel
        data = load_json(p) if p.is_file() and p.suffix.lower() == ".json" else None
        inputs[key] = {"path": rel, "exists": p.exists(), "data": data}
        if not p.exists():
            errors.append(f"missing required input {key}: {rel}")
        elif p.suffix.lower() == ".json" and data is None:
            errors.append(f"invalid json input {key}: {rel}")

    baseline = matrix.get("baseline", {})
    source_objects = [v.get("data") for v in inputs.values() if isinstance(v.get("data"), dict)]

    astro = inputs.get("astronomicon_hardening", {}).get("data") or {}
    custodes = inputs.get("custodes_audit", {}).get("data") or {}
    throne = inputs.get("throne_crown", {}).get("data") or {}
    crown_stage = load_json(repo / CROWN_STAGE)
    crown_aware_scores = crown_stage.get("crown_aware_scores", {}) if isinstance(crown_stage, dict) else {}

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

    crown_stage_integrated = isinstance(crown_stage, dict) and crown_stage.get("stage_integration_state") == "CROWN_AWARE_STAGE_OVERLAY_READY"
    stage_integrates_local_crown = crown_stage_integrated and crown_aware_scores.get("red_team_score", 0) > 0 and crown_aware_scores.get("blue_team_score", 0) > 0

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

    integration_note = (
        "Local Astronomicon Crown order is integrated into an explicit crown-aware global stage overlay; canonical v0.1 stage summary is preserved."
        if stage_integrates_local_crown else
        "Global stage scorer still does not consume the local Astronomicon Crown order; next required work is explicit stage-score integration."
    )

    verdict = "PASS_POST_ASTRONOMICON_SCORE_READOUT_READY" if not errors else "FAIL_POST_ASTRONOMICON_SCORE_READOUT"
    generated = utc()
    summary = {
        "summary_id": "throne.post_astronomicon_score_readout_summary.v0_3_crown_stage_overlay",
        "task_id": PATCH_ID,
        "validator_id": "post_astronomicon_score_readout.v0_3_crown_stage_overlay",
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "baseline": baseline,
        "current_scores": current_scores,
        "crown_aware_scores": crown_aware_scores,
        "deltas_vs_baseline": deltas,
        "astronomicon_chain_ok": chain_ok,
        "stage_integrates_local_crown": bool(stage_integrates_local_crown),
        "stage_integration_mode": "CROWN_AWARE_OVERLAY" if stage_integrates_local_crown else "NOT_INTEGRATED",
        "integration_note": integration_note,
        "missing_required_current_scores": missing_scores,
        "crown_stage_summary": CROWN_STAGE.as_posix() if crown_stage_integrated else None,
        "errors": errors,
        "warnings": warnings,
        "not_claimed": ["Great Nine assembled", "Core v1 ready", "visual work resumed", "Throne self-validation", "canonical v0.1 stage overwrite"]
    }
    receipt = {
        "receipt_id": "receipt.throne.post_astronomicon_score_readout.v0_3_crown_stage_overlay",
        "task_id": PATCH_ID,
        "validator_id": "post_astronomicon_score_readout.v0_3_crown_stage_overlay",
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "errors": errors,
        "warnings": warnings,
        "meaning": "Score readout with Astronomicon crown-aware stage overlay."
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    def row(label: str, key: str, source: Dict[str, Any]) -> str:
        cur = source.get(key)
        base = baseline.get(key)
        d = delta(cur, base) if key in baseline else None
        if base is None:
            return f"| {label} | `{cur}` | — | — |"
        return f"| {label} | `{cur}` | `{base}` | `{d}` |"

    lines = [
        "# POST ASTRONOMICON SCORE READOUT V0.3 — CROWN STAGE OVERLAY",
        "",
        f"verdict: `{verdict}`  ",
        f"stage_integrates_local_crown: `{stage_integrates_local_crown}`  ",
        f"stage_integration_mode: `{summary['stage_integration_mode']}`",
        "",
        "## Meaning",
        "",
        integration_note,
        "",
        "## Canonical current scores",
        "",
        "| Metric | Current | Baseline | Delta |",
        "|---|---:|---:|---:|",
        row("red_team_score", "red_team_score", current_scores),
        row("blue_team_score", "blue_team_score", current_scores),
        row("organ_truth_maturity_score", "organ_truth_maturity_score", current_scores),
        row("organ_assembled_score", "organ_assembled_score", current_scores),
        "",
        "## Crown-aware overlay scores",
        "",
        "| Metric | Crown-aware score |",
        "|---|---:|",
    ]
    for k in [
        "red_team_score",
        "blue_team_score",
        "custodes_organ_validators_score",
        "throne_organ_validators_score",
        "trust_proven_score",
        "rule_validated_score",
        "tui_launcher_presence_score",
        "throne_confirmed_score",
        "organ_truth_maturity_score_crown_aware_estimate",
        "organ_assembled_score",
    ]:
        lines.append(f"| {k} | `{crown_aware_scores.get(k)}` |")
    lines += ["", "## Not claimed", ""]
    for x in summary["not_claimed"]:
        lines.append(f"- {x}")
    (repo / REPORT).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "task_id": PATCH_ID,
        "validator_id": "post_astronomicon_score_readout.v0_3_crown_stage_overlay",
        "verdict": verdict,
        "astronomicon_chain_ok": chain_ok,
        "stage_integrates_local_crown": bool(stage_integrates_local_crown),
        "stage_integration_mode": summary["stage_integration_mode"],
        "crown_aware_scores": crown_aware_scores,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "receipt": RECEIPT.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
