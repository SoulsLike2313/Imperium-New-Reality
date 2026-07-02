#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, subprocess, sys
from pathlib import Path
from typing import Any, Dict, List, Tuple
TASK_ID="ASTRONOMICON-RED-BLUE-HARDENING-AND-SCAN-ISOLATION-0001"
VALIDATOR_ID="astronomicon_red_blue_hardening_scan_isolation_validator.v0_1"
INQ_SCAN=Path("ORGANS/INQUISITION/TOOLS/red_blue_team_skills_scan.py")
HARDENING_TOOL=Path("ORGANS/ASTRONOMICON/TOOLS/astronomicon_red_blue_hardening.py")
MATRIX=Path("ORGANS/ASTRONOMICON/RED_BLUE/ASTRONOMICON_RED_BLUE_HARDENING_MATRIX_V0_1.json")
CASES=Path("ORGANS/ASTRONOMICON/RED_BLUE/ASTRONOMICON_RED_BLUE_HARDENING_CASES_V0_1.json")
GLOBAL_SCAN=Path("ORGANS/INQUISITION/REPORTS/RED_BLUE_TEAM_SKILLS_SCAN_SUMMARY_V0_1.json")
SINGLE_SCAN=Path("ORGANS/INQUISITION/REPORTS/RED_BLUE_TEAM_SKILLS_SCAN_ASTRONOMICON_V0_1.json")
RECEIPT=Path("ORGANS/ASTRONOMICON/RECEIPTS/astronomicon_red_blue_hardening_scan_isolation_receipt.json")
SUMMARY=Path("ORGANS/ASTRONOMICON/REPORTS/ASTRONOMICON_RED_BLUE_HARDENING_SCAN_ISOLATION_SUMMARY_V0_1.json")
REPORT=Path("ORGANS/ASTRONOMICON/REPORTS/ASTRONOMICON_RED_BLUE_HARDENING_SCAN_ISOLATION_REPORT_V0_1.md")
def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def git_head(repo:Path):
    try:
        p=subprocess.run(["git","rev-parse","HEAD"],cwd=str(repo),capture_output=True,text=True,timeout=15)
        return p.stdout.strip() if p.returncode==0 else "UNKNOWN"
    except Exception: return "UNKNOWN"
def sha(path:Path): return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
def load_json(path:Path):
    try: return json.loads(path.read_text(encoding="utf-8-sig")), None
    except Exception as e: return None, str(e)
def add(checks,name,ok,details=None): checks.append({"name":name,"status":"PASS" if ok else "FAIL","details":details or {}})
def run_py(repo,script,args):
    p=subprocess.run([sys.executable,str(repo/script)]+args,cwd=str(repo),capture_output=True,text=True,timeout=120)
    return p.returncode,p.stdout,p.stderr
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo-root",default="."); ap.add_argument("--apply",action="store_true"); args=ap.parse_args(); repo=Path(args.repo_root).resolve()
    checks=[]; errors=[]; warnings=[]
    for rel in [INQ_SCAN,HARDENING_TOOL,MATRIX,CASES]:
        ok=(repo/rel).is_file(); add(checks,f"{rel.name}_exists",ok,{"path":rel.as_posix()})
        if not ok: errors.append(f"missing {rel.as_posix()}")
    matrix,matrix_err=load_json(repo/MATRIX) if (repo/MATRIX).is_file() else ({},"missing"); add(checks,"astronomicon_red_blue_matrix_parses",matrix_err is None,{"error":matrix_err})
    cases,cases_err=load_json(repo/CASES) if (repo/CASES).is_file() else ({},"missing"); add(checks,"astronomicon_red_blue_cases_parse",cases_err is None,{"error":cases_err})
    if matrix_err: errors.append("hardening matrix parse failed")
    if cases_err: errors.append("hardening cases parse failed")
    code,out,err=run_py(repo,INQ_SCAN,["--repo-root",str(repo)]); add(checks,"global_redblue_scan_runs",code==0,{"stderr":err[-1000:]})
    if code!=0: errors.append("global redblue scan failed")
    global_hash_before=sha(repo/GLOBAL_SCAN); global_data,global_err=load_json(repo/GLOBAL_SCAN)
    add(checks,"global_redblue_summary_has_10_organs",global_err is None and isinstance(global_data,dict) and global_data.get("organ_count")==10,{"error":global_err,"organ_count":global_data.get("organ_count") if isinstance(global_data,dict) else None})
    if global_err is not None or not isinstance(global_data,dict) or global_data.get("organ_count")!=10: errors.append("global redblue summary does not have 10 organs")
    if (repo/SINGLE_SCAN).exists(): (repo/SINGLE_SCAN).unlink()
    code,out,err=run_py(repo,INQ_SCAN,["--repo-root",str(repo),"--organ","ASTRONOMICON"]); add(checks,"single_organ_redblue_scan_runs",code==0,{"stderr":err[-1000:]})
    if code!=0: errors.append("single organ redblue scan failed")
    global_hash_after=sha(repo/GLOBAL_SCAN); add(checks,"single_organ_scan_does_not_overwrite_global_summary",global_hash_before==global_hash_after,{"before":global_hash_before,"after":global_hash_after})
    if global_hash_before!=global_hash_after: errors.append("single organ redblue scan overwrote global summary")
    single_data,single_err=load_json(repo/SINGLE_SCAN); add(checks,"single_organ_scan_writes_isolated_astronomicon_summary",single_err is None and isinstance(single_data,dict) and single_data.get("organ_count")==1 and single_data.get("target_organ")=="ASTRONOMICON",{"error":single_err,"organ_count":single_data.get("organ_count") if isinstance(single_data,dict) else None})
    if single_err is not None or not isinstance(single_data,dict) or single_data.get("organ_count")!=1: errors.append("single organ isolated scan invalid")
    code,out,err=run_py(repo,HARDENING_TOOL,["--repo-root",str(repo)]); add(checks,"astronomicon_red_blue_hardening_tool_runs",code==0,{"stderr":err[-1000:]})
    if code!=0: errors.append("Astronomicon redblue hardening tool failed")
    hardening,hard_err=load_json(repo/"ORGANS/ASTRONOMICON/REPORTS/ASTRONOMICON_RED_BLUE_HARDENING_SUMMARY_V0_1.json"); add(checks,"astronomicon_red_blue_hardening_summary_parses",hard_err is None,{"error":hard_err})
    if hard_err: errors.append("Astronomicon hardening summary parse failed"); hardening={}
    add(checks,"astronomicon_red_blue_local_scores_pass_threshold",hardening.get("red_local_hardening_score",0)>=80 and hardening.get("blue_local_hardening_score",0)>=80,{"red":hardening.get("red_local_hardening_score"),"blue":hardening.get("blue_local_hardening_score")})
    if hardening.get("red_local_hardening_score",0)<80 or hardening.get("blue_local_hardening_score",0)<80: errors.append("Astronomicon local red/blue hardening scores below threshold")
    add(checks,"proof_scores_remain_zero",hardening.get("red_team_proven_score")==0.0 and hardening.get("blue_team_proven_score")==0.0 and hardening.get("custodes_validation_score")==0.0 and hardening.get("throne_confirmation_score")==0.0,{"red_team_proven_score":hardening.get("red_team_proven_score"),"blue_team_proven_score":hardening.get("blue_team_proven_score"),"custodes_validation_score":hardening.get("custodes_validation_score"),"throne_confirmation_score":hardening.get("throne_confirmation_score")})
    if hardening.get("red_team_proven_score")!=0.0 or hardening.get("blue_team_proven_score")!=0.0: errors.append("red/blue proof scores should remain zero")
    code,out,err=run_py(repo,INQ_SCAN,["--repo-root",str(repo)]); add(checks,"global_redblue_scan_restored_after_test",code==0,{"stderr":err[-1000:]})
    if code!=0: errors.append("failed to restore global redblue scan")
    verdict="PASS_ASTRONOMICON_RED_BLUE_HARDENED_AND_SCAN_ISOLATED" if not errors else "FAIL_ASTRONOMICON_RED_BLUE_HARDENING_AND_SCAN_ISOLATION"; generated=utc()
    summary={"summary_id":"astronomicon.red_blue_hardening_scan_isolation_validation_summary.v0_1","task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"generated_at_utc":generated,"repo_head":git_head(repo),"target_organ":"ASTRONOMICON","red_local_hardening_score":hardening.get("red_local_hardening_score"),"blue_local_hardening_score":hardening.get("blue_local_hardening_score"),"red_team_proven_score":hardening.get("red_team_proven_score"),"blue_team_proven_score":hardening.get("blue_team_proven_score"),"custodes_validation_score":hardening.get("custodes_validation_score"),"throne_confirmation_score":hardening.get("throne_confirmation_score"),"checks":checks,"errors":errors,"warnings":warnings,"next_layer":"CUSTODES-ASTRONOMICON-VALIDATION-0001"}
    receipt={"receipt_id":"receipt.astronomicon.red_blue_hardening_scan_isolation.v0_1","task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"generated_at_utc":generated,"summary":SUMMARY.as_posix(),"report":REPORT.as_posix(),"checks":checks,"errors":errors,"warnings":warnings,"meaning":"Astronomicon local Red/Blue hardened and Red/Blue scan isolation fixed. Custodes/Throne remain next."}
    for p in [SUMMARY,RECEIPT,REPORT]: (repo/p).parent.mkdir(parents=True,exist_ok=True)
    (repo/SUMMARY).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); (repo/RECEIPT).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    checks_md="\n".join(f"- `{c['status']}` — {c['name']}" for c in checks); errors_md="\n".join(f"- {e}" for e in errors) if errors else "- none"; warnings_md="\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo/REPORT).write_text(f"""# ASTRONOMICON RED + BLUE HARDENING AND SCAN ISOLATION REPORT V0.1\n\ntask_id: `{TASK_ID}`  \nvalidator_id: `{VALIDATOR_ID}`  \nverdict: `{verdict}`  \ngenerated_at_utc: `{generated}`  \nrepo_head: `{git_head(repo)}`\n\n## Meaning\n\nAstronomicon Red/Blue is locally hardened by profile-specific red cases and blue guards.\n\nThe Red/Blue scan output isolation bug is also closed: single-organ scan writes isolated output and does not overwrite global 10-organ scan summary.\n\n## Scores\n\n- red_local_hardening_score: `{hardening.get('red_local_hardening_score')}`\n- blue_local_hardening_score: `{hardening.get('blue_local_hardening_score')}`\n- red_team_proven_score: `{hardening.get('red_team_proven_score')}`\n- blue_team_proven_score: `{hardening.get('blue_team_proven_score')}`\n- custodes_validation_score: `{hardening.get('custodes_validation_score')}`\n- throne_confirmation_score: `{hardening.get('throne_confirmation_score')}`\n\n## Next\n\n`CUSTODES-ASTRONOMICON-VALIDATION-0001`\n\n## Checks\n\n{checks_md}\n\n## Warnings\n\n{warnings_md}\n\n## Errors\n\n{errors_md}\n""",encoding="utf-8")
    print(json.dumps({"task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"target_organ":"ASTRONOMICON","red_local_hardening_score":hardening.get("red_local_hardening_score"),"blue_local_hardening_score":hardening.get("blue_local_hardening_score"),"red_team_proven_score":hardening.get("red_team_proven_score"),"blue_team_proven_score":hardening.get("blue_team_proven_score"),"custodes_validation_score":hardening.get("custodes_validation_score"),"throne_confirmation_score":hardening.get("throne_confirmation_score"),"receipt":RECEIPT.as_posix(),"summary":SUMMARY.as_posix(),"report":REPORT.as_posix(),"errors":errors,"warnings":warnings},ensure_ascii=False,indent=2)); return 0 if verdict.startswith("PASS") else 1
if __name__=="__main__": raise SystemExit(main())
