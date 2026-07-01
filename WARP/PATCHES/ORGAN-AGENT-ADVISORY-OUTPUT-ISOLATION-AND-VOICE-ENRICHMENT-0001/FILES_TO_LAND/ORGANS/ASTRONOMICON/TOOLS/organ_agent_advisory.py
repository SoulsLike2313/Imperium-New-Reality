#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

PATCH_ID = "ORGAN-AGENT-ADVISORY-OUTPUT-ISOLATION-AND-VOICE-ENRICHMENT-0001"
BASE_MATRIX = Path("ORGANS/ASTRONOMICON/MATRICES/ORGAN_AGENT_ADVISORY_SCORING_MATRIX_V0_1.json")
ISO_MATRIX = Path("ORGANS/ASTRONOMICON/MATRICES/ORGAN_AGENT_ADVISORY_OUTPUT_ISOLATION_AND_VOICE_MATRIX_V0_1.json")
SUMMARY = Path("ORGANS/ASTRONOMICON/REPORTS/ORGAN_AGENT_ADVISORY_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/ASTRONOMICON/REPORTS/ORGAN_AGENT_ADVISORY_REPORT_V0_1.md")
RECEIPT = Path("ORGANS/ASTRONOMICON/RECEIPTS/organ_agent_advisory_scoring_receipt.json")

ORGANS = [
    "ASTRONOMICON","ADMINISTRATUM","DOCTRINARIUM","MECHANICUS","INQUISITION",
    "CUSTODES","STRATEGIUM","SCHOLA_IMPERIALIS","OFFICIO_AGENTIS","THRONE"
]

PROFILE_DEFAULTS = {
    "ASTRONOMICON": ("operator intake / closure guidance", 92, ["intent intake exists", "patch lifecycle commands exist", "smoke closure exists"]),
    "ADMINISTRATUM": ("receipt and registry indexing", 74, ["census refresh exists", "receipt chain grows after lifecycle work"]),
    "DOCTRINARIUM": ("law/schema clarity", 78, ["pack taxonomy law exists", "organ duty contracts exist"]),
    "MECHANICUS": ("technical preflight hardness", 88, ["manifest and runner preflight exists", "syntax check avoids pyc self-contamination"]),
    "INQUISITION": ("fake-green and scope suspicion", 86, ["scope gate exists", "receipt does not equal work law exists"]),
    "CUSTODES": ("trust-chain gap", 96, ["trust is not claimed", "validator honesty still needs a dedicated layer"]),
    "STRATEGIUM": ("priority/routing math", 82, ["next attention ranking now has score factors"]),
    "SCHOLA_IMPERIALIS": ("lesson capture from validator failures", 68, ["self-contamination lesson exists", "operator pager confusion lesson exists"]),
    "OFFICIO_AGENTIS": ("servitor work-order boundary", 84, ["Task Pack law exists", "dispatch remains forbidden"]),
    "THRONE": ("Crown confirmation gap", 94, ["stage scoring exists", "foundation validators do not claim Throne"])
}

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

def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()

def clamp(x: float) -> float:
    return max(0.0, min(100.0, float(x)))

def file_score(repo: Path, paths: List[str]) -> float:
    if not paths:
        return 0.0
    return round(100.0 * sum(1 for p in paths if (repo / p).exists()) / len(paths), 2)

def verdict_score(repo: Path, path: str) -> float:
    data = load_json(repo / path)
    if not isinstance(data, dict):
        return 0.0
    verdict = str(data.get("verdict", ""))
    return 100.0 if verdict.startswith("PASS") else 30.0 if verdict else 0.0

def evidence(repo: Path) -> Dict[str, float]:
    return {
        "intent_intake": verdict_score(repo, "ORGANS/ASTRONOMICON/RECEIPTS/astronomicon_dry_run_validator_receipt.json"),
        "pack_taxonomy_law": verdict_score(repo, "ORGANS/DOCTRINARIUM/RECEIPTS/pack_taxonomy_law_receipt.json"),
        "patch_lifecycle_foundation": verdict_score(repo, "ORGANS/ASTRONOMICON/RECEIPTS/patch_pack_lifecycle_validation_foundation_receipt.json"),
        "patch_lifecycle_launcher": verdict_score(repo, "ORGANS/ASTRONOMICON/RECEIPTS/patch_lifecycle_launcher_commands_receipt.json"),
        "organ_advisory_scoring": verdict_score(repo, "ORGANS/ASTRONOMICON/RECEIPTS/organ_agent_advisory_scoring_validation_receipt.json"),
        "mechanicus_preflight": verdict_score(repo, "ORGANS/MECHANICUS/RECEIPTS/patch_pack_technical_preflight_receipt.json"),
        "inquisition_scope_gate": verdict_score(repo, "ORGANS/INQUISITION/RECEIPTS/patch_pack_scope_fake_green_receipt.json"),
        "assembly_stage_scoring": verdict_score(repo, "ORGANS/THRONE/RECEIPTS/organ_assembly_stage_scoring_receipt.json")
    }

def weights(matrix: Dict[str, Any]) -> Dict[str, float]:
    w = matrix.get("success_score_formula", {}).get("weighted_terms", {}) if isinstance(matrix, dict) else {}
    if not w:
        return {
            "evidence_strength": 0.18, "validator_availability": 0.16, "authority_clarity": 0.14,
            "scope_clarity": 0.12, "dependency_readiness": 0.12, "reversibility": 0.10,
            "risk_control": 0.10, "operator_clarity": 0.08
        }
    return {k: float(v) for k, v in w.items()}

def factor_map(repo: Path, organ: str, ev: Dict[str, float]) -> Dict[str, float]:
    if organ == "ASTRONOMICON":
        return {
            "evidence_strength": max(ev["intent_intake"], ev["patch_lifecycle_launcher"], ev["organ_advisory_scoring"]),
            "validator_availability": file_score(repo, [
                "ORGANS/ASTRONOMICON/TOOLS/astronomicon_intake_dry_run.py",
                "ORGANS/ASTRONOMICON/TOOLS/astronomicon_patch_pack_smoke.py",
                "ORGANS/ASTRONOMICON/TOOLS/organ_agent_advisory.py"
            ]),
            "authority_clarity": ev["pack_taxonomy_law"],
            "scope_clarity": ev["inquisition_scope_gate"],
            "dependency_readiness": min(ev["patch_lifecycle_foundation"], ev["patch_lifecycle_launcher"]),
            "reversibility": 85, "risk_control": ev["inquisition_scope_gate"], "operator_clarity": ev["patch_lifecycle_launcher"]
        }
    if organ == "MECHANICUS":
        return {
            "evidence_strength": ev["mechanicus_preflight"],
            "validator_availability": file_score(repo, [
                "ORGANS/MECHANICUS/VALIDATORS/validate_patch_pack_technical_preflight.py",
                "ORGANS/MECHANICUS/MATRICES/MECHANICUS_PATCH_PACK_TECHNICAL_PREFLIGHT_MATRIX_V0_1.json"
            ]),
            "authority_clarity": ev["pack_taxonomy_law"], "scope_clarity": ev["inquisition_scope_gate"],
            "dependency_readiness": ev["patch_lifecycle_foundation"], "reversibility": 90,
            "risk_control": ev["inquisition_scope_gate"], "operator_clarity": ev["patch_lifecycle_launcher"]
        }
    if organ == "INQUISITION":
        return {
            "evidence_strength": ev["inquisition_scope_gate"],
            "validator_availability": file_score(repo, [
                "ORGANS/INQUISITION/VALIDATORS/validate_patch_pack_scope_fake_green.py",
                "ORGANS/INQUISITION/MATRICES/INQUISITION_PATCH_PACK_SCOPE_FAKE_GREEN_MATRIX_V0_1.json"
            ]),
            "authority_clarity": ev["pack_taxonomy_law"], "scope_clarity": 90,
            "dependency_readiness": ev["patch_lifecycle_foundation"], "reversibility": 80,
            "risk_control": ev["inquisition_scope_gate"], "operator_clarity": ev["patch_lifecycle_launcher"]
        }
    if organ == "CUSTODES":
        return {"evidence_strength": 15, "validator_availability": 10, "authority_clarity": ev["pack_taxonomy_law"], "scope_clarity": 65, "dependency_readiness": 40, "reversibility": 70, "risk_control": ev["inquisition_scope_gate"], "operator_clarity": 65}
    if organ == "THRONE":
        return {"evidence_strength": ev["assembly_stage_scoring"], "validator_availability": 60, "authority_clarity": 90, "scope_clarity": 75, "dependency_readiness": 45, "reversibility": 80, "risk_control": ev["inquisition_scope_gate"], "operator_clarity": ev["patch_lifecycle_launcher"]}
    if organ == "DOCTRINARIUM":
        return {"evidence_strength": ev["pack_taxonomy_law"], "validator_availability": file_score(repo, ["ORGANS/DOCTRINARIUM/VALIDATORS/validate_pack_taxonomy_law.py","ORGANS/DOCTRINARIUM/MATRICES/PACK_TAXONOMY_MATRIX_V0_1.json"]), "authority_clarity": 95, "scope_clarity": 80, "dependency_readiness": ev["assembly_stage_scoring"], "reversibility": 88, "risk_control": ev["inquisition_scope_gate"], "operator_clarity": 75}
    if organ == "ADMINISTRATUM":
        return {"evidence_strength": file_score(repo, ["ORGANS/ADMINISTRATUM/REGISTRY/IMPERIUM_POPULATION_CENSUS_CURRENT_V0_2.json","ORGANS/ADMINISTRATUM/RECEIPTS/population_census_refresh_receipt.json"]), "validator_availability": 55, "authority_clarity": ev["pack_taxonomy_law"], "scope_clarity": 70, "dependency_readiness": ev["patch_lifecycle_foundation"], "reversibility": 75, "risk_control": 70, "operator_clarity": ev["patch_lifecycle_launcher"]}
    if organ == "STRATEGIUM":
        return {"evidence_strength": 35, "validator_availability": 10, "authority_clarity": ev["pack_taxonomy_law"], "scope_clarity": 65, "dependency_readiness": 65, "reversibility": 80, "risk_control": 65, "operator_clarity": ev["patch_lifecycle_launcher"]}
    if organ == "SCHOLA_IMPERIALIS":
        return {"evidence_strength": 25, "validator_availability": 10, "authority_clarity": 70, "scope_clarity": 60, "dependency_readiness": 60, "reversibility": 85, "risk_control": 65, "operator_clarity": 80}
    if organ == "OFFICIO_AGENTIS":
        return {"evidence_strength": ev["pack_taxonomy_law"], "validator_availability": 20, "authority_clarity": ev["pack_taxonomy_law"], "scope_clarity": 60, "dependency_readiness": 45, "reversibility": 70, "risk_control": 70, "operator_clarity": ev["patch_lifecycle_launcher"]}
    return {"evidence_strength": 0, "validator_availability": 0, "authority_clarity": 0, "scope_clarity": 0, "dependency_readiness": 0, "reversibility": 0, "risk_control": 0, "operator_clarity": 0}

def score(weights: Dict[str, float], factors: Dict[str, float]) -> float:
    return round(sum(float(weights.get(k, 0)) * clamp(factors.get(k, 0)) for k in weights), 2)

def advisory_item(repo: Path, organ: str, base_matrix: Dict[str, Any], iso_matrix: Dict[str, Any], ev: Dict[str, float]) -> Dict[str, Any]:
    zone, impact, ev_lines = PROFILE_DEFAULTS[organ]
    factors = factor_map(repo, organ, ev)
    s = score(weights(base_matrix), factors)
    priority = round(s * impact / 100.0, 2)
    profile = iso_matrix.get("organs", {}).get(organ, {})
    raises = []
    reduces = []
    for k, v in sorted(factors.items(), key=lambda kv: kv[1]):
        if v < 60:
            reduces.append(f"{k}: {v}/100 держит прогноз ниже")
        elif v >= 80:
            raises.append(f"{k}: {v}/100 поддерживает прогноз")
    if not raises:
        raises = ["имеющиеся evidence и operator clarity уже дают минимальную опору"]
    if not reduces:
        reduces = ["существенных слабых факторов в базовой формуле не найдено"]
    return {
        "organ_id": organ,
        "organ_domain": profile.get("domain", "profile domain not found"),
        "attention_zone": zone,
        "future_step_success_score": s,
        "impact_score": impact,
        "attention_priority_score": priority,
        "confidence": "HIGH" if s >= 75 else "MEDIUM" if s >= 50 else "LOW",
        "advisory_text": f"{organ}: зона внимания «{zone}». Расчётная успешность будущего шага {s}/100, приоритет внимания {priority}/100.",
        "what_is_visible": f"Видно профильную зону: {zone}; текущий расчёт основан на evidence snapshot и доступности валидаторов.",
        "why_this_zone_matters": f"Эта зона связана с доменом органа: {profile.get('domain', 'unknown')}. Усиление зоны повышает вероятность безопасного следующего шага без заявления trust.",
        "what_raises_success_probability": raises,
        "what_reduces_success_probability": reduces,
        "evidence_considered": ev_lines,
        "factor_breakdown": factors,
        "language_mode": "ADVISORY_ZONE_ONLY_NO_DIRECT_ACTION",
        "not_claimed": ["execution", "trust", "Throne verdict", "concrete action command"]
    }

def write_markdown(repo: Path, path: Path, title: str, advisories: List[Dict[str, Any]]):
    lines = [f"# {title}", "", "This is advisory-zone guidance only. It does not command concrete actions.", ""]
    for item in advisories:
        lines += [
            f"## {item['organ_id']}",
            "",
            f"- attention_zone: `{item['attention_zone']}`",
            f"- future_step_success_score: `{item['future_step_success_score']}`",
            f"- attention_priority_score: `{item['attention_priority_score']}`",
            f"- confidence: `{item['confidence']}`",
            "",
            item["advisory_text"],
            "",
            f"Visible: {item['what_is_visible']}",
            "",
            f"Why it matters: {item['why_this_zone_matters']}",
            "",
            "Raises probability:",
            *[f"- {x}" for x in item["what_raises_success_probability"]],
            "",
            "Reduces probability:",
            *[f"- {x}" for x in item["what_reduces_success_probability"]],
            "",
            "Not claimed:",
            *[f"- {x}" for x in item["not_claimed"]],
            ""
        ]
    (repo / path).parent.mkdir(parents=True, exist_ok=True)
    (repo / path).write_text("\n".join(lines) + "\n", encoding="utf-8")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--organ")
    ap.add_argument("--out")
    args = ap.parse_args()

    repo = Path(args.repo_root).resolve()
    base_matrix = load_json(repo / BASE_MATRIX) or {}
    iso_matrix = load_json(repo / ISO_MATRIX) or {}
    ev = evidence(repo)

    if args.organ:
        organ = args.organ.upper().replace("-", "_")
        if organ not in ORGANS:
            print(json.dumps({"verdict": "FAIL_ORGAN_AGENT_ADVISORY", "errors": [f"unknown organ {organ}"]}, ensure_ascii=False, indent=2))
            return 1
        item = advisory_item(repo, organ, base_matrix, iso_matrix, ev)
        out_json = Path(args.out) if args.out else Path(f"ORGANS/ASTRONOMICON/REPORTS/ORGAN_AGENT_ADVISORY_{organ}_V0_1.json")
        out_md = Path(str(out_json).replace(".json", ".md"))
        result = {
            "summary_id": "astronomicon.organ_agent_single_advisory.v0_1",
            "patch_id": PATCH_ID,
            "generated_at_utc": utc(),
            "repo_head": git_head(repo),
            "target_organ": organ,
            "verdict": "PASS_SINGLE_ORGAN_ADVISORY_GENERATED",
            "advisory_count": 1,
            "advisories": [item],
            "global_summary_touched": False,
            "hard_law": "Single-organ advisory writes isolated per-organ outputs and does not overwrite global summary."
        }
        write_json(repo / out_json, result)
        write_markdown(repo, out_md, f"ORGAN AGENT ADVISORY — {organ} V0.1", [item])
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    items = [advisory_item(repo, organ, base_matrix, iso_matrix, ev) for organ in ORGANS]
    ranked = sorted(items, key=lambda x: x["attention_priority_score"], reverse=True)
    result = {
        "summary_id": "astronomicon.organ_agent_advisory_summary.v0_1",
        "patch_id": PATCH_ID,
        "generated_at_utc": utc(),
        "repo_head": git_head(repo),
        "target_organ": None,
        "verdict": "PASS_ORGAN_AGENT_ADVISORY_GENERATED",
        "advisory_count": len(ranked),
        "advisories": ranked,
        "hard_law": "Organs recommend attention zones, not concrete actions."
    }
    out_json = Path(args.out) if args.out else SUMMARY
    write_json(repo / out_json, result)
    if not args.out or Path(args.out) == SUMMARY:
        write_markdown(repo, REPORT, "ORGAN AGENT ADVISORY REPORT V0.1", ranked)
        receipt = {
            "receipt_id": "receipt.astronomicon.organ_agent_advisory_scoring.v0_1",
            "task_id": PATCH_ID,
            "validator_id": "organ_agent_advisory_generator.v0_2_output_isolated",
            "verdict": result["verdict"],
            "generated_at_utc": result["generated_at_utc"],
            "summary": SUMMARY.as_posix(),
            "report": REPORT.as_posix(),
            "errors": [],
            "warnings": [],
            "meaning": "Global advisory generated. Per-organ advisory calls are isolated."
        }
        write_json(repo / RECEIPT, receipt)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
