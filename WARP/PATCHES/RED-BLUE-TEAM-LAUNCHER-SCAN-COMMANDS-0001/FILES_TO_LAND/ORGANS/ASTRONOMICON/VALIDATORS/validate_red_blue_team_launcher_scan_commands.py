#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, json, subprocess, sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

TASK_ID="RED-BLUE-TEAM-LAUNCHER-SCAN-COMMANDS-0001"
VALIDATOR_ID="red_blue_team_launcher_scan_commands_validator.v0_1"
LAUNCHER=Path("SUPPORT/LAUNCHER/imperium_cli.py")
COMMANDS=Path("SUPPORT/LAUNCHER/LAUNCHER_COMMANDS_V0_4.json")
MATRIX=Path("ORGANS/ASTRONOMICON/MATRICES/RED_BLUE_TEAM_LAUNCHER_SCAN_COMMANDS_MATRIX_V0_1.json")
SCAN=Path("ORGANS/INQUISITION/TOOLS/red_blue_team_skills_scan.py")
RECEIPT=Path("ORGANS/ASTRONOMICON/RECEIPTS/red_blue_team_launcher_scan_commands_receipt.json")
REPORT=Path("ORGANS/ASTRONOMICON/REPORTS/RED_BLUE_TEAM_LAUNCHER_SCAN_COMMANDS_REPORT_V0_1.md")
SUMMARY=Path("ORGANS/ASTRONOMICON/REPORTS/RED_BLUE_TEAM_LAUNCHER_SCAN_COMMANDS_SUMMARY_V0_1.json")

def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def git_head(repo:Path)->str:
    try:
        p=subprocess.run(["git","rev-parse","HEAD"],cwd=str(repo),capture_output=True,text=True,timeout=15)
        return p.stdout.strip() if p.returncode==0 else "UNKNOWN"
    except Exception: return "UNKNOWN"
def load_json(p:Path)->Tuple[Any,str|None]:
    try: return json.loads(p.read_text(encoding="utf-8-sig")), None
    except Exception as e: return None, str(e)
def add(checks:List[Dict[str,Any]],name:str,ok:bool,details:Dict[str,Any]|None=None):
    checks.append({"name":name,"status":"PASS" if ok else "FAIL","details":details or {}})
def run_cli(repo:Path,args:List[str])->Tuple[int,str,str]:
    p=subprocess.run([sys.executable,str(repo/LAUNCHER),"--repo-root",str(repo)]+args,cwd=str(repo),capture_output=True,text=True,timeout=120)
    return p.returncode,p.stdout,p.stderr

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--repo-root",default="."); ap.add_argument("--apply",action="store_true")
    args=ap.parse_args(); repo=Path(args.repo_root).resolve()
    checks=[]; errors=[]; warnings=[]
    for rel in [LAUNCHER,COMMANDS,MATRIX,SCAN]:
        ok=(repo/rel).is_file(); add(checks,f"{rel.name}_exists",ok,{"path":rel.as_posix()})
        if not ok: errors.append(f"missing {rel.as_posix()}")
    commands,err=load_json(repo/COMMANDS) if (repo/COMMANDS).is_file() else ({}, "missing")
    add(checks,"launcher_v0_4_commands_parse",err is None,{"error":err})
    if err: errors.append("launcher commands v0.4 parse failed"); commands={}
    req=["redblue scan","redblue scan organ <ORGAN>","redblue summary","organ <ORGAN> redblue"]
    declared=commands.get("new_red_blue_commands",[]) if isinstance(commands,dict) else []
    missing=[c for c in req if c not in declared]
    add(checks,"redblue_launcher_commands_declared",not missing,{"missing":missing})
    if missing: errors.append("missing redblue launcher commands: "+", ".join(missing))
    matrix,err=load_json(repo/MATRIX) if (repo/MATRIX).is_file() else ({}, "missing")
    add(checks,"redblue_launcher_matrix_parses",err is None,{"error":err})
    if err: errors.append("redblue launcher matrix parse failed")
    command_results={}
    for name,argv in [
        ("redblue_scan",["redblue","scan"]),
        ("redblue_scan_organ_inquisition",["redblue","scan","organ","INQUISITION"]),
        ("redblue_summary",["redblue","summary"]),
        ("organ_inquisition_redblue",["organ","INQUISITION","redblue"])
    ]:
        code,out,err=run_cli(repo,argv)
        command_results[name]={"exit_code":code,"stdout_tail":out[-2000:],"stderr_tail":err[-1000:]}
        add(checks,f"launcher_{name}_runs",code==0,command_results[name])
        if code!=0: errors.append(f"launcher {name} failed")
    for name,argv in [("redblue_prove_forbidden",["redblue","prove"]),("redblue_attack_forbidden",["redblue","attack"]),("redblue_defend_forbidden",["redblue","defend"])]:
        code,out,err=run_cli(repo,argv)
        add(checks,f"launcher_{name}",code!=0,{"exit_code":code,"stdout_tail":out[-500:],"stderr_tail":err[-500:]})
        if code==0: errors.append(f"forbidden command unexpectedly succeeded: {name}")
    scan_summary,scan_err=load_json(repo/"ORGANS/INQUISITION/REPORTS/RED_BLUE_TEAM_SKILLS_SCAN_SUMMARY_V0_1.json")
    ok=(scan_err is None and scan_summary.get("red_team_defined_score")==100.0 and scan_summary.get("blue_team_defined_score")==100.0 and scan_summary.get("red_team_proven_score")==0.0 and scan_summary.get("blue_team_proven_score")==0.0)
    add(checks,"redblue_scan_summary_still_defined_not_proven",ok,{"error":scan_err,"summary":scan_summary if isinstance(scan_summary,dict) else None})
    if not ok: errors.append("redblue scan summary not defined-not-proven after launcher commands")
    verdict="PASS_RED_BLUE_TEAM_LAUNCHER_SCAN_COMMANDS_READY" if not errors else "FAIL_RED_BLUE_TEAM_LAUNCHER_SCAN_COMMANDS"
    generated=utc()
    summary={"summary_id":"astronomicon.red_blue_team_launcher_scan_commands_summary.v0_1","task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"generated_at_utc":generated,"repo_head":git_head(repo),"command_results":command_results,"checks":checks,"errors":errors,"warnings":warnings,"not_claimed":["red_team_proven","blue_team_proven","Custodes trust","Throne verdict","organ assembled"]}
    receipt={"receipt_id":"receipt.astronomicon.red_blue_team_launcher_scan_commands.v0_1","task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"generated_at_utc":generated,"summary":SUMMARY.as_posix(),"report":REPORT.as_posix(),"checks":checks,"errors":errors,"warnings":warnings,"meaning":"Red/Blue defined-not-proven scan commands are exposed in launcher without proof claims."}
    for p in [SUMMARY,RECEIPT,REPORT]: (repo/p).parent.mkdir(parents=True,exist_ok=True)
    (repo/SUMMARY).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (repo/RECEIPT).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    checks_md="\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md="\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md="\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo/REPORT).write_text(f"""# RED + BLUE TEAM LAUNCHER SCAN COMMANDS REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`  
repo_head: `{git_head(repo)}`

## Commands

```text
imperium redblue scan
imperium redblue scan organ <ORGAN>
imperium redblue summary
imperium organ <ORGAN> redblue
```

## Meaning

The operator can now view Red/Blue skill lane status from the launcher.

The command shows definition readiness and proof gap. It does not prove Red/Blue.

## Not claimed

- red_team_proven
- blue_team_proven
- Custodes trust
- Throne verdict
- organ assembled

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}
""",encoding="utf-8")
    print(json.dumps({"task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"receipt":RECEIPT.as_posix(),"summary":SUMMARY.as_posix(),"report":REPORT.as_posix(),"errors":errors,"warnings":warnings},ensure_ascii=False,indent=2))
    return 0 if verdict.startswith("PASS") else 1
if __name__=="__main__":
    raise SystemExit(main())
