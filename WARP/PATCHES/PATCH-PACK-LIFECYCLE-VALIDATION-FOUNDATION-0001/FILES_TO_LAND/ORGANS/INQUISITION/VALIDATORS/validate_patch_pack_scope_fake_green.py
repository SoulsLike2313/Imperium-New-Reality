#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, json, re, subprocess
from pathlib import Path

TASK_ID="PATCH-PACK-LIFECYCLE-VALIDATION-FOUNDATION-0001"
VALIDATOR_ID="inquisition_patch_pack_scope_fake_green_gate.v0_1"
RECEIPT=Path("ORGANS/INQUISITION/RECEIPTS/patch_pack_scope_fake_green_receipt.json")
REPORT=Path("ORGANS/INQUISITION/REPORTS/PATCH_PACK_SCOPE_FAKE_GREEN_REPORT_V0_1.md")
SUMMARY=Path("ORGANS/INQUISITION/REPORTS/PATCH_PACK_SCOPE_FAKE_GREEN_SUMMARY_V0_1.json")
ALLOWED=("ORGANS/","SUPPORT/","WARP/")
BAD_RUN=[r"\bgit\s+(push|commit|pull)\b",r"\b(Invoke-Expression|iex|Invoke-WebRequest|iwr|Invoke-RestMethod|irm)\b"]
BAD_FAKE=[r"receipt\s+existence\s*(==|=|is)\s*work\s+done",r"smoke\s+validation\s*(==|=|is)\s*(trust|throne)",r"self[- ]?validator\s*(==|=|is)\s*trust"]
HIGH=["TRUST_PROVEN","THRONE_VERDICT","CUSTODES_TRUST","ORGAN_ASSEMBLED","NO_CORE_MUTATION_PROVEN"]

def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def head(repo):
    try:
        p=subprocess.run(["git","rev-parse","HEAD"],cwd=repo,capture_output=True,text=True,timeout=15)
        return p.stdout.strip() if p.returncode==0 else "UNKNOWN"
    except Exception: return "UNKNOWN"
def rel(repo,p):
    try: return p.relative_to(repo).as_posix()
    except Exception: return p.as_posix()
def read(p):
    try: return p.read_text(encoding="utf-8",errors="replace")
    except Exception: return ""
def patch_dirs(repo,patch_id):
    root=repo/"WARP/PATCHES"
    if patch_id:
        p=root/patch_id
        return [p] if p.is_dir() else []
    return sorted([p for p in root.iterdir() if p.is_dir()]) if root.is_dir() else []
def scan(repo,patch_dir):
    errors=[]; warnings=[]; checks=[]
    def add(name,ok,details=None,sev="error"):
        checks.append({"name":name,"status":"PASS" if ok else "FAIL","details":details or {},"severity":sev})
        if not ok: (errors if sev=="error" else warnings).append(name)
    pp=patch_dir/"PATCH_PACK.md"; ftl=patch_dir/"FILES_TO_LAND"; runners=list(patch_dir.glob("RUN_*.ps1")); doc=read(pp)
    add("expected_verdict_or_output_declared",bool(re.search(r"(PASS|FAIL|WARN|PARTIAL)[_A-Z0-9-]*",doc)),{"path":rel(repo,pp)},"warning")
    vio=[]
    for r in runners:
        txt=read(r)
        for pat in BAD_RUN:
            if re.search(pat,txt,re.I): vio.append({"runner":rel(repo,r),"pattern":pat})
    add("runner_no_owner_authority_or_remote_exec",not vio,{"violations":vio[:10]})
    scope=[]; trav=[]
    if ftl.is_dir():
        for f in ftl.rglob("*"):
            if not f.is_file(): continue
            rp=f.relative_to(ftl).as_posix()
            if ".." in Path(rp).parts: trav.append(rp)
            if not rp.startswith(ALLOWED): scope.append(rp)
    add("files_to_land_no_path_traversal",not trav,{"violations":trav[:10]})
    add("files_to_land_allowed_roots",not scope,{"violations":scope[:20],"allowed_roots":ALLOWED})
    alltxt=doc+"\n"+"\n".join(read(r) for r in runners)
    fake=[pat for pat in BAD_FAKE if re.search(pat,alltxt,re.I)]
    add("no_receipt_equals_work_done_claim",not fake,{"patterns":fake})
    high=[]
    upper=doc.upper()
    for term in HIGH:
        if term in upper:
            i=upper.find(term); win=upper[max(0,i-80):i+len(term)+80]
            if not any(n in win for n in ["NOT","MUST NOT","DOES NOT","CANNOT","CAN NOT","NOT_YET"]): high.append({"term":term,"window":win})
    add("no_trust_throne_assembly_claim",not high,{"hits":high[:10]})
    verdict="PASS_SCOPE_FAKE_GREEN_GATE" if not errors else "FAIL_SCOPE_FAKE_GREEN_GATE"
    return {"patch_id":patch_dir.name,"path":rel(repo,patch_dir),"verdict":verdict,"checks":checks,"errors":errors,"warnings":warnings}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo-root",default="."); ap.add_argument("--patch-id"); ap.add_argument("--all",action="store_true"); ap.add_argument("--fail-on-errors",action="store_true"); args=ap.parse_args()
    repo=Path(args.repo_root).resolve(); results=[scan(repo,d) for d in patch_dirs(repo,args.patch_id if not args.all else None)]
    err=sum(len(r["errors"]) for r in results); pc=sum(1 for r in results if r["verdict"]=="PASS_SCOPE_FAKE_GREEN_GATE")
    verdict="PASS_SCOPE_FAKE_GREEN_GATE" if err==0 else ("FAIL_SCOPE_FAKE_GREEN_GATE" if (args.patch_id or args.fail_on_errors) else "WARN_SCOPE_FAKE_GREEN_PARTIAL")
    gen=utc()
    summary={"summary_id":"inquisition.patch_pack_scope_fake_green_summary.v0_1","task_id":TASK_ID,"validator_id":VALIDATOR_ID,"generated_at_utc":gen,"repo_head":head(repo),"target_patch_id":args.patch_id,"patch_count":len(results),"pass_count":pc,"error_count":err,"verdict":verdict,"results":results}
    receipt={k:summary[k] for k in ["task_id","validator_id","verdict","generated_at_utc","repo_head","target_patch_id","patch_count","pass_count","error_count"]}; receipt.update({"receipt_id":"receipt.inquisition.patch_pack_scope_fake_green.v0_1","summary":SUMMARY.as_posix(),"report":REPORT.as_posix(),"errors":[e for r in results for e in r["errors"]],"warnings":[w for r in results for w in r["warnings"]]})
    for p in [SUMMARY,RECEIPT,REPORT]: (repo/p).parent.mkdir(parents=True,exist_ok=True)
    (repo/SUMMARY).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (repo/RECEIPT).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (repo/REPORT).write_text("# PATCH PACK SCOPE / FAKE-GREEN GATE REPORT V0.1\n\nverdict: `"+verdict+"`\n\n"+"\n".join(f"- `{r['patch_id']}` — `{r['verdict']}`" for r in results[:80])+"\n",encoding="utf-8")
    print(json.dumps({"task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"target_patch_id":args.patch_id,"patch_count":len(results),"pass_count":pc,"error_count":err,"receipt":RECEIPT.as_posix(),"summary":SUMMARY.as_posix(),"errors":receipt["errors"][:20],"warnings":receipt["warnings"][:20]},ensure_ascii=False,indent=2))
    return 0 if verdict=="PASS_SCOPE_FAKE_GREEN_GATE" or (not args.patch_id and not args.fail_on_errors) else 1
if __name__=="__main__": raise SystemExit(main())
