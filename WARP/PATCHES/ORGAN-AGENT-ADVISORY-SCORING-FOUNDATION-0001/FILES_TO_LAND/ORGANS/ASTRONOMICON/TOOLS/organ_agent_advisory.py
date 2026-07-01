#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

PATCH_ID = "ORGAN-AGENT-ADVISORY-SCORING-FOUNDATION-0001"
MATRIX = Path("ORGANS/ASTRONOMICON/MATRICES/ORGAN_AGENT_ADVISORY_SCORING_MATRIX_V0_1.json")
SUMMARY = Path("ORGANS/ASTRONOMICON/REPORTS/ORGAN_AGENT_ADVISORY_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/ASTRONOMICON/REPORTS/ORGAN_AGENT_ADVISORY_REPORT_V0_1.md")
RECEIPT = Path("ORGANS/ASTRONOMICON/RECEIPTS/organ_agent_advisory_scoring_receipt.json")

ORGANS = [
    "ASTRONOMICON","ADMINISTRATUM","DOCTRINARIUM","MECHANICUS","INQUISITION",
    "CUSTODES","STRATEGIUM","SCHOLA_IMPERIALIS","OFFICIO_AGENTIS","THRONE"
]

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

def clamp(x: float) -> float:
    return max(0.0, min(100.0, float(x)))

def weighted_score(weights: Dict[str, float], factors: Dict[str, float]) -> float:
    return round(sum(float(weights[k]) * clamp(factors.get(k, 0.0)) for k in weights), 2)

def file_score(repo: Path, paths: List[str]) -> float:
    if not paths:
        return 0.0
    return round(100.0 * sum(1 for p in paths if (repo / p).exists()) / len(paths), 2)

def verdict_score(repo: Path, path: str, pass_prefix: str = "PASS") -> float:
    data = load_json(repo / path)
    if not isinstance(data, dict):
        return 0.0
    verdict = str(data.get("verdict", ""))
    return 100.0 if verdict.startswith(pass_prefix) else 30.0 if verdict else 0.0

def current_evidence(repo: Path) -> Dict[str, float]:
    return {
        "intent_intake": verdict_score(repo, "ORGANS/ASTRONOMICON/RECEIPTS/astronomicon_dry_run_validator_receipt.json"),
        "pack_taxonomy_law": verdict_score(repo, "ORGANS/DOCTRINARIUM/RECEIPTS/pack_taxonomy_law_receipt.json"),
        "patch_lifecycle_foundation": verdict_score(repo, "ORGANS/ASTRONOMICON/RECEIPTS/patch_pack_lifecycle_validation_foundation_receipt.json"),
        "patch_lifecycle_launcher": verdict_score(repo, "ORGANS/ASTRONOMICON/RECEIPTS/patch_lifecycle_launcher_commands_receipt.json"),
        "mechanicus_preflight": verdict_score(repo, "ORGANS/MECHANICUS/RECEIPTS/patch_pack_technical_preflight_receipt.json"),
        "inquisition_scope_gate": verdict_score(repo, "ORGANS/INQUISITION/RECEIPTS/patch_pack_scope_fake_green_receipt.json"),
        "assembly_stage_scoring": verdict_score(repo, "ORGANS/THRONE/RECEIPTS/organ_assembly_stage_scoring_receipt.json"),
    }

def factors_for_organ(repo: Path, organ: str, ev: Dict[str, float]) -> Tuple[Dict[str, float], float, str, List[str]]:
    organ = organ.upper()
    if organ == "ASTRONOMICON":
        factors = {
            "evidence_strength": max(ev["intent_intake"], ev["patch_lifecycle_launcher"]),
            "validator_availability": file_score(repo, [
                "ORGANS/ASTRONOMICON/TOOLS/astronomicon_intake_dry_run.py",
                "ORGANS/ASTRONOMICON/TOOLS/astronomicon_patch_pack_smoke.py",
                "ORGANS/ASTRONOMICON/VALIDATORS/validate_patch_lifecycle_launcher_commands.py"
            ]),
            "authority_clarity": ev["pack_taxonomy_law"],
            "scope_clarity": ev["inquisition_scope_gate"],
            "dependency_readiness": min(ev["patch_lifecycle_foundation"], ev["patch_lifecycle_launcher"]),
            "reversibility": 85,
            "risk_control": ev["inquisition_scope_gate"],
            "operator_clarity": ev["patch_lifecycle_launcher"],
        }
        return factors, 92, "operator intake / closure guidance", [
            "launcher commands are present",
            "patch lifecycle foundation exists",
            "smoke can refuse closure"
        ]
    if organ == "MECHANICUS":
        factors = {
            "evidence_strength": ev["mechanicus_preflight"],
            "validator_availability": file_score(repo, [
                "ORGANS/MECHANICUS/VALIDATORS/validate_patch_pack_technical_preflight.py",
                "ORGANS/MECHANICUS/MATRICES/MECHANICUS_PATCH_PACK_TECHNICAL_PREFLIGHT_MATRIX_V0_1.json"
            ]),
            "authority_clarity": ev["pack_taxonomy_law"],
            "scope_clarity": ev["inquisition_scope_gate"],
            "dependency_readiness": ev["patch_lifecycle_foundation"],
            "reversibility": 90,
            "risk_control": ev["inquisition_scope_gate"],
            "operator_clarity": ev["patch_lifecycle_launcher"],
        }
        return factors, 88, "technical preflight hardness", ["manifest/hash preflight exists", "runner danger pattern scan exists"]
    if organ == "INQUISITION":
        factors = {
            "evidence_strength": ev["inquisition_scope_gate"],
            "validator_availability": file_score(repo, [
                "ORGANS/INQUISITION/VALIDATORS/validate_patch_pack_scope_fake_green.py",
                "ORGANS/INQUISITION/MATRICES/INQUISITION_PATCH_PACK_SCOPE_FAKE_GREEN_MATRIX_V0_1.json"
            ]),
            "authority_clarity": ev["pack_taxonomy_law"],
            "scope_clarity": 90,
            "dependency_readiness": ev["patch_lifecycle_foundation"],
            "reversibility": 80,
            "risk_control": ev["inquisition_scope_gate"],
            "operator_clarity": ev["patch_lifecycle_launcher"],
        }
        return factors, 86, "fake-green and scope suspicion", ["scope gate exists", "receipt != work done law exists"]
    if organ == "DOCTRINARIUM":
        factors = {
            "evidence_strength": ev["pack_taxonomy_law"],
            "validator_availability": file_score(repo, [
                "ORGANS/DOCTRINARIUM/VALIDATORS/validate_pack_taxonomy_law.py",
                "ORGANS/DOCTRINARIUM/MATRICES/PACK_TAXONOMY_MATRIX_V0_1.json"
            ]),
            "authority_clarity": 95,
            "scope_clarity": 80,
            "dependency_readiness": ev["assembly_stage_scoring"],
            "reversibility": 88,
            "risk_control": ev["inquisition_scope_gate"],
            "operator_clarity": 75,
        }
        return factors, 78, "law/schema clarity", ["pack taxonomy law exists", "duty contracts exist"]
    if organ == "ADMINISTRATUM":
        factors = {
            "evidence_strength": file_score(repo, [
                "ORGANS/ADMINISTRATUM/REGISTRY/IMPERIUM_POPULATION_CENSUS_CURRENT_V0_2.json",
                "ORGANS/ADMINISTRATUM/RECEIPTS/population_census_refresh_receipt.json"
            ]),
            "validator_availability": 55,
            "authority_clarity": ev["pack_taxonomy_law"],
            "scope_clarity": 70,
            "dependency_readiness": ev["patch_lifecycle_foundation"],
            "reversibility": 75,
            "risk_control": 70,
            "operator_clarity": ev["patch_lifecycle_launcher"],
        }
        return factors, 74, "receipt and registry indexing", ["census exists", "patch lifecycle receipts now multiply"]
    if organ == "CUSTODES":
        factors = {
            "evidence_strength": 15,
            "validator_availability": 10,
            "authority_clarity": ev["pack_taxonomy_law"],
            "scope_clarity": 65,
            "dependency_readiness": 40,
            "reversibility": 70,
            "risk_control": ev["inquisition_scope_gate"],
            "operator_clarity": 65,
        }
        return factors, 96, "trust-chain gap", ["trust is not claimed", "validators now need honesty review"]
    if organ == "THRONE":
        factors = {
            "evidence_strength": ev["assembly_stage_scoring"],
            "validator_availability": 60,
            "authority_clarity": 90,
            "scope_clarity": 75,
            "dependency_readiness": 45,
            "reversibility": 80,
            "risk_control": ev["inquisition_scope_gate"],
            "operator_clarity": ev["patch_lifecycle_launcher"],
        }
        return factors, 94, "Crown confirmation gap", ["stage scoring exists", "foundation validators do not claim Throne"]
    if organ == "STRATEGIUM":
        factors = {
            "evidence_strength": 35,
            "validator_availability": 10,
            "authority_clarity": ev["pack_taxonomy_law"],
            "scope_clarity": 65,
            "dependency_readiness": 65,
            "reversibility": 80,
            "risk_control": 65,
            "operator_clarity": ev["patch_lifecycle_launcher"],
        }
        return factors, 82, "priority/routing math", ["next-step selection needs scoring law"]
    if organ == "SCHOLA_IMPERIALIS":
        factors = {
            "evidence_strength": 25,
            "validator_availability": 10,
            "authority_clarity": 70,
            "scope_clarity": 60,
            "dependency_readiness": 60,
            "reversibility": 85,
            "risk_control": 65,
            "operator_clarity": 80,
        }
        return factors, 68, "lesson capture from validator failures", ["recent self-contamination lesson exists", "operator confusion with less happened"]
    if organ == "OFFICIO_AGENTIS":
        factors = {
            "evidence_strength": ev["pack_taxonomy_law"],
            "validator_availability": 20,
            "authority_clarity": ev["pack_taxonomy_law"],
            "scope_clarity": 60,
            "dependency_readiness": 45,
            "reversibility": 70,
            "risk_control": 70,
            "operator_clarity": ev["patch_lifecycle_launcher"],
        }
        return factors, 84, "servitor work-order boundary", ["Task Pack law exists", "dispatch remains forbidden"]
    return {}, 0, "unknown", []

def advisory_item(repo: Path, organ: str, matrix: Dict[str, Any], ev: Dict[str, float]) -> Dict[str, Any]:
    weights = matrix["success_score_formula"]["weighted_terms"]
    factors, impact, zone, evidence = factors_for_organ(repo, organ, ev)
    score = weighted_score(weights, factors)
    priority = round(score * impact / 100.0, 2)
    profile = matrix["organs"][organ]
    return {
        "organ_id": organ,
        "organ_domain": profile["domain"],
        "attention_zone": zone,
        "future_step_success_score": score,
        "impact_score": impact,
        "attention_priority_score": priority,
        "confidence": "HIGH" if score >= 75 else "MEDIUM" if score >= 50 else "LOW",
        "advisory_text": f"{organ}: обратить внимание на зону «{zone}». Расчётная успешность следующего шага {score}/100, приоритет внимания {priority}/100.",
        "why_this_zone": evidence,
        "factor_breakdown": factors,
        "language_mode": "ADVISORY_ZONE_ONLY_NO_DIRECT_ACTION",
        "not_claimed": ["execution", "trust", "Throne verdict", "concrete action command"]
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--organ")
    ap.add_argument("--out", default=str(SUMMARY))
    args = ap.parse_args()

    repo = Path(args.repo_root).resolve()
    matrix = load_json(repo / MATRIX)
    if not isinstance(matrix, dict):
        print(json.dumps({"verdict": "FAIL_ORGAN_AGENT_ADVISORY", "errors": ["matrix missing or invalid"]}, ensure_ascii=False, indent=2))
        return 1

    ev = current_evidence(repo)
    targets = [args.organ.upper()] if args.organ else ORGANS
    items = []
    errors = []
    for organ in targets:
        if organ not in ORGANS:
            errors.append(f"unknown organ {organ}")
            continue
        items.append(advisory_item(repo, organ, matrix, ev))

    ranked = sorted(items, key=lambda x: x["attention_priority_score"], reverse=True)

    generated = utc()
    summary = {
        "summary_id": "astronomicon.organ_agent_advisory_summary.v0_1",
        "patch_id": PATCH_ID,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "target_organ": args.organ.upper() if args.organ else None,
        "verdict": "PASS_ORGAN_AGENT_ADVISORY_GENERATED" if not errors else "FAIL_ORGAN_AGENT_ADVISORY",
        "score_model": matrix["success_score_formula"],
        "evidence_snapshot": ev,
        "advisory_count": len(ranked),
        "advisories": ranked,
        "hard_law": "Organs recommend attention zones, not concrete actions."
    }
    write_json(repo / args.out, summary)

    if not args.organ:
        write_json(repo / SUMMARY, summary)
        lines = [
            "# ORGAN AGENT ADVISORY REPORT V0.1",
            "",
            f"verdict: `{summary['verdict']}`  ",
            f"generated_at_utc: `{generated}`  ",
            f"repo_head: `{summary['repo_head']}`",
            "",
            "## Meaning",
            "",
            "Organs speak as advisory agents. They point to attention zones using mathematical scoring.",
            "",
            "They do not command concrete actions, execute, claim trust, or claim Throne verdict.",
            "",
            "## Ranked attention zones",
            ""
        ]
        for it in ranked:
            lines.append(f"- `{it['organ_id']}` — zone `{it['attention_zone']}`, success `{it['future_step_success_score']}`, priority `{it['attention_priority_score']}`, confidence `{it['confidence']}`")
        lines += ["", "## Advisory voice", ""]
        for it in ranked[:10]:
            lines.append(f"- {it['advisory_text']}")
        (repo / REPORT).parent.mkdir(parents=True, exist_ok=True)
        (repo / REPORT).write_text("\n".join(lines) + "\n", encoding="utf-8")
        receipt = {
            "receipt_id": "receipt.astronomicon.organ_agent_advisory_scoring.v0_1",
            "task_id": PATCH_ID,
            "validator_id": "organ_agent_advisory_generator.v0_1",
            "verdict": summary["verdict"],
            "generated_at_utc": generated,
            "summary": SUMMARY.as_posix(),
            "report": REPORT.as_posix(),
            "errors": errors,
            "warnings": [],
            "meaning": "Conversational organ-agent advisory generated from mathematical scoring; no concrete actions claimed."
        }
        write_json(repo / RECEIPT, receipt)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
