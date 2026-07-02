#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, json, subprocess
from pathlib import Path
from typing import Any, Dict, List
PATCH_ID="ASTRONOMICON-RED-BLUE-HARDENING-AND-SCAN-ISOLATION-0001"
MATRIX=Path("ORGANS/ASTRONOMICON/RED_BLUE/ASTRONOMICON_RED_BLUE_HARDENING_MATRIX_V0_1.json")
CASES=Path("ORGANS/ASTRONOMICON/RED_BLUE/ASTRONOMICON_RED_BLUE_HARDENING_CASES_V0_1.json")
SUMMARY=Path("ORGANS/ASTRONOMICON/REPORTS/ASTRONOMICON_RED_BLUE_HARDENING_SUMMARY_V0_1.json")
REPORT=Path("ORGANS/ASTRONOMICON/REPORTS/ASTRONOMICON_RED_BLUE_HARDENING_REPORT_V0_1.md")
RECEIPT=Path("ORGANS/ASTRONOMICON/RECEIPTS/astronomicon_red_blue_hardening_receipt.json")
def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def git_head(repo:Path):
    try:
        p=subprocess.run(["git","rev-parse","--short","HEAD"],cwd=str(repo),capture_output=True,text=True,timeout=15)
        return p.stdout.strip() if p.returncode==0 else "UNKNOWN"
    except Exception: return "UNKNOWN"
def load_json(path:Path)->Any:
    try: return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception: return None
def write_json(path:Path,data:Any): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def evidence_pass(repo:Path, paths:List[str])->bool: return all((repo/p).is_file() for p in paths)
def eval_cases(repo:Path, items:List[Dict[str,Any]], key:str)->List[Dict[str,Any]]:
    rows=[]
    for item in items:
        paths=item.get(key,[]); ok=evidence_pass(repo,paths)
        rows.append({"id":item.get("case_id") or item.get("guard_id"),"skill":item.get("skill"),"status":"PASS" if ok else "FAIL","required_evidence":paths,"missing_evidence":[p for p in paths if not (repo/p).is_file()],"attention_zone":item.get("expected_attention_zone") or item.get("defense_zone"),"meaning":"local Astronomicon Red/Blue hardening evidence exists" if ok else "local evidence missing"})
    return rows
def pct(rows): return round(100.0*sum(1 for r in rows if r["status"]=="PASS")/len(rows),2) if rows else 0.0
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo-root",default="."); args=ap.parse_args(); repo=Path(args.repo_root).resolve()
    matrix=load_json(repo/MATRIX) or {}; cases=load_json(repo/CASES) or {}
    red_rows=eval_cases(repo,cases.get("red_cases",[]),"expected_detector_evidence"); blue_rows=eval_cases(repo,cases.get("blue_guards",[]),"expected_guard_evidence")
    red_score=pct(red_rows); blue_score=pct(blue_rows); th=matrix.get("pass_thresholds",{}); errors=[]
    if len(red_rows)<th.get("required_red_case_count_min",6): errors.append("red_case_count_below_threshold")
    if len(blue_rows)<th.get("required_blue_guard_count_min",6): errors.append("blue_guard_count_below_threshold")
    if red_score<th.get("red_local_hardening_score_min",80.0): errors.append("red_local_hardening_score_below_threshold")
    if blue_score<th.get("blue_local_hardening_score_min",80.0): errors.append("blue_local_hardening_score_below_threshold")
    for r in red_rows+blue_rows:
        if r["status"]!="PASS": errors.append(f"{r['id']}:missing_evidence")
    verdict="PASS_ASTRONOMICON_RED_BLUE_LOCAL_HARDENED_NOT_CUSTODES" if not errors else "FAIL_ASTRONOMICON_RED_BLUE_LOCAL_HARDENING"; generated=utc()
    summary={"summary_id":"astronomicon.red_blue_hardening_summary.v0_1","task_id":PATCH_ID,"validator_id":"astronomicon_red_blue_hardening_tool.v0_1","verdict":verdict,"generated_at_utc":generated,"repo_head":git_head(repo),"target_organ":"ASTRONOMICON","red_case_count":len(red_rows),"blue_guard_count":len(blue_rows),"red_local_hardening_score":red_score,"blue_local_hardening_score":blue_score,"red_team_proven_score":0.0,"blue_team_proven_score":0.0,"custodes_validation_score":0.0,"throne_confirmation_score":0.0,"red_results":red_rows,"blue_results":blue_rows,"errors":errors,"warnings":[],"not_claimed":["Custodes trust","Throne verdict","organ assembled","red_team_proven","blue_team_proven"]}
    write_json(repo/SUMMARY,summary); write_json(repo/RECEIPT,{"receipt_id":"receipt.astronomicon.red_blue_hardening.v0_1","task_id":PATCH_ID,"validator_id":"astronomicon_red_blue_hardening_tool.v0_1","verdict":verdict,"generated_at_utc":generated,"summary":SUMMARY.as_posix(),"report":REPORT.as_posix(),"errors":errors,"warnings":[],"meaning":"Astronomicon Red/Blue local hardening evidence is present; Custodes and Throne scores remain zero."})
    lines=["# ASTRONOMICON RED + BLUE LOCAL HARDENING REPORT V0.1","",f"verdict: `{verdict}`  ",f"red_local_hardening_score: `{red_score}`  ",f"blue_local_hardening_score: `{blue_score}`  ","red_team_proven_score: `0.0`  ","blue_team_proven_score: `0.0`  ","custodes_validation_score: `0.0`  ","throne_confirmation_score: `0.0`","","## Meaning","","Astronomicon local Red/Blue lanes are hardened by case evidence. This is still not Custodes trust and not Throne verdict.","","## Red cases",""]
    for r in red_rows: lines.append(f"- `{r['status']}` — `{r['id']}` / `{r['skill']}` / zone `{r['attention_zone']}`")
    lines += ["","## Blue guards",""]
    for r in blue_rows: lines.append(f"- `{r['status']}` — `{r['id']}` / `{r['skill']}` / zone `{r['attention_zone']}`")
    lines += ["","## Not claimed","","- Custodes trust","- Throne verdict","- organ assembled"]
    (repo/REPORT).parent.mkdir(parents=True,exist_ok=True); (repo/REPORT).write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2)); return 0 if verdict.startswith("PASS") else 1
if __name__=="__main__": raise SystemExit(main())
