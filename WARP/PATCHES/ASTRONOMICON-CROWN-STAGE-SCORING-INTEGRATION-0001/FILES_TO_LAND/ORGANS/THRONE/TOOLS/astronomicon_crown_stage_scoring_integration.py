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
MATRIX = Path("ORGANS/THRONE/MATRICES/ASTRONOMICON_CROWN_STAGE_SCORING_INTEGRATION_MATRIX_V0_1.json")
SUMMARY = Path("ORGANS/THRONE/REPORTS/ASTRONOMICON_CROWN_STAGE_SCORING_INTEGRATION_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/THRONE/REPORTS/ASTRONOMICON_CROWN_STAGE_SCORING_INTEGRATION_REPORT_V0_1.md")
RECEIPT = Path("ORGANS/THRONE/RECEIPTS/astronomicon_crown_stage_scoring_integration_receipt.json")

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

def deep_get(data: Any, key: str, default=None) -> Any:
    if isinstance(data, dict):
        if key in data:
            return data[key]
        for v in data.values():
            r = deep_get(v, key, None)
            if r is not None:
                return r
    if isinstance(data, list):
        for item in data:
            r = deep_get(item, key, None)
            if r is not None:
                return r
    return default

def is_pass(data: Any) -> bool:
    return isinstance(data, dict) and str(data.get("verdict", "")).startswith("PASS")

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
        errors.append("integration matrix missing or invalid")

    inputs = {}
    for key, rel in matrix.get("required_inputs", {}).items():
        p = repo / rel
        data = load_json(p) if p.is_file() and p.suffix.lower() == ".json" else None
        inputs[key] = {"path": rel, "exists": p.exists(), "data": data}
        if not p.exists():
            errors.append(f"missing required input {key}: {rel}")
        elif p.suffix.lower() == ".json" and data is None:
            errors.append(f"invalid json input {key}: {rel}")

    canonical = inputs.get("canonical_stage_summary", {}).get("data") or {}
    canonical_scores = canonical.get("scores", {}) if isinstance(canonical.get("scores"), dict) else {}
    astro = inputs.get("astronomicon_red_blue_hardening", {}).get("data") or {}
    custodes = inputs.get("custodes_audit", {}).get("data") or {}
    throne = inputs.get("throne_crown", {}).get("data") or {}
    tui_console = inputs.get("tui_console_receipt", {}).get("data") or {}
    tui_window = inputs.get("windowed_tui_receipt", {}).get("data") or {}

    organ_count = int(matrix.get("organ_count", 10))
    weight = float(matrix.get("per_organ_weight", 100.0 / organ_count))

    red_ok = astro.get("red_local_hardening_score") == 100.0 and throne.get("astronomicon_crown_order_score") == 100.0
    blue_ok = astro.get("blue_local_hardening_score") == 100.0 and throne.get("astronomicon_crown_order_score") == 100.0
    custodes_ok = custodes.get("custodes_validation_score") == 100.0 and isinstance(custodes.get("indictments"), list) and len(custodes.get("indictments")) == 0
    throne_ok = throne.get("astronomicon_crown_order_score") == 100.0 and throne.get("throne_self_validation_score") == 0.0
    tui_ok = is_pass(tui_console) and is_pass(tui_window)

    if not red_ok: errors.append("Astronomicon red local hardening / Crown order condition failed")
    if not blue_ok: errors.append("Astronomicon blue local hardening / Crown order condition failed")
    if not custodes_ok: errors.append("Custodes Astronomicon condition failed")
    if not throne_ok: errors.append("Throne Crown order anti-self-deception condition failed")
    if not tui_ok: warnings.append("TUI presence condition not fully PASS; score remains 0 for TUI launcher presence")

    crown_aware_scores = dict(canonical_scores)
    crown_aware_scores.update({
        "red_team_score": weight if red_ok else 0.0,
        "blue_team_score": weight if blue_ok else 0.0,
        "red_team_layer_score": weight if red_ok else 0.0,
        "blue_team_layer_score": weight if blue_ok else 0.0,
        "custodes_organ_validators_score": weight if custodes_ok else 0.0,
        "throne_organ_validators_score": weight if throne_ok else 0.0,
        "trust_proven_score": weight if (custodes_ok and throne_ok) else 0.0,
        "rule_validated_score": weight if (red_ok and blue_ok and custodes_ok) else 0.0,
        "tui_launcher_presence_score": weight if tui_ok else 0.0,
        "action_proven_score": 0.0,
        "throne_confirmed_score": weight if throne_ok else 0.0,
        "organ_assembled_score": 0.0
    })

    high_level = [
        crown_aware_scores.get("profile_baseline_score", 0.0),
        crown_aware_scores.get("duty_defined_score", 0.0),
        crown_aware_scores.get("assembly_target_defined_score", 0.0),
        crown_aware_scores.get("rule_validated_score", 0.0),
        crown_aware_scores.get("action_proven_score", 0.0),
        crown_aware_scores.get("trust_proven_score", 0.0),
        crown_aware_scores.get("throne_confirmed_score", 0.0),
        crown_aware_scores.get("organ_assembled_score", 0.0),
    ]
    crown_aware_scores["organ_truth_maturity_score_crown_aware_estimate"] = round(sum(float(x or 0.0) for x in high_level) / len(high_level), 2)

    verdict = "PASS_ASTRONOMICON_CROWN_STAGE_SCORING_INTEGRATED" if not errors else "FAIL_ASTRONOMICON_CROWN_STAGE_SCORING_INTEGRATION"
    generated = utc()
    summary = {
        "summary_id": "throne.astronomicon_crown_stage_scoring_integration_summary.v0_1",
        "task_id": PATCH_ID,
        "validator_id": "astronomicon_crown_stage_scoring_integration.v0_1",
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "target_organ": "ASTRONOMICON",
        "organ_count": organ_count,
        "integrated_organ_count": 1 if verdict.startswith("PASS") else 0,
        "per_organ_weight": weight,
        "stage_integration_state": "CROWN_AWARE_STAGE_OVERLAY_READY" if verdict.startswith("PASS") else "CROWN_AWARE_STAGE_OVERLAY_BLOCKED",
        "canonical_scores_before": canonical_scores,
        "crown_aware_scores": crown_aware_scores,
        "conditions": {
            "red_ok": red_ok,
            "blue_ok": blue_ok,
            "custodes_ok": custodes_ok,
            "throne_ok": throne_ok,
            "tui_ok": tui_ok,
            "throne_self_validation_score": throne.get("throne_self_validation_score"),
            "astronomicon_assembled_score": throne.get("astronomicon_assembled_score")
        },
        "errors": errors,
        "warnings": warnings,
        "not_claimed": matrix.get("not_claimed", [])
    }
    receipt = {
        "receipt_id": "receipt.throne.astronomicon_crown_stage_scoring_integration.v0_1",
        "task_id": PATCH_ID,
        "validator_id": "astronomicon_crown_stage_scoring_integration.v0_1",
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "errors": errors,
        "warnings": warnings,
        "meaning": "Astronomicon local Crown order is integrated into a global 10-organ crown-aware stage scoring overlay without claiming assembled state."
    }

    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    lines = [
        "# ASTRONOMICON CROWN STAGE SCORING INTEGRATION V0.1",
        "",
        f"verdict: `{verdict}`  ",
        f"stage_integration_state: `{summary['stage_integration_state']}`  ",
        f"integrated_organ_count: `{summary['integrated_organ_count']}` / `{organ_count}`  ",
        f"per_organ_weight: `{weight}`",
        "",
        "## Meaning",
        "",
        "Astronomicon's local Crown order now contributes to a crown-aware global stage overlay.",
        "",
        "This does not claim Astronomicon assembled, Great Nine assembled, Core v1 ready, or Throne self-validation.",
        "",
        "## Crown-aware scores",
        "",
        "| Metric | Score |",
        "|---|---:|",
    ]
    for k in [
        "red_team_score",
        "blue_team_score",
        "red_team_layer_score",
        "blue_team_layer_score",
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
    lines += ["", "## Conditions", ""]
    for k, v in summary["conditions"].items():
        lines.append(f"- `{k}`: `{v}`")
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
        "validator_id": "astronomicon_crown_stage_scoring_integration.v0_1",
        "verdict": verdict,
        "stage_integration_state": summary["stage_integration_state"],
        "integrated_organ_count": summary["integrated_organ_count"],
        "per_organ_weight": weight,
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
