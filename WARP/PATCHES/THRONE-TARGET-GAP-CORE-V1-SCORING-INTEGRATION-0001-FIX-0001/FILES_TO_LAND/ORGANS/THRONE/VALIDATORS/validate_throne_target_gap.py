#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse, csv, datetime as dt, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "THRONE-TARGET-GAP-VALIDATOR-0001"
UPGRADE_ID = "THRONE-TARGET-GAP-CORE-V1-SCORING-INTEGRATION-0001-FIX-0001"
VALIDATOR_ID = "throne_target_gap_validator.v0_3_core_v1_operational_split"

THRONE = Path("ORGANS/THRONE")
CENSUS_JSON = Path("WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/OUTPUTS/IMPERIUM_POPULATION_CENSUS_V0_1.json")
SUMMARY_JSON = Path("WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/OUTPUTS/IMPERIUM_POPULATION_SUMMARY_V0_1.json")

TARGET_MATRIX = THRONE / "MATRICES/THRONE_TARGET_V1_MATRIX_V0_1.json"
GAP_SCORING_MATRIX = THRONE / "MATRICES/THRONE_TARGET_GAP_SCORING_MATRIX_V0_1.json"
CORE_V1_SCORING_MATRIX = THRONE / "MATRICES/THRONE_TARGET_GAP_CORE_V1_SCORING_INTEGRATION_MATRIX_V0_1.json"
FIX_MATRIX = THRONE / "MATRICES/THRONE_TARGET_GAP_CORE_V1_SCORING_FIX_0001_MATRIX_V0_1.json"

RECEIPT = THRONE / "RECEIPTS/throne_target_gap_receipt.json"
REPORT = THRONE / "REPORTS/THRONE_TARGET_GAP_REPORT_V0_1.md"
ORGAN_CSV = THRONE / "REPORTS/THRONE_ORGAN_READINESS_TABLE_V0_1.csv"
NEXT_ATTENTION = THRONE / "REPORTS/THRONE_NEXT_ATTENTION_AREAS_V0_1.json"
CORE_BREAKDOWN_JSON = THRONE / "REPORTS/THRONE_CORE_V1_READINESS_BREAKDOWN_V0_1.json"
CORE_BREAKDOWN_CSV = THRONE / "REPORTS/THRONE_CORE_V1_READINESS_BREAKDOWN_V0_1.csv"
OP_BREAKDOWN_JSON = THRONE / "REPORTS/THRONE_CORE_V1_OPERATIONAL_BREAKDOWN_V0_1.json"
OP_BREAKDOWN_CSV = THRONE / "REPORTS/THRONE_CORE_V1_OPERATIONAL_BREAKDOWN_V0_1.csv"

GREAT_NINE = [
    "ASTRONOMICON", "ADMINISTRATUM", "DOCTRINARIUM", "MECHANICUS", "INQUISITION",
    "CUSTODES", "STRATEGIUM", "SCHOLA_IMPERIALIS", "OFFICIO_AGENTIS"
]
SUBJECTS = ["THRONE"] + GREAT_NINE

REQUIRED_SLOTS = [
    "README.md","ORGAN_CARD.json","MANIFEST.json","FUNCTIONS.md",
    "MATRICES","SCHEMAS","VALIDATORS","RECEIPTS","REPORTS","TESTS",
    "TUI","DASHBOARDS","EYES","BLOCK","LESSONS","NEGATIVE_LESSONS"
]

CORE_MATRICES = {
    "THRONE_KERNEL_ANATOMY_MATRIX_V0_1.json": ["kernel_identity","organ_kernel_roles","external_kernel_lessons","non_goals"],
    "THRONE_CORE_V1_DEFINITION_MATRIX_V0_1.json": ["oath","must_capabilities","v1_gate","benchmark_policy"],
    "THRONE_KERNEL_BOUNDARY_MATRIX_V0_1.json": ["zones","allowed_returns","forbidden_mutations","proof_requirements"],
    "THRONE_REQUEST_PACKET_MATRIX_V0_1.json": ["packet_types","task_pack_required_fields","patch_pack_required_fields","routing_rules"],
    "THRONE_OBJECT_REGISTRY_MATRIX_V0_1.json": ["registered_object_classes","required_fields","registry_owner"],
    "THRONE_ORGAN_SERVICE_STACK_MATRIX_V0_1.json": ["default_task_stack","default_patch_stack","stack_law"],
    "THRONE_SERVITOR_EXECUTION_BOUNDARY_MATRIX_V0_1.json": ["servitor_identity","allowed","forbidden","stop_conditions"],
    "THRONE_EVIDENCE_CHAIN_MATRIX_V0_1.json": ["chain","minimum_evidence","fake_green_guards"],
    "THRONE_TRUST_BOUNDARY_MATRIX_V0_1.json": ["trust_layers","required_questions","verdict_rules"],
    "THRONE_INTEGRATION_KERNEL_MATRIX_V0_1.json": ["integration_states","admission_path","kernel_rights_rule"],
    "THRONE_HUMAN_READABILITY_MATRIX_V0_1.json": ["tui_v1_must","human_translation_fields","non_goals"],
    "THRONE_CORE_V1_READINESS_SCORING_MATRIX_V0_1.json": ["dimensions","v1_gate_logic"],
}

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda: f.read(1024*1024), b""):
            h.update(c)
    return h.hexdigest()

def clamp(x: float) -> float:
    return round(max(0.0, min(100.0, x)), 2)

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def weighted(scores: Dict[str, float], weights: Dict[str, int]) -> float:
    total = sum(weights.values()) or 1
    return clamp(sum(scores.get(k,0) * w for k,w in weights.items()) / total)

def organ_path(organ: str) -> Path:
    return THRONE if organ == "THRONE" else Path("ORGANS") / organ

def classify_by_owner(residents: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    by = defaultdict(list)
    for r in residents:
        owner = str(r.get("owner_candidate") or "UNKNOWN")
        by[owner].append(r)
        if "ORGANS/THRONE/" in str(r.get("path","")) and owner != "THRONE":
            by["THRONE"].append(r)
    return by

def count_classes(items: List[Dict[str, Any]]) -> Counter:
    return Counter(str(r.get("class") or "UNKNOWN") for r in items)

def exists_score(root: Path, repo: Path) -> Dict[str, Any]:
    abs_root = repo / root
    present = []
    missing = []
    for s in REQUIRED_SLOTS:
        if (abs_root / s).exists():
            present.append(s)
        else:
            missing.append(s)
    return {"present": present, "missing": missing, "slot_score": clamp(len(present)*100/max(1,len(REQUIRED_SLOTS)))}

def parse_json_if_exists(path: Path) -> bool:
    if not path.is_file(): return False
    try:
        read_json(path); return True
    except Exception:
        return False

def coverage(count: int, target: int) -> float:
    return clamp(count*100/max(1,target))

def compute_organ(repo: Path, organ: str, by_owner: Dict[str,List[Dict[str,Any]]]) -> Dict[str, Any]:
    root = organ_path(organ)
    abs_root = repo / root
    exists = abs_root.is_dir()
    ss = exists_score(root, repo) if exists else {"present": [], "missing": REQUIRED_SLOTS, "slot_score": 0}
    items = by_owner.get(organ, [])
    cc = count_classes(items)
    schema = cc.get("SCHEMA",0); validator = cc.get("VALIDATOR",0); receipt = cc.get("RECEIPT",0); report = cc.get("REPORT",0); matrix = cc.get("MATRIX",0)
    has_warp = any(str(r.get("status")) == "WARP" for r in items)
    has_neg = any(str(r.get("status")) == "NEGATIVE_EXAMPLE" for r in items)
    has_quar = any(str(r.get("status")) == "QUARANTINE" for r in items)
    scores = {
        "physical_presence_score": 100 if exists else 0,
        "required_slot_score": ss["slot_score"],
        "identity_score": 100 if parse_json_if_exists(abs_root/"ORGAN_CARD.json") else 0,
        "manifest_score": 100 if parse_json_if_exists(abs_root/"MANIFEST.json") else 0,
        "schema_coverage_score": coverage(schema,3),
        "validator_coverage_score": coverage(validator,2),
        "receipt_coverage_score": coverage(receipt,3),
        "boundary_lifecycle_score": 100 if exists and not has_warp else 70 if exists else 0,
        "observability_score": clamp(sum(1 for p in ["TUI","DASHBOARDS","EYES","REPORTS"] if (abs_root/p).exists())*25),
        "trust_action_readiness_score": clamp(sum([validator>0, receipt>0, matrix>0, (abs_root/"FUNCTIONS.md").is_file()])*25)
    }
    weights = {
        "physical_presence_score":10,"required_slot_score":15,"identity_score":10,"manifest_score":10,
        "schema_coverage_score":10,"validator_coverage_score":15,"receipt_coverage_score":10,
        "boundary_lifecycle_score":10,"observability_score":5,"trust_action_readiness_score":5
    }
    scores["organ_readiness_score"] = weighted(scores, weights)
    gaps = []
    for f in ["README.md","ORGAN_CARD.json","MANIFEST.json","FUNCTIONS.md"]:
        if f in ss["missing"]: gaps.append(f"missing {f}")
    if schema == 0: gaps.append("no schema evidence")
    if validator == 0: gaps.append("no validator evidence")
    if receipt == 0: gaps.append("no receipt evidence")
    if has_warp: gaps.append("has WARP-status residents")
    if has_quar: gaps.append("has quarantine residents")
    if has_neg: gaps.append("has negative-example residents")
    return {
        "organ_id": organ, "path": root.as_posix(), "exists": exists, "scores": scores,
        "present_slots": ss["present"], "missing_slots": ss["missing"],
        "evidence_counts": {"residents": len(items), "schemas": schema, "validators": validator, "receipts": receipt, "reports": report, "matrices": matrix},
        "major_gaps": gaps[:30]
    }

def matrix_score(repo: Path, fname: str, sections: List[str]) -> Dict[str, Any]:
    p = repo / THRONE / "MATRICES" / fname
    res = {"matrix": fname, "exists": False, "parses": False, "present_sections": [], "missing_sections": list(sections), "score": 0.0, "errors": []}
    if not p.is_file():
        res["errors"].append("missing"); return res
    res["exists"] = True
    try:
        data = read_json(p); res["parses"] = True
    except Exception as e:
        res["errors"].append(str(e)); res["score"] = 20; return res
    present = [s for s in sections if s in data]
    missing = [s for s in sections if s not in data]
    res["present_sections"] = present; res["missing_sections"] = missing
    res["score"] = clamp(40 + len(present)*50/max(1,len(sections)) + (10 if len(json.dumps(data, ensure_ascii=False)) > 400 else 0))
    return res

def compute_target_definition(repo: Path) -> Dict[str, Any]:
    results = {fname: matrix_score(repo, fname, secs) for fname, secs in CORE_MATRICES.items()}
    score = clamp(sum(r["score"] for r in results.values()) / max(1, len(results)))
    return {"score": score, "matrix_results": results, "missing": [k for k,r in results.items() if not r["exists"]], "malformed": [k for k,r in results.items() if r["exists"] and not r["parses"]]}

def path_text(residents: List[Dict[str,Any]]) -> str:
    return "\n".join(str(r.get("path","")) + " " + str(r.get("class","")) + " " + str(r.get("owner_candidate","")) for r in residents).lower()

def signal_score(text: str, patterns: List[str], cap: int = 5) -> Dict[str, Any]:
    hits = []
    for pat in patterns:
        if re.search(pat, text, re.I):
            hits.append(pat)
    return {"score": clamp(len(hits)*100/max(1, min(cap, len(patterns)))), "hits": hits, "missing": [p for p in patterns if p not in hits]}

def compute_operational(repo: Path, residents: List[Dict[str,Any]], organs: Dict[str,Any]) -> Dict[str, Any]:
    text = path_text(residents)

    workflow_patterns = [
        r"task_pack", r"astronomicon.*intake|intake.*astronomicon", r"administratum.*registration|registration",
        r"context_pack|context", r"warp[/\\]patches|warp", r"fix[_-]?loop", r"throne.*verdict|verdict"
    ]
    trust_patterns = [r"inquisition", r"custodes", r"trust", r"fake[_-]?green", r"receipt"]
    visibility_patterns = [r"tui", r"dashboard", r"report", r"receipt", r"warning|block"]
    no_core_patterns = [r"no[_-]?core[_-]?mutation", r"external_product", r"before_after_census|census", r"allowed_return|allowed_returns"]

    workflow = signal_score(text, workflow_patterns, cap=len(workflow_patterns))
    trust = signal_score(text, trust_patterns, cap=len(trust_patterns))
    visibility = signal_score(text, visibility_patterns, cap=len(visibility_patterns))
    no_core = signal_score(text, no_core_patterns, cap=len(no_core_patterns))

    # Operational evidence is intentionally strict: it requires both artifacts and organ capabilities.
    actual_task_receipts = len([r for r in residents if "task" in str(r.get("path","")).lower() and str(r.get("class","")).upper() == "RECEIPT"])
    throne_verdict_receipts = len([r for r in residents if "throne" in str(r.get("path","")).lower() and "receipt" in str(r.get("path","")).lower()])
    servitor_evidence = 1 if re.search(r"servitor|officio", text, re.I) else 0
    fix_loop_evidence = 1 if re.search(r"fix[_-]?loop", text, re.I) else 0
    external_product_evidence = 1 if re.search(r"external_product|external[/\\]|product", text, re.I) else 0

    operational_components = {
        "task_receipt_evidence": clamp(actual_task_receipts * 25),
        "throne_verdict_receipt_evidence": clamp(throne_verdict_receipts * 20),
        "servitor_evidence": 100 if servitor_evidence else 0,
        "fix_loop_evidence": 100 if fix_loop_evidence else 0,
        "external_product_evidence": 100 if external_product_evidence else 0,
        "workflow_signal_score": workflow["score"],
    }
    operational_score = weighted(operational_components, {
        "task_receipt_evidence": 20,
        "throne_verdict_receipt_evidence": 20,
        "servitor_evidence": 20,
        "fix_loop_evidence": 15,
        "external_product_evidence": 15,
        "workflow_signal_score": 10,
    })

    return {
        "core_v1_operational_evidence_score": operational_score,
        "core_v1_workflow_readiness_score": workflow["score"],
        "core_v1_trust_readiness_score": trust["score"],
        "core_v1_human_visibility_score": visibility["score"],
        "core_v1_no_core_mutation_evidence_score": no_core["score"],
        "components": operational_components,
        "signals": {"workflow": workflow, "trust": trust, "visibility": visibility, "no_core_mutation": no_core},
        "note": "These are operational evidence signals. They are intentionally stricter than target-definition completeness."
    }

def recommendations(organs: Dict[str,Any], op: Dict[str,Any], target_definition_score: float) -> List[Dict[str,Any]]:
    recs=[]
    def push(priority, area, reason, patch_family):
        recs.append({"priority":priority,"area":area,"reason":reason,"recommended_patch_family":patch_family})
    if target_definition_score >= 90 and op["core_v1_operational_evidence_score"] < 50:
        push(5, "Separate target from operational proof", "Core target is described, but operational evidence is still weak.", "THRONE-CORE-V1-OPERATIONAL-EVIDENCE-0001")
    missing_readme=[o for o,d in organs.items() if o!="THRONE" and "README.md" in d.get("missing_slots",[])]
    missing_manifest=[o for o,d in organs.items() if o!="THRONE" and "MANIFEST.json" in d.get("missing_slots",[])]
    if missing_readme: push(10, "Great Nine README passports", "Missing README: " + ", ".join(missing_readme[:9]), "ORGAN-README-PASSPORT-STAMP-0001")
    if missing_manifest: push(20, "Great Nine manifests", "Missing MANIFEST: " + ", ".join(missing_manifest[:9]), "ORGAN-MANIFEST-STAMP-0001")
    if organs.get("ASTRONOMICON",{}).get("scores",{}).get("organ_readiness_score",100) < 70:
        push(30, "Astronomicon relationship validation", "Astronomicon is entry gate; intake/fix-loop/pass criteria must be measurable.", "THRONE-ASTRONOMICON-RELATIONSHIP-VALIDATION-0001")
    if op["core_v1_trust_readiness_score"] < 60:
        push(40, "Custodes/Inquisition trust proof", "Trust evidence is not deep enough for Core v1.", "CUSTODES-INQUISITION-TRUST-CHAIN-0001")
    low=sorted((d["scores"]["organ_readiness_score"],o) for o,d in organs.items())[0]
    push(60, "Lowest organ readiness: "+low[1], f"{low[1]} readiness is {low[0]}%.", f"{low[1]}-GAP-CLOSURE-0001")
    return sorted(recs, key=lambda x:x["priority"])

def write_outputs(repo: Path, receipt: Dict[str,Any], organs: Dict[str,Any], recs: List[Dict[str,Any]], target_def: Dict[str,Any], op: Dict[str,Any]):
    for p in [repo/RECEIPT.parent, repo/REPORT.parent]:
        p.mkdir(parents=True, exist_ok=True)

    (repo/RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    (repo/NEXT_ATTENTION).write_text(json.dumps(recs, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

    core_breakdown = {
        "task_id": TASK_ID,
        "upgrade_id": UPGRADE_ID,
        "validator_id": VALIDATOR_ID,
        "generated_at_utc": receipt["generated_at_utc"],
        "core_v1_target_definition_score": target_def["score"],
        "matrix_results": target_def["matrix_results"],
        "missing_matrices": target_def["missing"],
        "malformed_matrices": target_def["malformed"]
    }
    (repo/CORE_BREAKDOWN_JSON).write_text(json.dumps(core_breakdown, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

    op_breakdown = {
        "task_id": TASK_ID,
        "upgrade_id": UPGRADE_ID,
        "validator_id": VALIDATOR_ID,
        "generated_at_utc": receipt["generated_at_utc"],
        "core_v1_target_definition_score": target_def["score"],
        **op
    }
    (repo/OP_BREAKDOWN_JSON).write_text(json.dumps(op_breakdown, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

    with (repo/OP_BREAKDOWN_CSV).open("w", encoding="utf-8", newline="") as f:
        fields=["metric","score"]
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for k in [
            "core_v1_target_definition_score",
            "core_v1_operational_evidence_score",
            "core_v1_workflow_readiness_score",
            "core_v1_trust_readiness_score",
            "core_v1_human_visibility_score",
            "core_v1_no_core_mutation_evidence_score"
        ]:
            w.writerow({"metric":k,"score":op_breakdown.get(k)})

    with (repo/CORE_BREAKDOWN_CSV).open("w", encoding="utf-8", newline="") as f:
        fields=["matrix","score","exists","parses","missing_sections"]
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for name,r in target_def["matrix_results"].items():
            w.writerow({"matrix":name,"score":r["score"],"exists":r["exists"],"parses":r["parses"],"missing_sections":";".join(r["missing_sections"])})

    with (repo/ORGAN_CSV).open("w", encoding="utf-8", newline="") as f:
        fields=["organ_id","exists","organ_readiness_score","schemas","validators","receipts","reports","missing_slots","major_gaps"]
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for o,d in organs.items():
            w.writerow({
                "organ_id":o, "exists":d["exists"], "organ_readiness_score":d["scores"]["organ_readiness_score"],
                "schemas":d["evidence_counts"]["schemas"], "validators":d["evidence_counts"]["validators"],
                "receipts":d["evidence_counts"]["receipts"], "reports":d["evidence_counts"]["reports"],
                "missing_slots":"; ".join(d["missing_slots"]), "major_gaps":"; ".join(d["major_gaps"])
            })

    organ_lines = [f"- `{o}`: `{d['scores']['organ_readiness_score']}` — gaps: {', '.join(d['major_gaps'][:6]) or 'none'}" for o,d in sorted(organs.items(), key=lambda kv: kv[1]["scores"]["organ_readiness_score"])]
    rec_lines = [f"{r['priority']}. **{r['area']}** — {r['reason']} → `{r['recommended_patch_family']}`" for r in recs]
    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in receipt["checks"])
    warnings_md = "\n".join(f"- {w}" for w in receipt["warnings"]) if receipt["warnings"] else "- none"
    errors_md = "\n".join(f"- {e}" for e in receipt["errors"]) if receipt["errors"] else "- none"

    report = f"""# THRONE TARGET GAP REPORT V0.3 — CORE V1 OPERATIONAL SPLIT

task_id: `{TASK_ID}`  
upgrade_id: `{UPGRADE_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{receipt['verdict']}`  
mode: `MEASURE_ONLY`  
validation_model: `TARGET_V1_VS_CURRENT_REALITY_WITH_OPERATIONAL_SPLIT`  
generated_at_utc: `{receipt['generated_at_utc']}`

## Global scores

- core_readiness_score: `{receipt['scores']['core_readiness_score']}`
- throne_readiness_score: `{receipt['scores']['throne_readiness_score']}`
- great_nine_readiness_score: `{receipt['scores']['great_nine_readiness_score']}`
- lowest_organ_readiness_score: `{receipt['scores']['lowest_organ_readiness_score']}`

## Core v1 split

- core_v1_target_definition_score: `{receipt['scores']['core_v1_target_definition_score']}`
- core_v1_operational_evidence_score: `{receipt['scores']['core_v1_operational_evidence_score']}`
- core_v1_workflow_readiness_score: `{receipt['scores']['core_v1_workflow_readiness_score']}`
- core_v1_trust_readiness_score: `{receipt['scores']['core_v1_trust_readiness_score']}`
- core_v1_human_visibility_score: `{receipt['scores']['core_v1_human_visibility_score']}`
- core_v1_no_core_mutation_evidence_score: `{receipt['scores']['core_v1_no_core_mutation_evidence_score']}`

## Interpretation

Target definition can be high while operational evidence remains low.

This is expected. The score must not imply near-v1 readiness until workflow, servitor execution, trust chain, fix-loop, human visibility, and no-core-mutation are proven by receipts.

## Organ readiness, lowest first

{chr(10).join(organ_lines)}

## Next attention areas

{chr(10).join(rec_lines) if rec_lines else '- none'}

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}

## Outputs

- `{RECEIPT.as_posix()}`
- `{OP_BREAKDOWN_JSON.as_posix()}`
- `{OP_BREAKDOWN_CSV.as_posix()}`
- `{CORE_BREAKDOWN_JSON.as_posix()}`
- `{CORE_BREAKDOWN_CSV.as_posix()}`
- `{ORGAN_CSV.as_posix()}`
- `{NEXT_ATTENTION.as_posix()}`
"""
    (repo/REPORT).write_text(report, encoding="utf-8")

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--repo-root", default=".")
    repo=Path(ap.parse_args().repo_root).resolve()

    checks=[]; errors=[]; warnings=[]
    required=[TARGET_MATRIX,GAP_SCORING_MATRIX,CORE_V1_SCORING_MATRIX,FIX_MATRIX,CENSUS_JSON]
    missing=[p.as_posix() for p in required if not (repo/p).is_file()]
    add(checks,"required_inputs_exist", not missing, {"missing":missing})
    if missing: errors += [f"Missing input: {p}" for p in missing]

    census={}; summary={}; fix={}
    try:
        if not missing:
            for p in [TARGET_MATRIX,GAP_SCORING_MATRIX,CORE_V1_SCORING_MATRIX,FIX_MATRIX,CENSUS_JSON]:
                read_json(repo/p)
            census=read_json(repo/CENSUS_JSON)
            fix=read_json(repo/FIX_MATRIX)
            if (repo/SUMMARY_JSON).is_file(): summary=read_json(repo/SUMMARY_JSON)
            else: summary=census.get("summary",{})
            add(checks,"input_json_parse", True)
    except Exception as e:
        add(checks,"input_json_parse", False, {"error":str(e)})
        errors.append(f"Input JSON parse failed: {e}")

    residents=census.get("residents",[]) if isinstance(census,dict) else []
    add(checks,"census_has_residents", isinstance(residents,list) and len(residents)>0, {"resident_count":len(residents) if isinstance(residents,list) else None})
    if not isinstance(residents,list) or not residents: errors.append("Census residents missing or empty")

    by=classify_by_owner(residents) if isinstance(residents,list) else {}
    organs={o: compute_organ(repo,o,by) for o in SUBJECTS}

    target_def=compute_target_definition(repo)
    op=compute_operational(repo,residents,organs)

    add(checks,"target_definition_measured", target_def["score"] > 0 and not target_def["malformed"], {"score":target_def["score"],"missing":target_def["missing"],"malformed":target_def["malformed"]})
    if target_def["malformed"]: errors.append("Malformed target definition matrices")
    if target_def["missing"]: warnings.append(f"Missing target definition matrices: {target_def['missing']}")

    comp=fix.get("core_readiness_composition",{})
    comp_weights={
        "target_definition": int(comp.get("target_definition_weight",20)),
        "operational": int(comp.get("operational_evidence_weight",25)),
        "workflow": int(comp.get("workflow_readiness_weight",20)),
        "trust": int(comp.get("trust_readiness_weight",15)),
        "human": int(comp.get("human_visibility_weight",10)),
        "great_nine": int(comp.get("great_nine_readiness_weight",10)),
    }
    add(checks,"fix_scoring_composition_present", bool(comp), {"composition":comp})

    throne=organs["THRONE"]["scores"]["organ_readiness_score"]
    gn=clamp(sum(organs[o]["scores"]["organ_readiness_score"] for o in GREAT_NINE)/len(GREAT_NINE))
    lowest=clamp(min([throne]+[organs[o]["scores"]["organ_readiness_score"] for o in GREAT_NINE]))

    score_inputs={
        "target_definition":target_def["score"],
        "operational":op["core_v1_operational_evidence_score"],
        "workflow":op["core_v1_workflow_readiness_score"],
        "trust":op["core_v1_trust_readiness_score"],
        "human":op["core_v1_human_visibility_score"],
        "great_nine":gn
    }
    core_readiness=weighted(score_inputs, comp_weights)

    guard=fix.get("near_v1_guard",{})
    capped=False
    if guard.get("enabled", True):
        if op["core_v1_operational_evidence_score"] < 50:
            cap=float(guard.get("max_core_score_without_operational_evidence_50",70))
            if core_readiness > cap: core_readiness=cap; capped=True
        if op["core_v1_workflow_readiness_score"] < 50:
            cap=float(guard.get("max_core_score_without_workflow_50",72))
            if core_readiness > cap: core_readiness=cap; capped=True
        if op["core_v1_trust_readiness_score"] < 50:
            cap=float(guard.get("max_core_score_without_trust_50",75))
            if core_readiness > cap: core_readiness=cap; capped=True

    if capped:
        warnings.append("Near-v1 guard capped core_readiness_score because operational/workflow/trust evidence is not deep enough.")

    add(checks,"target_vs_operational_split_present", True, {
        "target_definition": target_def["score"],
        "operational": op["core_v1_operational_evidence_score"],
        "workflow": op["core_v1_workflow_readiness_score"],
        "trust": op["core_v1_trust_readiness_score"],
    })
    add(checks,"near_v1_guard_active", bool(guard.get("enabled", True)), {"capped": capped})

    if core_readiness >= 80 and (op["core_v1_operational_evidence_score"] < 50 or op["core_v1_workflow_readiness_score"] < 50):
        errors.append("Core readiness still near-v1 while operational/workflow evidence is weak")

    recs=recommendations(organs, op, target_def["score"])

    verdict="FAIL_UNMEASURABLE" if errors else "PASS_MEASURED"

    input_hashes={}
    for p in required+[SUMMARY_JSON]:
        apath=repo/p
        if apath.is_file(): input_hashes[p.as_posix()]=sha(apath)

    receipt={
        "receipt_id":"receipt.throne_target_gap.v0_3_core_v1_operational_split",
        "task_id":TASK_ID,
        "upgrade_id":UPGRADE_ID,
        "validator_id":VALIDATOR_ID,
        "verdict":verdict,
        "generated_at_utc":utc(),
        "mode":"MEASURE_ONLY",
        "validation_model":"TARGET_V1_VS_CURRENT_REALITY_WITH_OPERATIONAL_SPLIT",
        "scores":{
            "core_readiness_score":core_readiness,
            "throne_readiness_score":throne,
            "great_nine_readiness_score":gn,
            "lowest_organ_readiness_score":lowest,
            "core_v1_target_definition_score":target_def["score"],
            "core_v1_operational_evidence_score":op["core_v1_operational_evidence_score"],
            "core_v1_workflow_readiness_score":op["core_v1_workflow_readiness_score"],
            "core_v1_trust_readiness_score":op["core_v1_trust_readiness_score"],
            "core_v1_human_visibility_score":op["core_v1_human_visibility_score"],
            "core_v1_no_core_mutation_evidence_score":op["core_v1_no_core_mutation_evidence_score"],
        },
        "target_definition":target_def,
        "operational_breakdown":op,
        "organs":organs,
        "next_attention":recs,
        "input_hashes_sha256":input_hashes,
        "checks":checks,
        "warnings":warnings,
        "errors":errors,
        "meaning":"PASS_MEASURED means target and operational readiness were separated and measured; it does not mean Core v1 is achieved."
    }

    write_outputs(repo, receipt, organs, recs, target_def, op)

    print(json.dumps({
        "task_id":TASK_ID,
        "upgrade_id":UPGRADE_ID,
        "validator_id":VALIDATOR_ID,
        "verdict":verdict,
        "core_readiness_score":core_readiness,
        "throne_readiness_score":throne,
        "great_nine_readiness_score":gn,
        "core_v1_target_definition_score":target_def["score"],
        "core_v1_operational_evidence_score":op["core_v1_operational_evidence_score"],
        "core_v1_workflow_readiness_score":op["core_v1_workflow_readiness_score"],
        "core_v1_trust_readiness_score":op["core_v1_trust_readiness_score"],
        "core_v1_human_visibility_score":op["core_v1_human_visibility_score"],
        "receipt":RECEIPT.as_posix(),
        "report":REPORT.as_posix(),
        "operational_breakdown":OP_BREAKDOWN_JSON.as_posix(),
        "errors":errors
    }, ensure_ascii=False, indent=2))

    return 0 if verdict == "PASS_MEASURED" else 1

if __name__ == "__main__":
    raise SystemExit(main())
