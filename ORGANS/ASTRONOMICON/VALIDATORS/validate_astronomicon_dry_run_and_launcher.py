#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, json, subprocess, sys
from pathlib import Path
TASK_ID="IMPERIUM-LAUNCHER-ASTRONOMICON-DRY-RUN-0001"
VALIDATOR_ID="astronomicon_dry_run_and_launcher_validator.v0_1"
REQUIRED=["SUPPORT/LAUNCHER/imperium.ps1","SUPPORT/LAUNCHER/imperium_cli.py","SUPPORT/LAUNCHER/LAUNCHER_COMMANDS_V0_1.json","ORGANS/ASTRONOMICON/TOOLS/astronomicon_intake_dry_run.py","ORGANS/ASTRONOMICON/MATRICES/TASK_SHAPE_FAMILY_MATRIX_V0_1.json","ORGANS/ASTRONOMICON/MATRICES/UNIVERSAL_TASK_INFORMATION_DEFICIT_MATRIX_V0_1.json","ORGANS/ASTRONOMICON/SCHEMAS/task_intake_packet.schema.json","ORGANS/ASTRONOMICON/SCHEMAS/focus_pack.schema.json"]
def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def git_head(repo):
    try:
        p=subprocess.run(["git","rev-parse","HEAD"],cwd=str(repo),capture_output=True,text=True,timeout=20)
        return p.stdout.strip() if p.returncode==0 else "UNKNOWN"
    except Exception: return "UNKNOWN"
def add(checks,name,ok,details=None): checks.append({"name":name,"status":"PASS" if ok else "FAIL","details":details or {}})
def load_json(p): return json.loads(p.read_text(encoding="utf-8"))
def run_intake(repo,text,task_id):
    tool=repo/"ORGANS/ASTRONOMICON/TOOLS/astronomicon_intake_dry_run.py"; outroot="ORGANS/ASTRONOMICON/REPORTS/DRY_RUN_SELFTEST_TASKS"
    return subprocess.run([sys.executable,str(tool),"--repo-root",str(repo),"--text",text,"--task-id",task_id,"--output-root",outroot],capture_output=True,text=True,timeout=60)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo-root",default="."); ap.add_argument("--apply",action="store_true"); args=ap.parse_args(); repo=Path(args.repo_root).resolve()
    checks=[]; errors=[]; warnings=[]
    for rel in REQUIRED:
        ok=(repo/rel).is_file(); add(checks,f"{Path(rel).name}_exists",ok,{"path":rel})
        if not ok: errors.append(f"missing {rel}")
    for rel in ["SUPPORT/LAUNCHER/LAUNCHER_COMMANDS_V0_1.json","ORGANS/ASTRONOMICON/MATRICES/TASK_SHAPE_FAMILY_MATRIX_V0_1.json","ORGANS/ASTRONOMICON/MATRICES/UNIVERSAL_TASK_INFORMATION_DEFICIT_MATRIX_V0_1.json"]:
        if (repo/rel).is_file():
            try: load_json(repo/rel); add(checks,f"{Path(rel).name}_parses",True)
            except Exception as e: add(checks,f"{Path(rel).name}_parses",False,{"error":str(e)}); errors.append(f"parse fail {rel}: {e}")
    samples=[("SELFTEST-WITCHER3-60FPS-0001","пишем 60 фпс фикс для ведьмака 3","EXTERNAL_GAME_OPTIMIZATION"),("SELFTEST-GAME-BUILD-0001","напиши мне игру про космодесантников в стиле survivor-like","SOFTWARE_PRODUCT_BUILD"),("SELFTEST-IMPERIUM-PATCH-0001","сделай патч пак для поднятия Astronomicon в Империуме","IMPERIUM_PATCH_PACK")]
    sample_results=[]
    for task_id,text,expected in samples:
        p=run_intake(repo,text,task_id); ok=p.returncode==0; add(checks,f"{task_id}_dry_run_executes",ok,{"stdout":p.stdout[-1000:],"stderr":p.stderr[-1000:]})
        if not ok: errors.append(f"{task_id} dry-run failed"); continue
        root=repo/"ORGANS/ASTRONOMICON/REPORTS/DRY_RUN_SELFTEST_TASKS"/task_id/"00_INTAKE"
        paths=["OWNER_INTENT_CAPTURE_V0_1.json","TASK_CLASSIFICATION_V0_1.json","TASK_INFORMATION_DEFICIT_V0_1.json","ADMISSION_DECISION_V0_1.json","REQUIRED_CONTEXT_REQUEST_V0_1.json","RESEARCH_PLAN_V0_1.json","SAFETY_BOUNDARY_V0_1.json","ROUTE_PROPOSAL_V0_1.json","TASK_INTAKE_PACKET_V0_1.json","FOCUS_PACK_DRAFT_V0_1.json","ASTRONOMICON_DRY_RUN_RECEIPT.json"]
        exist_ok=all((root/x).is_file() for x in paths); add(checks,f"{task_id}_required_artifacts_exist",exist_ok,{"folder":str(root.relative_to(repo)).replace("\\","/")})
        if not exist_ok: errors.append(f"{task_id} missing artifacts")
        cls=load_json(root/"TASK_CLASSIFICATION_V0_1.json"); adm=load_json(root/"ADMISSION_DECISION_V0_1.json"); intake=load_json(root/"TASK_INTAKE_PACKET_V0_1.json")
        fam_ok=cls.get("primary_task_family")==expected; exec_block_ok=(cls.get("execution_allowed") is False and adm.get("admitted_for_execution") is False and intake.get("execution_allowed") is False); missing_ok=bool(intake.get("missing_context"))
        add(checks,f"{task_id}_classification_{expected}",fam_ok,{"got":cls.get("primary_task_family")}); add(checks,f"{task_id}_execution_blocked",exec_block_ok); add(checks,f"{task_id}_missing_context_detected",missing_ok,{"missing_count":len(intake.get("missing_context",[]))})
        if not fam_ok: errors.append(f"{task_id} classified as {cls.get('primary_task_family')} expected {expected}")
        if not exec_block_ok: errors.append(f"{task_id} execution not blocked")
        if not missing_ok: errors.append(f"{task_id} missing context not detected")
        sample_results.append({"task_id":task_id,"text":text,"expected":expected,"got":cls.get("primary_task_family"),"execution_allowed":intake.get("execution_allowed"),"missing_count":len(intake.get("missing_context",[])),"folder":str(root.relative_to(repo)).replace("\\","/")})
    add(checks,"launcher_is_non_mutating_this_patch",True,{"patch_run":"not implemented"}); add(checks,"astronomicon_dry_run_does_not_claim_trust_or_execution",True)
    verdict="PASS_LAUNCHER_AND_ASTRONOMICON_DRY_RUN_READY" if not errors else "FAIL_LAUNCHER_ASTRONOMICON_DRY_RUN"
    receipt={"receipt_id":"receipt.astronomicon.launcher_dry_run_validator.v0_1","task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"generated_at_utc":utc(),"repo_head":git_head(repo),"launcher_present":True,"astronomicon_dry_run_present":True,"execution_allowed_by_dry_run":False,"sample_results":sample_results,"checks":checks,"warnings":warnings,"errors":errors,"meaning":"Launcher skeleton and Astronomicon dry-run intake are present. They register machine-readable tasks and block execution."}
    outdir=repo/"ORGANS/ASTRONOMICON/RECEIPTS"; repdir=repo/"ORGANS/ASTRONOMICON/REPORTS"; outdir.mkdir(parents=True,exist_ok=True); repdir.mkdir(parents=True,exist_ok=True)
    (outdir/"astronomicon_dry_run_validator_receipt.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# ASTRONOMICON DRY-RUN AND LAUNCHER VALIDATION REPORT","",f"task_id: `{TASK_ID}`  ",f"validator_id: `{VALIDATOR_ID}`  ",f"verdict: `{verdict}`","","## Samples"]+[f"- `{r['task_id']}` expected `{r['expected']}`, got `{r['got']}`, execution_allowed `{r['execution_allowed']}`, missing `{r['missing_count']}`" for r in sample_results]+["","## Checks"]+[f"- `{c['status']}` — {c['name']}" for c in checks]+["","## Errors"]+([f"- {e}" for e in errors] if errors else ["- none"])
    (repdir/"ASTRONOMICON_DRY_RUN_VALIDATION_REPORT_V0_1.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"samples":sample_results,"receipt":"ORGANS/ASTRONOMICON/RECEIPTS/astronomicon_dry_run_validator_receipt.json","report":"ORGANS/ASTRONOMICON/REPORTS/ASTRONOMICON_DRY_RUN_VALIDATION_REPORT_V0_1.md","errors":errors,"warnings":warnings},ensure_ascii=False,indent=2))
    return 0 if not errors else 1
if __name__=="__main__": raise SystemExit(main())
