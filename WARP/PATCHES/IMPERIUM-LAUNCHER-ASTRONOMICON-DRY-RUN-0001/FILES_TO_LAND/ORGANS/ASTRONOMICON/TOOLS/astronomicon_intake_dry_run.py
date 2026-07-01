#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, re
from pathlib import Path
from typing import Any, Dict, List, Tuple

PATCH_ID="IMPERIUM-LAUNCHER-ASTRONOMICON-DRY-RUN-0001"
MATRIX_REL=Path("ORGANS/ASTRONOMICON/MATRICES/TASK_SHAPE_FAMILY_MATRIX_V0_1.json")
DEFICIT_REL=Path("ORGANS/ASTRONOMICON/MATRICES/UNIVERSAL_TASK_INFORMATION_DEFICIT_MATRIX_V0_1.json")
def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def slug(s,n=32):
    s=s.lower()
    for k,v in {"ведьмак":"witcher","игра":"game","игру":"game","фпс":"fps","патч":"patch","империум":"imperium","валидатор":"validator"}.items(): s=s.replace(k,v)
    s=re.sub(r"[^a-z0-9]+","-",s).strip("-")
    return (s[:n].strip("-") or "task").upper()
def load(repo,rel): return json.loads((repo/rel).read_text(encoding="utf-8"))
def contains_any(text, words): return any(w.lower() in text for w in words)
def classify(text,matrix):
    t=text.lower(); best=("UNKNOWN_RESEARCH_REQUIRED",0.20,matrix["families"][-1])
    for fam in matrix["families"]:
        if fam["task_family"]=="UNKNOWN_RESEARCH_REQUIRED": continue
        v=contains_any(t,fam.get("verbs",[])); target=contains_any(t,fam.get("targets",[]))
        score=(0.45 if v else 0)+(0.45 if target else 0)
        if fam["task_family"]=="EXTERNAL_GAME_OPTIMIZATION" and (("fps" in t or "фпс" in t or "кадр" in t) and ("witcher" in t or "ведьмак" in t or "game" in t or "игр" in t)): score=0.92
        if fam["task_family"]=="IMPERIUM_PATCH_PACK" and ("imperium" in t or "империум" in t or "warp" in t): score=max(score,0.86)
        if fam["task_family"]=="SOFTWARE_PRODUCT_BUILD" and (("напиши" in t or "создай" in t or "сделай" in t) and ("игр" in t or "game" in t or "прилож" in t)): score=max(score,0.82)
        if score>best[1]: best=(fam["task_family"],round(min(score,0.99),2),fam)
    return best
def detect_goal(text,family):
    return {"EXTERNAL_GAME_OPTIMIZATION":"Create a safe measurable optimization task for stable performance without unsafe mutation.","SOFTWARE_PRODUCT_BUILD":"Create a product build task that requires a brief, scope, platform, references, and validation plan.","IMPERIUM_PATCH_PACK":"Create an Imperium WARP patch planning task with validators, receipts, and no fake green.","REPO_AUDIT":"Create a read-only repository audit task with evidence requirements.","MEDIA_PROMPT_BUILD":"Create a structured media prompt/build task with constraints and output format."}.get(family,"Determine task shape through research and owner clarification.")
def known_context(text,family):
    t=text.lower(); known={"raw_text_available":True}
    if "witcher" in t or "ведьмак" in t: known["target_product"]="The Witcher 3 Wild Hunt"
    if "60" in t and ("fps" in t or "фпс" in t or "кадр" in t): known["target_fps"]=60
    if "1080" in t: known["resolution"]="1080p"
    if "ультра" in t or "ultra" in t: known["quality_preset"]="ultra"
    if "империум" in t or "imperium" in t: known["target_system"]="Imperium"
    if "патч" in t or "patch" in t: known["patch_intent_detected"]=True
    if family=="SOFTWARE_PRODUCT_BUILD" and ("игр" in t or "game" in t): known["target_product_class"]="game"
    return known
def build_missing(family,text,deficit,known):
    req=list(deficit["universal_required_fields"])+list(deficit["family_specific_requirements"].get(family,[])); present=set()
    if known.get("target_product") or known.get("target_product_class") or known.get("target_system"): present.add("target_object")
    if text.strip(): present.add("owner_goal")
    if known.get("target_fps"): present.add("success_criteria")
    return [x for x in req if x not in present]
def research_queries(family,text,known):
    if family=="EXTERNAL_GAME_OPTIMIZATION":
        target=known.get("target_product","target game")
        return [f"{target} graphics settings config file location",f"{target} safe performance optimization settings mods benchmark",f"{target} DX11 DX12 user settings performance impact",f"{target} modded install backup config files"]
    if family=="SOFTWARE_PRODUCT_BUILD": return ["product brief template game development","vertical slice definition game prototype","game build validation checklist"]
    if family=="IMPERIUM_PATCH_PACK": return ["Imperium local doctrine receipts validators patch pack","current repository WARP patch conventions"]
    if family=="REPO_AUDIT": return ["repository audit checklist static analysis risk categories","read-only code audit evidence report format"]
    return ["determine task shape requirements","domain-specific task intake checklist"]
def route(family):
    common=[("ASTRONOMICON","capture intent, classify task, request missing context"),("ADMINISTRATUM","register task and index context/receipts")]
    if family=="EXTERNAL_GAME_OPTIMIZATION":
        rest=[("STRATEGIUM","plan benchmark and optimization sequence"),("MECHANICUS","collect hardware/game/mod/baseline data and prepare safe tools"),("OFFICIO_AGENTIS","prepare narrow LLM/servitor work order"),("INQUISITION","attack placebo, unsafe changes, fake benchmark, broken-mod risk"),("CUSTODES","verify permission, backup, allowed paths, trust chain"),("THRONE","issue crown verdict from before/after evidence")]
    elif family=="IMPERIUM_PATCH_PACK":
        rest=[("STRATEGIUM","plan patch scope and order"),("MECHANICUS","build/run validators and technical checks"),("INQUISITION","attack fake green and scope violations"),("CUSTODES","verify trust/permission boundaries"),("THRONE","crown final receipt and score interpretation")]
    else:
        rest=[("STRATEGIUM","plan task after missing context is filled"),("MECHANICUS","prepare tools/validators when scope is known"),("INQUISITION","challenge unsafe or fake-green claims"),("CUSTODES","verify permission/trust before mutation"),("THRONE","confirm only with evidence")]
    return [{"organ":o,"role":r} for o,r in common+rest]
def write_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def make_task(repo,text,task_id=None,output_root=None):
    matrix=load(repo,MATRIX_REL); deficit=load(repo,DEFICIT_REL); family,confidence,fam=classify(text,matrix)
    if not task_id: task_id=f"{slug(text)}-{hashlib.sha1(text.encode('utf-8')).hexdigest()[:8].upper()}"
    root=repo/(output_root or "WARP/TASKS")/task_id/"00_INTAKE"; generated=utc(); known=known_context(text,family); missing=build_missing(family,text,deficit,known); admission=fam.get("default_admission","NEEDS_TASK_SHAPE_RESEARCH")
    files={}
    files["OWNER_INTENT_CAPTURE_V0_1.json"]={"artifact_id":"OWNER_INTENT_CAPTURE_V0_1","task_id":task_id,"generated_at_utc":generated,"raw_owner_text":text,"normalized_owner_goal":detect_goal(text,family),"known_context":known,"unknowns":missing,"owner_lock_required":True}
    files["TASK_CLASSIFICATION_V0_1.json"]={"artifact_id":"TASK_CLASSIFICATION_V0_1","task_id":task_id,"primary_task_family":family,"classification_confidence":confidence,"execution_allowed":False,"classification_method":"rule_matrix_v0_1","matrix":MATRIX_REL.as_posix(),"research_required":family=="UNKNOWN_RESEARCH_REQUIRED" or confidence<0.80}
    files["TASK_INFORMATION_DEFICIT_V0_1.json"]={"artifact_id":"TASK_INFORMATION_DEFICIT_V0_1","task_id":task_id,"task_family":family,"missing_context":missing,"known_context":known,"blocking_missing_context":missing[:],"execution_blocked":True}
    files["ADMISSION_DECISION_V0_1.json"]={"artifact_id":"ADMISSION_DECISION_V0_1","task_id":task_id,"decision":admission,"admitted_for_planning":True,"admitted_for_execution":False,"reason":"Dry-run intake never permits execution. Missing context must be filled and validated before mutation.","blocked_until":missing}
    files["REQUIRED_CONTEXT_REQUEST_V0_1.json"]={"artifact_id":"REQUIRED_CONTEXT_REQUEST_V0_1","task_id":task_id,"required_files":[{"name":f"{x.upper()}_V0_1.json","purpose":f"Provide/derive required context: {x}"} for x in missing],"optional_files":["owner examples","reference screenshots","manual notes","links or source bundle"],"execution_allowed_after_collection":False}
    files["RESEARCH_PLAN_V0_1.json"]={"artifact_id":"RESEARCH_PLAN_V0_1","task_id":task_id,"research_required":files["TASK_CLASSIFICATION_V0_1.json"]["research_required"] or bool(missing),"queries":research_queries(family,text,known),"must_extract":missing,"must_not_do":["execute web commands","download random binaries","mutate files","trust one source","claim success from research"],"execution_allowed_after_research":False}
    files["SAFETY_BOUNDARY_V0_1.json"]={"artifact_id":"SAFETY_BOUNDARY_V0_1","task_id":task_id,"mutation_allowed_now":False,"allowed_now":["classification","planning","context request","research planning","receipt generation"],"forbidden_now":["file mutation outside this dry-run task folder","external execution","patch run","final verdict","trust claim"],"future_mutation_requires":["allowed scope","backup/rollback","validators","Custodes trust","Throne verdict"]}
    files["ROUTE_PROPOSAL_V0_1.json"]={"artifact_id":"ROUTE_PROPOSAL_V0_1","task_id":task_id,"route":route(family),"route_state":"PROPOSED_NOT_EXECUTED"}
    files["TASK_INTAKE_PACKET_V0_1.json"]={"artifact_id":"TASK_INTAKE_PACKET_V0_1","task_id":task_id,"title":f"{family}: {text[:80]}","owner_goal":detect_goal(text,family),"raw_owner_text":text,"task_family":family,"admission_state":admission,"execution_allowed":False,"known_context":known,"success_criteria":["success metric must be explicit","validation evidence required","no final claim without receipt"],"hard_constraints":files["SAFETY_BOUNDARY_V0_1.json"]["forbidden_now"],"missing_context":missing,"next_required_action":"fill required context or run research intake; execution remains blocked"}
    files["FOCUS_PACK_DRAFT_V0_1.json"]={"artifact_id":"FOCUS_PACK_DRAFT_V0_1","task_id":task_id,"llm_role":"task-shape analyst, not executor","goal":detect_goal(text,family),"known_context":known,"missing_context":missing,"allowed_output":["questions","research plan","context checklist","risk list","non-executing plan"],"forbidden_output":["final fix","mutation commands","trust claim","Throne verdict","unsafe broad scope"],"stop_conditions":missing}
    for name,data in files.items(): write_json(root/name,data)
    receipt={"receipt_id":"receipt.astronomicon.dry_run_intake.v0_1","task_id":task_id,"patch_id":PATCH_ID,"organ_id":"ASTRONOMICON","generated_at_utc":generated,"verdict":"PASS_DRY_RUN_INTAKE_REGISTERED","task_family":family,"classification_confidence":confidence,"execution_allowed":False,"task_folder":str(root.relative_to(repo)).replace("\\","/"),"files":[str((root/n).relative_to(repo)).replace("\\","/") for n in files],"errors":[],"meaning":"Astronomicon registered a machine-readable dry-run task. It did not execute or mutate the target."}
    write_json(root/"ASTRONOMICON_DRY_RUN_RECEIPT.json",receipt)
    report=f"# ASTRONOMICON DRY-RUN INTAKE REPORT\n\ntask_id: `{task_id}`  \nverdict: `PASS_DRY_RUN_INTAKE_REGISTERED`  \ntask_family: `{family}`  \nconfidence: `{confidence}`  \nexecution_allowed: `False`\n\n## Owner text\n\n```text\n{text}\n```\n\n## Missing context\n\n"+"\n".join(f"- `{m}`" for m in missing)+"\n\n## Next\n\nFill required context or research task shape. No execution is allowed by this dry-run.\n"
    (root/"ASTRONOMICON_TASK_INTAKE_REPORT.md").write_text(report,encoding="utf-8")
    return {"task_id":task_id,"task_family":family,"confidence":confidence,"execution_allowed":False,"task_folder":str(root.relative_to(repo)).replace("\\","/"),"receipt":str((root/"ASTRONOMICON_DRY_RUN_RECEIPT.json").relative_to(repo)).replace("\\","/"),"missing_context":missing}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo-root",default="."); ap.add_argument("--text",required=True); ap.add_argument("--task-id"); ap.add_argument("--output-root")
    args=ap.parse_args(); print(json.dumps(make_task(Path(args.repo_root).resolve(),args.text,args.task_id,args.output_root),ensure_ascii=False,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
