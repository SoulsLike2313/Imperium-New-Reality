#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path
ORGANS=["ASTRONOMICON","ADMINISTRATUM","DOCTRINARIUM","MECHANICUS","INQUISITION","CUSTODES","STRATEGIUM","SCHOLA_IMPERIALIS","OFFICIO_AGENTIS","THRONE"]
def load_json(path):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception: return None
def git_head(repo):
    try:
        p=subprocess.run(["git","rev-parse","--short","HEAD"],cwd=str(repo),capture_output=True,text=True,timeout=15)
        return p.stdout.strip() if p.returncode==0 else "UNKNOWN"
    except Exception: return "UNKNOWN"
def print_status(repo):
    print("IMPERIUM TERMINAL LAUNCHER V0.1"); print(f"Repo: {repo}"); print(f"HEAD: {git_head(repo)}")
    receipt=load_json(repo/"ORGANS/THRONE/RECEIPTS/organ_assembly_stage_scoring_receipt.json")
    if receipt:
        s=receipt.get("scores",{})
        print("Stage scoring:")
        for k in ["profile_baseline_score","duty_defined_score","assembly_target_defined_score","organ_truth_maturity_score","organ_assembled_score","red_team_score","blue_team_score"]:
            print(f"  {k}: {s.get(k)}")
    else: print("Stage scoring receipt: missing")
def print_organs(repo):
    summary=load_json(repo/"ORGANS/THRONE/REPORTS/ORGAN_ASSEMBLY_STAGE_SCORING_SUMMARY_V0_1.json"); scores={}
    if summary:
        for row in summary.get("organs",[]): scores[row.get("organ_id")]=row
    print("ORGANS")
    for o in ORGANS:
        row=scores.get(o,{}); print(f"- {o}: maturity={row.get('organ_truth_maturity_score','?')} assembled={row.get('stage_scores',{}).get('organ_assembled_score','?')}")
def organ_view(repo,organ,mode):
    organ=organ.upper().replace("-","_")
    if organ not in ORGANS: print(f"Unknown organ: {organ}",file=sys.stderr); sys.exit(2)
    root=repo/"ORGANS"/organ; print(f"ORGAN {organ}"); print(f"path: {root}")
    if mode=="status":
        for rel in ["CONTRACTS/ORGAN_DUTY_CONTRACT_V0_1.json","ASSEMBLY/ORGAN_ASSEMBLY_TARGET_V0_1.json"]: print(f"{rel}: {'OK' if (root/rel).is_file() else 'MISSING'}")
    elif mode=="assembly":
        data=load_json(root/"ASSEMBLY/ORGAN_ASSEMBLY_TARGET_V0_1.json")
        if not data: print("assembly target missing"); return
        for k,v in data.get("assembly_gates",{}).items(): print(f"- {k}: {v.get('proof_state')}")
    elif mode=="receipts":
        d=root/"RECEIPTS"
        if not d.is_dir(): print("receipts dir missing"); return
        for f in sorted(d.glob("*.json"))[-20:]: print(f"- {f.relative_to(repo)}")
    else: print(f"Unknown organ mode: {mode}",file=sys.stderr); sys.exit(2)
def patch_list(repo):
    d=repo/"WARP/PATCHES"; print("PATCHES")
    for p in sorted([x for x in d.iterdir() if x.is_dir()])[-50:]: print(f"- {p.name}")
def patch_inspect(repo,patch_id):
    d=repo/"WARP/PATCHES"/patch_id
    if not d.is_dir(): print(f"Patch not found: {patch_id}",file=sys.stderr); sys.exit(2)
    print(f"PATCH {patch_id}")
    for rel in ["PATCH_PACK.md","PATCH_FILE_MANIFEST_SHA256.json"]:
        if (d/rel).exists(): print(f"- {rel}")
    pp=d/"PATCH_PACK.md"
    if pp.exists(): print("\n--- PATCH_PACK.md head ---"); print("\n".join(pp.read_text(encoding="utf-8",errors="replace").splitlines()[:60]))
def intake_dry_run(repo,text,task_id):
    tool=repo/"ORGANS/ASTRONOMICON/TOOLS/astronomicon_intake_dry_run.py"
    if not tool.is_file(): print("Astronomicon dry-run tool missing",file=sys.stderr); sys.exit(2)
    cmd=[sys.executable,str(tool),"--repo-root",str(repo),"--text",text]
    if task_id: cmd+=["--task-id",task_id]
    p=subprocess.run(cmd,text=True); sys.exit(p.returncode)
def main():
    ap=argparse.ArgumentParser(add_help=False); ap.add_argument("--repo-root",default="."); ns,rest=ap.parse_known_args(); repo=Path(ns.repo_root).resolve()
    if not rest or rest[0] in ["help","-h","--help"]:
        print("Commands: status | organs | organ <id> status|assembly|receipts | patch list|inspect <id> | intake dry-run <text> [--task-id ID]"); return 0
    if rest[0]=="status": print_status(repo); return 0
    if rest[0]=="organs": print_organs(repo); return 0
    if rest[0]=="organ" and len(rest)>=3: organ_view(repo,rest[1],rest[2]); return 0
    if rest[0]=="patch" and len(rest)>=2:
        if rest[1]=="list": patch_list(repo); return 0
        if rest[1]=="inspect" and len(rest)>=3: patch_inspect(repo,rest[2]); return 0
    if rest[0]=="intake" and len(rest)>=3 and rest[1]=="dry-run":
        text=rest[2]; task_id=None
        if "--task-id" in rest:
            i=rest.index("--task-id")
            if i+1<len(rest): task_id=rest[i+1]
        intake_dry_run(repo,text,task_id); return 0
    print("Unknown command. Run: help",file=sys.stderr); return 2
if __name__=="__main__": raise SystemExit(main())
