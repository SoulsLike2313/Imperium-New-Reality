#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, py_compile, re, subprocess
from pathlib import Path

TASK_ID="PATCH-PACK-LIFECYCLE-VALIDATION-FOUNDATION-0001"
VALIDATOR_ID="mechanicus_patch_pack_technical_preflight.v0_1"
RECEIPT=Path("ORGANS/MECHANICUS/RECEIPTS/patch_pack_technical_preflight_receipt.json")
REPORT=Path("ORGANS/MECHANICUS/REPORTS/PATCH_PACK_TECHNICAL_PREFLIGHT_REPORT_V0_1.md")
SUMMARY=Path("ORGANS/MECHANICUS/REPORTS/PATCH_PACK_TECHNICAL_PREFLIGHT_SUMMARY_V0_1.json")
BAD=[r"\bgit\s+(push|commit|pull)\b",r"\b(Invoke-Expression|iex|Invoke-WebRequest|iwr|Invoke-RestMethod|irm)\b",r"\bcurl\s+.*\|\s*(iex|powershell|pwsh|sh|bash)\b"]

def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def head(repo):
    try:
        p=subprocess.run(["git","rev-parse","HEAD"],cwd=repo,capture_output=True,text=True,timeout=15)
        return p.stdout.strip() if p.returncode==0 else "UNKNOWN"
    except Exception: return "UNKNOWN"
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""): h.update(b)
    return h.hexdigest()
def rel(repo,p):
    try: return p.relative_to(repo).as_posix()
    except Exception: return p.as_posix()
def load(p):
    try: return json.loads(p.read_text(encoding="utf-8-sig")),None
    except Exception as e: return None,str(e)
def patch_dirs(repo,patch_id):
    root=repo/"WARP/PATCHES"
    if patch_id:
        p=root/patch_id
        return [p] if p.is_dir() else []
    return sorted([p for p in root.iterdir() if p.is_dir()]) if root.is_dir() else []
def resolve(repo,patch_dir,s):
    s=str(s).replace("\\","/")
    c=[]
    if s.startswith(("WARP/","ORGANS/","SUPPORT/")): c.append(repo/s)
    c.append(patch_dir/s)
    needle=f"WARP/PATCHES/{patch_dir.name}/"
    if needle in s: c.append(repo/s[s.index(needle):])
    for x in c:
        if x.exists(): return x
    return c[0]
def scan(repo,patch_dir):
    errors=[]; warnings=[]; checks=[]
    def add(name,ok,details=None,sev="error"):
        checks.append({"name":name,"status":"PASS" if ok else "FAIL","details":details or {},"severity":sev})
        if not ok: (errors if sev=="error" else warnings).append(name)
    pp=patch_dir/"PATCH_PACK.md"; man=patch_dir/"PATCH_FILE_MANIFEST_SHA256.json"; ftl=patch_dir/"FILES_TO_LAND"; runners=list(patch_dir.glob("RUN_*.ps1"))
    add("patch_pack_doc_exists",pp.is_file(),{"path":rel(repo,pp)})
    add("runner_exists",bool(runners),{"runners":[rel(repo,x) for x in runners]})
    add("files_to_land_exists",ftl.is_dir(),{"path":rel(repo,ftl)})
    add("sha256_manifest_exists",man.is_file(),{"path":rel(repo,man)})
    if man.is_file():
        data,err=load(man); add("manifest_parses_as_list",err is None and isinstance(data,list),{"error":err})
        missing=[]; hash_bad=[]; byte_bad=[]; checked=0
        if isinstance(data,list):
            for row in data:
                if not isinstance(row,dict) or "path" not in row: continue
                target=resolve(repo,patch_dir,row["path"])
                if target.resolve()==man.resolve(): continue
                if not target.is_file(): missing.append(row["path"]); continue
                checked+=1
                if "bytes" in row and int(row["bytes"])!=target.stat().st_size: byte_bad.append(row["path"])
                if "sha256" in row and str(row["sha256"]).lower()!=sha(target).lower(): hash_bad.append(row["path"])
        add("manifest_paths_resolve",not missing,{"missing_count":len(missing),"sample":missing[:10]})
        add("manifest_hashes_match",not hash_bad,{"mismatch_count":len(hash_bad),"sample":hash_bad[:10]})
        add("manifest_byte_counts_match",not byte_bad,{"mismatch_count":len(byte_bad),"sample":byte_bad[:10]})
    pyerr=[]; pys=list(ftl.rglob("*.py")) if ftl.is_dir() else []
    for p in pys:
        try:
            import tokenize
            with tokenize.open(str(p)) as fh:
                source = fh.read()
            compile(source, str(p), "exec")
        except Exception as e:
            pyerr.append({"path":rel(repo,p),"error":str(e)})
    add("python_files_syntax_compile_without_pyc",not pyerr,{"checked":len(pys),"errors":pyerr[:10]})
    caches=[rel(repo,p) for p in patch_dir.rglob("__pycache__")]+[rel(repo,p) for p in patch_dir.rglob("*.pyc")]
    add("no_pycache_or_pyc",not caches,{"matches":caches[:20]})
    longs=[rel(repo,p) for p in patch_dir.rglob("*") if len(str(p))>240]
    add("no_long_paths_inside_patch",not longs,{"count":len(longs),"sample":longs[:10]})
    vio=[]
    for r in runners:
        txt=r.read_text(encoding="utf-8",errors="replace")
        for pat in BAD:
            if re.search(pat,txt,re.I): vio.append({"runner":rel(repo,r),"pattern":pat})
    add("runner_no_git_or_remote_exec",not vio,{"violations":vio[:10]})
    return {"patch_id":patch_dir.name,"path":rel(repo,patch_dir),"verdict":"PASS_TECHNICAL_PREFLIGHT" if not errors else "FAIL_TECHNICAL_PREFLIGHT","checks":checks,"errors":errors,"warnings":warnings}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo-root",default="."); ap.add_argument("--patch-id"); ap.add_argument("--all",action="store_true"); ap.add_argument("--fail-on-errors",action="store_true"); args=ap.parse_args()
    repo=Path(args.repo_root).resolve(); results=[scan(repo,d) for d in patch_dirs(repo,args.patch_id if not args.all else None)]
    err=sum(len(r["errors"]) for r in results); pc=sum(1 for r in results if r["verdict"]=="PASS_TECHNICAL_PREFLIGHT")
    verdict="PASS_TECHNICAL_PREFLIGHT" if err==0 else ("FAIL_TECHNICAL_PREFLIGHT" if (args.patch_id or args.fail_on_errors) else "WARN_TECHNICAL_PREFLIGHT_PARTIAL")
    gen=utc()
    summary={"summary_id":"mechanicus.patch_pack_technical_preflight_summary.v0_1","task_id":TASK_ID,"validator_id":VALIDATOR_ID,"generated_at_utc":gen,"repo_head":head(repo),"target_patch_id":args.patch_id,"patch_count":len(results),"pass_count":pc,"error_count":err,"verdict":verdict,"results":results}
    receipt={k:summary[k] for k in ["task_id","validator_id","verdict","generated_at_utc","repo_head","target_patch_id","patch_count","pass_count","error_count"]}; receipt.update({"receipt_id":"receipt.mechanicus.patch_pack_technical_preflight.v0_1","summary":SUMMARY.as_posix(),"report":REPORT.as_posix(),"errors":[e for r in results for e in r["errors"]],"warnings":[w for r in results for w in r["warnings"]]})
    for p in [SUMMARY,RECEIPT,REPORT]: (repo/p).parent.mkdir(parents=True,exist_ok=True)
    (repo/SUMMARY).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (repo/RECEIPT).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (repo/REPORT).write_text("# PATCH PACK TECHNICAL PREFLIGHT REPORT V0.1\n\nverdict: `"+verdict+"`\n\n"+"\n".join(f"- `{r['patch_id']}` — `{r['verdict']}`" for r in results[:80])+"\n",encoding="utf-8")
    print(json.dumps({"task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"target_patch_id":args.patch_id,"patch_count":len(results),"pass_count":pc,"error_count":err,"receipt":RECEIPT.as_posix(),"summary":SUMMARY.as_posix(),"errors":receipt["errors"][:20],"warnings":receipt["warnings"][:20]},ensure_ascii=False,indent=2))
    return 0 if verdict=="PASS_TECHNICAL_PREFLIGHT" or (not args.patch_id and not args.fail_on_errors) else 1
if __name__=="__main__": raise SystemExit(main())
