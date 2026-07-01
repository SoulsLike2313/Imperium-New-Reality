#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, json, subprocess, sys
from pathlib import Path

TASK_ID="PATCH-PACK-LIFECYCLE-VALIDATION-FOUNDATION-0001"
VALIDATOR_ID="astronomicon_patch_pack_lifecycle_validation_foundation.v0_1"
CURRENT_PATCH_ID=TASK_ID
MATRIX=Path("ORGANS/ASTRONOMICON/MATRICES/PATCH_PACK_LIFECYCLE_VALIDATION_FOUNDATION_MATRIX_V0_1.json")
DOCTRINE=Path("ORGANS/ASTRONOMICON/DOCTRINE/PATCH_PACK_LIFECYCLE_VALIDATION_FOUNDATION_V0_1.md")
MECH=Path("ORGANS/MECHANICUS/VALIDATORS/validate_patch_pack_technical_preflight.py")
INQ=Path("ORGANS/INQUISITION/VALIDATORS/validate_patch_pack_scope_fake_green.py")
SMOKE=Path("ORGANS/ASTRONOMICON/TOOLS/astronomicon_patch_pack_smoke.py")
RECEIPT=Path("ORGANS/ASTRONOMICON/RECEIPTS/patch_pack_lifecycle_validation_foundation_receipt.json")
REPORT=Path("ORGANS/ASTRONOMICON/REPORTS/PATCH_PACK_LIFECYCLE_VALIDATION_FOUNDATION_REPORT_V0_1.md")
SUMMARY=Path("ORGANS/ASTRONOMICON/REPORTS/PATCH_PACK_LIFECYCLE_VALIDATION_FOUNDATION_SUMMARY_V0_1.json")
SMOKE_OUT=Path("ORGANS/ASTRONOMICON/REPORTS/PATCH_PACK_LIFECYCLE_SMOKE_ALL_SUMMARY_V0_1.json")

def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def head(repo):
    try:
        p=subprocess.run(["git","rev-parse","HEAD"],cwd=repo,capture_output=True,text=True,timeout=15)
        return p.stdout.strip() if p.returncode==0 else "UNKNOWN"
    except Exception: return "UNKNOWN"
def load(p):
    try: return json.loads(p.read_text(encoding="utf-8-sig")),None
    except Exception as e: return None,str(e)
def add(checks,name,ok,details=None):
    checks.append({"name":name,"status":"PASS" if ok else "FAIL","details":details or {}})
def run(repo,script,args):
    p=subprocess.run([sys.executable,str(repo/script)]+args,cwd=repo,capture_output=True,text=True,timeout=180)
    return p.returncode,p.stdout,p.stderr
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo-root",default="."); ap.add_argument("--apply",action="store_true"); args=ap.parse_args()
    repo=Path(args.repo_root).resolve(); checks=[]; errors=[]; warnings=[]
    for r in [MATRIX,DOCTRINE,MECH,INQ,SMOKE]:
        ok=(repo/r).is_file(); add(checks,f"{r.name}_exists",ok,{"path":r.as_posix()})
        if not ok: errors.append(f"missing {r.as_posix()}")
    if (repo/MATRIX).is_file():
        _,err=load(repo/MATRIX); add(checks,"lifecycle_matrix_parses",err is None,{"error":err})
        if err: errors.append("lifecycle matrix parse failed: "+err)
    mech_result={}; inq_result={}; smoke_result={}
    if (repo/MECH).is_file():
        code,out,err=run(repo,MECH,["--repo-root",str(repo),"--patch-id",CURRENT_PATCH_ID])
        add(checks,"mechanicus_preflight_current_patch_runs",code==0,{"stderr":err[-1000:],"stdout_tail":out[-1000:]})
        if code!=0: errors.append("Mechanicus preflight failed")
        mech_result,_=load(repo/"ORGANS/MECHANICUS/RECEIPTS/patch_pack_technical_preflight_receipt.json")
        ok=isinstance(mech_result,dict) and mech_result.get("verdict")=="PASS_TECHNICAL_PREFLIGHT"
        add(checks,"mechanicus_preflight_current_patch_passes",ok,{"verdict":mech_result.get("verdict") if isinstance(mech_result,dict) else None})
        if not ok: errors.append("Mechanicus preflight receipt not PASS")
    if (repo/INQ).is_file():
        code,out,err=run(repo,INQ,["--repo-root",str(repo),"--patch-id",CURRENT_PATCH_ID])
        add(checks,"inquisition_scope_gate_current_patch_runs",code==0,{"stderr":err[-1000:],"stdout_tail":out[-1000:]})
        if code!=0: errors.append("Inquisition scope gate failed")
        inq_result,_=load(repo/"ORGANS/INQUISITION/RECEIPTS/patch_pack_scope_fake_green_receipt.json")
        ok=isinstance(inq_result,dict) and inq_result.get("verdict")=="PASS_SCOPE_FAKE_GREEN_GATE"
        add(checks,"inquisition_scope_gate_current_patch_passes",ok,{"verdict":inq_result.get("verdict") if isinstance(inq_result,dict) else None})
        if not ok: errors.append("Inquisition scope receipt not PASS")
    if (repo/SMOKE).is_file():
        code,out,err=run(repo,SMOKE,["--repo-root",str(repo),"--out",SMOKE_OUT.as_posix()])
        add(checks,"astronomicon_post_work_smoke_runs",code==0,{"stderr":err[-1000:],"stdout_tail":out[-1000:]})
        if code!=0: errors.append("Astronomicon smoke tool failed")
        smoke_result,perr=load(repo/SMOKE_OUT)
        ok=isinstance(smoke_result,dict) and int(smoke_result.get("patch_count",0))>0
        add(checks,"astronomicon_post_work_smoke_scans_patch_packs",ok,{"patch_count":smoke_result.get("patch_count") if isinstance(smoke_result,dict) else None})
        if not ok: errors.append("Astronomicon smoke scanned zero patch packs")
        if isinstance(smoke_result,dict):
            non=[r for r in smoke_result.get("results",[]) if r.get("smoke_verdict")!="CLOSED_BY_DECLARED_GOALS"]
            add(checks,"astronomicon_post_work_smoke_can_refuse_closure",bool(non),{"non_closed_count":len(non)})
            if not non: warnings.append("smoke found no non-closed packs; unusual")
    add(checks,"before_work_validation_available",bool(mech_result) and bool(inq_result),{})
    add(checks,"after_work_smoke_validation_available",bool(smoke_result),{})
    add(checks,"does_not_claim_custodes_or_throne",True,{"custodes":"not claimed","throne":"not claimed"})
    verdict="PASS_PATCH_PACK_LIFECYCLE_VALIDATION_FOUNDATION_READY" if not errors else "FAIL_PATCH_PACK_LIFECYCLE_VALIDATION_FOUNDATION"
    gen=utc()
    summary={"summary_id":"astronomicon.patch_pack_lifecycle_validation_foundation_summary.v0_1","task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"generated_at_utc":gen,"repo_head":head(repo),"before_work_validation":{"mechanicus_preflight":mech_result.get("verdict") if isinstance(mech_result,dict) else None,"inquisition_scope_fake_green":inq_result.get("verdict") if isinstance(inq_result,dict) else None},"after_work_validation":{"astronomicon_smoke_patch_count":smoke_result.get("patch_count") if isinstance(smoke_result,dict) else None,"smoke_summary":SMOKE_OUT.as_posix()},"can_validate_before_work_at_foundation_level":verdict.startswith("PASS"),"can_validate_after_work_at_smoke_level":bool(smoke_result),"not_yet_claimed":["Custodes trust","Throne verdict","full red/blue","full product quality","Valid Servitor Task Pack"],"checks":checks,"errors":errors,"warnings":warnings}
    receipt={"receipt_id":"receipt.astronomicon.patch_pack_lifecycle_validation_foundation.v0_1","task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"generated_at_utc":gen,"repo_head":head(repo),"summary":SUMMARY.as_posix(),"report":REPORT.as_posix(),"checks":checks,"errors":errors,"warnings":warnings,"meaning":"Patch Pack lifecycle now has baseline before-work validation and after-work smoke validation."}
    for p in [SUMMARY,RECEIPT,REPORT]: (repo/p).parent.mkdir(parents=True,exist_ok=True)
    (repo/SUMMARY).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (repo/RECEIPT).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (repo/REPORT).write_text("# PATCH PACK LIFECYCLE VALIDATION FOUNDATION REPORT V0.1\n\nverdict: `"+verdict+"`\n\n## Checks\n\n"+"\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)+"\n\n## Errors\n\n"+("\n".join(f"- {e}" for e in errors) if errors else "- none")+"\n",encoding="utf-8")
    print(json.dumps({"task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"before_work":summary["before_work_validation"],"after_work":summary["after_work_validation"],"receipt":RECEIPT.as_posix(),"summary":SUMMARY.as_posix(),"report":REPORT.as_posix(),"errors":errors,"warnings":warnings},ensure_ascii=False,indent=2))
    return 0 if verdict.startswith("PASS") else 1
if __name__=="__main__": raise SystemExit(main())
