#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse, csv, datetime as dt, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

TASK_ID = "THRONE-TARGET-GAP-VALIDATOR-0001"
UPGRADE_ID = "THRONE-TARGET-GAP-CORE-V1-SCORING-INTEGRATION-0001"
VALIDATOR_ID = "throne_target_gap_validator.v0_2_core_v1_scoring"

THRONE = Path("ORGANS/THRONE")
TARGET_MATRIX = THRONE / "MATRICES/THRONE_TARGET_V1_MATRIX_V0_1.json"
SCORING_MATRIX = THRONE / "MATRICES/THRONE_TARGET_GAP_SCORING_MATRIX_V0_1.json"
CORE_V1_SCORING_MATRIX = THRONE / "MATRICES/THRONE_TARGET_GAP_CORE_V1_SCORING_INTEGRATION_MATRIX_V0_1.json"

CENSUS_JSON = Path("WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/OUTPUTS/IMPERIUM_POPULATION_CENSUS_V0_1.json")
SUMMARY_JSON = Path("WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/OUTPUTS/IMPERIUM_POPULATION_SUMMARY_V0_1.json")
GAP_JSON = Path("WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/OUTPUTS/IMPERIUM_POPULATION_GAP_MAP_V0_1.json")

RECEIPT = THRONE / "RECEIPTS/throne_target_gap_receipt.json"
REPORT = THRONE / "REPORTS/THRONE_TARGET_GAP_REPORT_V0_1.md"
READINESS_CSV = THRONE / "REPORTS/THRONE_ORGAN_READINESS_TABLE_V0_1.csv"
NEXT_ATTENTION = THRONE / "REPORTS/THRONE_NEXT_ATTENTION_AREAS_V0_1.json"
CORE_V1_BREAKDOWN_JSON = THRONE / "REPORTS/THRONE_CORE_V1_READINESS_BREAKDOWN_V0_1.json"
CORE_V1_BREAKDOWN_CSV = THRONE / "REPORTS/THRONE_CORE_V1_READINESS_BREAKDOWN_V0_1.csv"

DEFAULT_REQUIRED_SLOTS = ["README.md","ORGAN_CARD.json","MANIFEST.json","FUNCTIONS.md","MATRICES","SCHEMAS","VALIDATORS","RECEIPTS","REPORTS","TESTS","TUI","DASHBOARDS","EYES","BLOCK","LESSONS","NEGATIVE_LESSONS"]
GREAT_NINE = ["ASTRONOMICON","ADMINISTRATUM","DOCTRINARIUM","MECHANICUS","INQUISITION","CUSTODES","STRATEGIUM","SCHOLA_IMPERIALIS","OFFICIO_AGENTIS"]
SUBJECTS = ["THRONE"] + GREAT_NINE

DEFAULT_WEIGHTS = {
 "physical_presence_score":10,"required_slot_score":15,"identity_score":10,"manifest_score":10,
 "schema_coverage_score":10,"validator_coverage_score":15,"receipt_coverage_score":10,
 "boundary_lifecycle_score":10,"observability_score":5,"trust_action_readiness_score":5,
}

CORE_MATRIX_REQUIRED = {
 "THRONE_KERNEL_ANATOMY_MATRIX_V0_1.json":["kernel_identity","organ_kernel_roles","external_kernel_lessons","non_goals"],
 "THRONE_CORE_V1_DEFINITION_MATRIX_V0_1.json":["oath","must_capabilities","v1_gate","benchmark_policy"],
 "THRONE_KERNEL_BOUNDARY_MATRIX_V0_1.json":["zones","allowed_returns","forbidden_mutations","proof_requirements"],
 "THRONE_REQUEST_PACKET_MATRIX_V0_1.json":["packet_types","task_pack_required_fields","patch_pack_required_fields","routing_rules"],
 "THRONE_OBJECT_REGISTRY_MATRIX_V0_1.json":["registered_object_classes","required_fields","registry_owner"],
 "THRONE_ORGAN_SERVICE_STACK_MATRIX_V0_1.json":["default_task_stack","default_patch_stack","stack_law"],
 "THRONE_SERVITOR_EXECUTION_BOUNDARY_MATRIX_V0_1.json":["servitor_identity","allowed","forbidden","stop_conditions"],
 "THRONE_EVIDENCE_CHAIN_MATRIX_V0_1.json":["chain","minimum_evidence","fake_green_guards"],
 "THRONE_TRUST_BOUNDARY_MATRIX_V0_1.json":["trust_layers","required_questions","verdict_rules"],
 "THRONE_INTEGRATION_KERNEL_MATRIX_V0_1.json":["integration_states","admission_path","kernel_rights_rule"],
 "THRONE_HUMAN_READABILITY_MATRIX_V0_1.json":["tui_v1_must","human_translation_fields","non_goals"],
 "THRONE_CORE_V1_READINESS_SCORING_MATRIX_V0_1.json":["dimensions","v1_gate_logic"],
}

def utc_now(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def read_json(path: Path): return json.loads(path.read_text(encoding="utf-8"))
def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda:f.read(1024*1024), b""): h.update(c)
    return h.hexdigest()
def add_check(checks, name, passed, details=None): checks.append({"name":name,"status":"PASS" if passed else "FAIL","details":details or {}})
def clamp(x: float) -> float: return round(max(0.0, min(100.0, x)), 2)
def score_bool(v: bool) -> float: return 100.0 if v else 0.0
def weighted(scores: Dict[str,float], weights: Dict[str,int]) -> float:
    tw=sum(weights.values()) or 1
    return clamp(sum(scores.get(k,0.0)*w for k,w in weights.items())/tw)
def organ_path(organ: str) -> Path: return THRONE if organ == "THRONE" else Path("ORGANS")/organ

def classify_residents_by_owner(residents):
    by=defaultdict(list)
    for r in residents:
        owner=str(r.get("owner_candidate") or "UNKNOWN")
        by[owner].append(r)
        if organ_path("THRONE").as_posix() in str(r.get("path", "")) and owner != "THRONE": by["THRONE"].append(r)
    return by

def count_classes(items): return Counter(str(r.get("class") or "UNKNOWN") for r in items)

def organ_slot_score(root: Path, required_slots: List[str], repo_root: Path):
    present=[]; missing=[]
    for slot in required_slots:
        if (repo_root/root/slot).exists(): present.append(slot)
        else: missing.append(slot)
    return clamp(len(present)*100.0/max(1,len(required_slots))), present, missing

def parse_json_if_exists(path: Path) -> bool:
    if not path.is_file(): return False
    try: read_json(path); return True
    except Exception: return False

def coverage_score(count:int, target:int): return clamp(count*100.0/max(1,target))

def compute_organ(repo_root: Path, organ: str, by_owner, required_slots, weights):
    root=organ_path(organ); abs_root=repo_root/root; exists=abs_root.is_dir()
    slot_score,present_slots,missing_slots = organ_slot_score(root, required_slots, repo_root) if exists else (0.0, [], required_slots)
    identity_ok=parse_json_if_exists(abs_root/"ORGAN_CARD.json")
    manifest_ok=parse_json_if_exists(abs_root/"MANIFEST.json")
    functions_ok=(abs_root/"FUNCTIONS.md").is_file()
    items=by_owner.get(organ, [])
    cc=count_classes(items)
    schema_count=cc.get("SCHEMA",0); validator_count=cc.get("VALIDATOR",0); receipt_count=cc.get("RECEIPT",0); report_count=cc.get("REPORT",0); matrix_count=cc.get("MATRIX",0)
    has_warp=any(str(r.get("status"))=="WARP" for r in items)
    has_negative=any(str(r.get("status"))=="NEGATIVE_EXAMPLE" for r in items)
    has_quarantine=any(str(r.get("status"))=="QUARANTINE" for r in items)
    obs=[(abs_root/"TUI").exists(),(abs_root/"DASHBOARDS").exists(),(abs_root/"EYES").exists(),(abs_root/"REPORTS").exists()]
    trust=[validator_count>0,receipt_count>0,matrix_count>0,functions_ok]
    scores={
      "physical_presence_score":score_bool(exists),
      "required_slot_score":slot_score,
      "identity_score":score_bool(identity_ok),
      "manifest_score":score_bool(manifest_ok),
      "schema_coverage_score":coverage_score(schema_count,3),
      "validator_coverage_score":coverage_score(validator_count,2),
      "receipt_coverage_score":coverage_score(receipt_count,3),
      "boundary_lifecycle_score":100.0 if exists and not has_warp else 70.0 if exists else 0.0,
      "observability_score":clamp(sum(1 for x in obs if x)*100.0/len(obs)),
      "trust_action_readiness_score":clamp(sum(1 for x in trust if x)*100.0/len(trust)),
    }
    scores["organ_readiness_score"]=weighted(scores, weights)
    gaps=[]
    if not exists: gaps.append("organ directory missing")
    for f in ["README.md","ORGAN_CARD.json","MANIFEST.json","FUNCTIONS.md"]:
        if f in missing_slots: gaps.append(f"missing {f}")
    if schema_count==0: gaps.append("no schema evidence")
    if validator_count==0: gaps.append("no validator evidence")
    if receipt_count==0: gaps.append("no receipt evidence")
    if has_warp: gaps.append("has WARP-status residents")
    if has_quarantine: gaps.append("has quarantine residents")
    if has_negative: gaps.append("has negative-example residents")
    return {"organ_id":organ,"path":root.as_posix(),"exists":exists,"scores":scores,"present_slots":present_slots,"missing_slots":missing_slots,"evidence_counts":{"residents":len(items),"schemas":schema_count,"validators":validator_count,"receipts":receipt_count,"reports":report_count,"matrices":matrix_count},"major_gaps":gaps[:30]}

def score_matrix_file(repo_root: Path, filename: str, required_sections: List[str]):
    path=repo_root/THRONE/"MATRICES"/filename
    res={"matrix":filename,"path":(THRONE/"MATRICES"/filename).as_posix(),"exists":False,"parses":False,"required_sections":required_sections,"present_sections":[],"missing_sections":list(required_sections),"sha256":None,"score":0.0,"errors":[]}
    if not path.is_file(): res["errors"].append("matrix missing"); return res
    res["exists"]=True; res["sha256"]=sha256_file(path)
    try: data=read_json(path); res["parses"]=True
    except Exception as exc: res["errors"].append(f"json parse failed: {exc}"); res["score"]=20.0; return res
    present=[s for s in required_sections if s in data]
    missing=[s for s in required_sections if s not in data]
    res["present_sections"]=present; res["missing_sections"]=missing
    base=40.0; section_score=len(present)*50.0/max(1,len(required_sections)); substance_bonus=10.0 if len(json.dumps(data, ensure_ascii=False))>400 else 0.0
    res["score"]=clamp(base+section_score+substance_bonus)
    return res

def compute_core_v1_anatomy(repo_root: Path, integration: Dict[str,Any]):
    matrix_to_zone=integration.get("matrix_to_score_zone", {})
    zone_weights=integration.get("core_v1_anatomy_weights", {})
    required_zones=integration.get("required_score_zones", [])
    zone_items=defaultdict(list); matrix_results={}
    for filename, required_sections in CORE_MATRIX_REQUIRED.items():
        res=score_matrix_file(repo_root, filename, required_sections); matrix_results[filename]=res
        zone=matrix_to_zone.get(filename)
        if zone: zone_items[zone].append(res["score"])
    zones={}
    for zone in required_zones:
        vals=zone_items.get(zone, [])
        zones[zone]={"score":clamp(sum(vals)/len(vals)) if vals else 0.0,"evidence_count":len(vals),"weight":zone_weights.get(zone,1),"status":"MEASURED" if vals else "MISSING_EVIDENCE"}
    no_core_vals=[]
    for name in ["THRONE_KERNEL_BOUNDARY_MATRIX_V0_1.json","THRONE_CORE_V1_DEFINITION_MATRIX_V0_1.json"]:
        if name in matrix_results: no_core_vals.append(matrix_results[name].get("score",0.0))
    if "no_core_mutation_score" in zones:
        zones["no_core_mutation_score"]["score"]=clamp(sum(no_core_vals)/len(no_core_vals)) if no_core_vals else 0.0
        zones["no_core_mutation_score"]["evidence_count"]=len(no_core_vals)
        zones["no_core_mutation_score"]["status"]="MEASURED" if no_core_vals else "MISSING_EVIDENCE"
    anatomy_score=weighted({z:float(d["score"]) for z,d in zones.items()}, {z:int(d["weight"]) for z,d in zones.items()})
    return {"core_v1_anatomy_readiness_score":anatomy_score,"zones":zones,"matrix_results":matrix_results,"missing_matrices":[n for n,r in matrix_results.items() if not r["exists"]],"malformed_matrices":[n for n,r in matrix_results.items() if r["exists"] and not r["parses"]],"missing_sections":{n:r["missing_sections"] for n,r in matrix_results.items() if r["missing_sections"]}}

def recommend(organs, census_summary, core_v1):
    recs=[]
    def push(priority, area, reason, patch_family): recs.append({"priority":priority,"area":area,"reason":reason,"recommended_patch_family":patch_family})
    missing_readme=[o for o,d in organs.items() if "README.md" in d.get("missing_slots",[]) and o!="THRONE"]
    missing_manifest=[o for o,d in organs.items() if "MANIFEST.json" in d.get("missing_slots",[]) and o!="THRONE"]
    low_organs=sorted((d["scores"]["organ_readiness_score"],o) for o,d in organs.items())
    if missing_readme: push(10,"Great Nine README passports",f"Missing README: {', '.join(missing_readme[:9])}","ORGAN-README-PASSPORT-STAMP-0001")
    if missing_manifest: push(20,"Great Nine manifests",f"Missing MANIFEST: {', '.join(missing_manifest[:9])}","ORGAN-MANIFEST-STAMP-0001")
    low_zones=sorted((d["score"],z) for z,d in core_v1.get("zones",{}).items())
    if low_zones:
        score,zone=low_zones[0]
        if score<100: push(25,f"Core v1 zone hardening: {zone}",f"{zone} is {score}%.","THRONE-CORE-V1-ZONE-HARDENING-0001")
    if organs.get("ASTRONOMICON",{}).get("scores",{}).get("organ_readiness_score",100)<70: push(30,"Astronomicon relationship validation","Astronomicon is entry gate; intake/fix-loop/pass criteria must be made measurable.","THRONE-ASTRONOMICON-RELATIONSHIP-VALIDATION-0001")
    if organs.get("CUSTODES",{}).get("scores",{}).get("organ_readiness_score",100)<50: push(40,"Custodes trust layer","Custodes readiness is low; organ validator trust cannot be audited deeply yet.","CUSTODES-TRUST-LAYER-0001")
    if census_summary.get("validator_count",0) < census_summary.get("schema_count",0): push(50,"Schema-validator coverage","Schema count exceeds validator count; declaration/evidence gap is visible.","SCHEMA-VALIDATOR-COVERAGE-0001")
    if low_organs:
        score,organ=low_organs[0]; push(60,f"Lowest organ readiness: {organ}",f"{organ} readiness is {score}%.",f"{organ}-GAP-CLOSURE-0001")
    return sorted(recs, key=lambda r:r["priority"])

def write_outputs(repo_root, receipt, organs, next_attention, core_v1):
    for p in [repo_root/RECEIPT.parent, repo_root/REPORT.parent]: p.mkdir(parents=True, exist_ok=True)
    (repo_root/RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    (repo_root/NEXT_ATTENTION).write_text(json.dumps(next_attention, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    breakdown={"task_id":TASK_ID,"upgrade_id":UPGRADE_ID,"validator_id":VALIDATOR_ID,"generated_at_utc":receipt["generated_at_utc"],"core_v1_anatomy_readiness_score":core_v1["core_v1_anatomy_readiness_score"],"zones":core_v1["zones"],"missing_matrices":core_v1["missing_matrices"],"malformed_matrices":core_v1["malformed_matrices"],"missing_sections":core_v1["missing_sections"]}
    (repo_root/CORE_V1_BREAKDOWN_JSON).write_text(json.dumps(breakdown, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    with (repo_root/CORE_V1_BREAKDOWN_CSV).open("w",encoding="utf-8",newline="") as f:
        wr=csv.DictWriter(f, fieldnames=["zone","score","weight","evidence_count","status"]); wr.writeheader()
        for z,d in core_v1["zones"].items(): wr.writerow({"zone":z,"score":d["score"],"weight":d["weight"],"evidence_count":d["evidence_count"],"status":d["status"]})
    with (repo_root/READINESS_CSV).open("w",encoding="utf-8",newline="") as f:
        fields=["organ_id","exists","organ_readiness_score","physical_presence_score","required_slot_score","identity_score","manifest_score","schema_coverage_score","validator_coverage_score","receipt_coverage_score","boundary_lifecycle_score","observability_score","trust_action_readiness_score","schemas","validators","receipts","reports","missing_slots","major_gaps"]
        wr=csv.DictWriter(f, fieldnames=fields); wr.writeheader()
        for organ,data in organs.items():
            row={"organ_id":organ,"exists":data["exists"],"schemas":data["evidence_counts"]["schemas"],"validators":data["evidence_counts"]["validators"],"receipts":data["evidence_counts"]["receipts"],"reports":data["evidence_counts"]["reports"],"missing_slots":"; ".join(data["missing_slots"]),"major_gaps":"; ".join(data["major_gaps"])}
            row.update(data["scores"]); wr.writerow(row)
    organ_lines=[f"- `{o}`: `{d['scores']['organ_readiness_score']}` — gaps: {', '.join(d['major_gaps'][:6]) or 'none'}" for o,d in sorted(organs.items(), key=lambda kv: kv[1]["scores"]["organ_readiness_score"])]
    zone_lines=[f"- `{z}`: `{d['score']}` — evidence: `{d['evidence_count']}`, status: `{d['status']}`" for z,d in sorted(core_v1["zones"].items(), key=lambda kv: kv[1]["score"])]
    rec_lines=[f"{r['priority']}. **{r['area']}** — {r['reason']} → `{r['recommended_patch_family']}`" for r in next_attention]
    checks_md="\n".join(f"- `{c['status']}` — {c['name']}" for c in receipt["checks"])
    warnings_md="\n".join(f"- {w}" for w in receipt.get("warnings", [])) if receipt.get("warnings") else "- none"
    errors_md="\n".join(f"- {e}" for e in receipt["errors"]) if receipt["errors"] else "- none"
    report=f"""# THRONE TARGET GAP REPORT V0.2 — CORE V1 SCORING INTEGRATED

task_id: `{TASK_ID}`  
upgrade_id: `{UPGRADE_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{receipt['verdict']}`  
mode: `MEASURE_ONLY`  
validation_model: `TARGET_V1_VS_CURRENT_REALITY_WITH_CORE_V1_ANATOMY`  
generated_at_utc: `{receipt['generated_at_utc']}`

## Global scores

- core_readiness_score: `{receipt['scores']['core_readiness_score']}`
- throne_readiness_score: `{receipt['scores']['throne_readiness_score']}`
- great_nine_readiness_score: `{receipt['scores']['great_nine_readiness_score']}`
- core_v1_anatomy_readiness_score: `{receipt['scores']['core_v1_anatomy_readiness_score']}`
- lowest_organ_readiness_score: `{receipt['scores']['lowest_organ_readiness_score']}`

## Core v1 anatomy zones, lowest first

{chr(10).join(zone_lines)}

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
- `{READINESS_CSV.as_posix()}`
- `{NEXT_ATTENTION.as_posix()}`
- `{CORE_V1_BREAKDOWN_JSON.as_posix()}`
- `{CORE_V1_BREAKDOWN_CSV.as_posix()}`

## Meaning

This report does not claim Imperium Core v1 is achieved.

It proves the Throne target-gap radar now includes Core v1 meta-kernel anatomy in its scoring.
"""
    (repo_root/REPORT).write_text(report, encoding="utf-8")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo-root", default="."); args=ap.parse_args(); repo_root=Path(args.repo_root).resolve()
    checks=[]; errors=[]; warnings=[]
    required=[TARGET_MATRIX, SCORING_MATRIX, CORE_V1_SCORING_MATRIX, CENSUS_JSON]
    missing=[p.as_posix() for p in required if not (repo_root/p).is_file()]
    add_check(checks,"required_inputs_exist", not missing, {"missing":missing})
    if missing: errors += [f"Missing input: {p}" for p in missing]
    target=scoring=integration=census={}; census_summary={}; census_gaps={}
    try:
        if not missing:
            target=read_json(repo_root/TARGET_MATRIX); scoring=read_json(repo_root/SCORING_MATRIX); integration=read_json(repo_root/CORE_V1_SCORING_MATRIX); census=read_json(repo_root/CENSUS_JSON)
            census_summary=read_json(repo_root/SUMMARY_JSON) if (repo_root/SUMMARY_JSON).is_file() else census.get("summary", {})
            census_gaps=read_json(repo_root/GAP_JSON) if (repo_root/GAP_JSON).is_file() else census.get("gaps", {})
            add_check(checks,"input_json_parse", True)
    except Exception as exc:
        add_check(checks,"input_json_parse", False, {"error":str(exc)}); errors.append(f"Input JSON parse failed: {exc}")
    residents=census.get("residents", []) if isinstance(census, dict) else []
    add_check(checks,"census_has_residents", isinstance(residents, list) and len(residents)>0, {"resident_count":len(residents) if isinstance(residents, list) else None})
    if not isinstance(residents, list) or not residents: errors.append("Census residents missing or empty")
    weights=scoring.get("weights", DEFAULT_WEIGHTS) if isinstance(scoring, dict) else DEFAULT_WEIGHTS
    required_slots=scoring.get("required_slots", DEFAULT_REQUIRED_SLOTS) if isinstance(scoring, dict) else DEFAULT_REQUIRED_SLOTS
    add_check(checks,"scoring_matrix_has_weights", all(k in weights for k in DEFAULT_WEIGHTS), {"weights":weights})
    if not all(k in weights for k in DEFAULT_WEIGHTS): errors.append("Scoring matrix missing required weights")
    composition=integration.get("core_readiness_composition", {}) if isinstance(integration, dict) else {}
    composition_ok=all(k in composition for k in ["throne_structural_readiness_weight","great_nine_readiness_weight","core_v1_anatomy_readiness_weight"])
    add_check(checks,"core_v1_scoring_composition_present", composition_ok, {"composition":composition})
    if not composition_ok: errors.append("Core v1 scoring composition missing")
    add_check(checks,"target_matrix_exists_and_mentions_target", bool(target), {"target_keys":list(target.keys())[:20] if isinstance(target, dict) else []})
    if not target: errors.append("Target matrix empty")
    by_owner=classify_residents_by_owner(residents) if isinstance(residents, list) else {}
    organs={organ:compute_organ(repo_root, organ, by_owner, required_slots, weights) for organ in SUBJECTS}
    core_v1=compute_core_v1_anatomy(repo_root, integration if isinstance(integration, dict) else {})
    add_check(checks,"core_v1_anatomy_matrices_measured", not core_v1["missing_matrices"] and not core_v1["malformed_matrices"], {"missing_matrices":core_v1["missing_matrices"],"malformed_matrices":core_v1["malformed_matrices"]})
    if core_v1["missing_matrices"]: warnings.append(f"Missing Core v1 matrices: {core_v1['missing_matrices']}")
    if core_v1["malformed_matrices"]: errors.append(f"Malformed Core v1 matrices: {core_v1['malformed_matrices']}")
    throne_score=organs["THRONE"]["scores"]["organ_readiness_score"]
    great_nine_scores=[organs[o]["scores"]["organ_readiness_score"] for o in GREAT_NINE]
    great_nine_readiness=clamp(sum(great_nine_scores)/len(great_nine_scores))
    lowest=clamp(min([throne_score]+great_nine_scores))
    core_v1_score=core_v1["core_v1_anatomy_readiness_score"]
    if composition_ok:
        comp={"throne":int(composition["throne_structural_readiness_weight"]),"great_nine":int(composition["great_nine_readiness_weight"]),"core_v1":int(composition["core_v1_anatomy_readiness_weight"])}
        core_readiness=weighted({"throne":throne_score,"great_nine":great_nine_readiness,"core_v1":core_v1_score}, comp)
    else:
        core_readiness=clamp((throne_score*0.2)+(great_nine_readiness*0.3)+(core_v1_score*0.5))
    next_attention=recommend(organs, census_summary, core_v1)
    all_100=all(d["scores"]["organ_readiness_score"]==100 for d in organs.values()) and core_v1_score==100
    add_check(checks,"fake_green_guard_not_all_100", not all_100, {})
    if all_100: errors.append("Fake-green suspicion: all organs and Core v1 anatomy scored 100")
    if core_readiness < 100: warnings.append("Core readiness below target v1; this is expected and measured.")
    verdict="FAIL_UNMEASURABLE" if errors else "PASS_MEASURED"
    input_hashes={}
    for p in [TARGET_MATRIX,SCORING_MATRIX,CORE_V1_SCORING_MATRIX,CENSUS_JSON,SUMMARY_JSON,GAP_JSON]:
        apath=repo_root/p
        if apath.is_file(): input_hashes[p.as_posix()]=sha256_file(apath)
    receipt={"receipt_id":"receipt.throne_target_gap.v0_2_core_v1_scoring","task_id":TASK_ID,"upgrade_id":UPGRADE_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"generated_at_utc":utc_now(),"mode":"MEASURE_ONLY","validation_model":"TARGET_V1_VS_CURRENT_REALITY_WITH_CORE_V1_ANATOMY","scores":{"core_readiness_score":core_readiness,"throne_readiness_score":throne_score,"great_nine_readiness_score":great_nine_readiness,"core_v1_anatomy_readiness_score":core_v1_score,"lowest_organ_readiness_score":lowest},"core_v1_anatomy":core_v1,"organs":organs,"next_attention":next_attention,"input_hashes_sha256":input_hashes,"checks":checks,"warnings":warnings,"errors":errors,"meaning":"PASS_MEASURED means the target gap was measured with Core v1 anatomy scoring, not that Core v1 is achieved."}
    write_outputs(repo_root, receipt, organs, next_attention, core_v1)
    print(json.dumps({"task_id":TASK_ID,"upgrade_id":UPGRADE_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"core_readiness_score":core_readiness,"throne_readiness_score":throne_score,"great_nine_readiness_score":great_nine_readiness,"core_v1_anatomy_readiness_score":core_v1_score,"lowest_organ_readiness_score":lowest,"receipt":RECEIPT.as_posix(),"report":REPORT.as_posix(),"core_v1_breakdown":CORE_V1_BREAKDOWN_JSON.as_posix(),"errors":errors}, ensure_ascii=False, indent=2))
    return 0 if verdict in {"PASS_MEASURED","WARN_PARTIAL_EVIDENCE"} else 1

if __name__ == "__main__":
    raise SystemExit(main())
