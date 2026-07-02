#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, json, subprocess, sys, re
from pathlib import Path
from typing import Any
PATCH_ID='CUSTODES-ASTRONOMICON-VALIDATION-0001'
MATRIX=Path('ORGANS/CUSTODES/MATRICES/CUSTODES_ASTRONOMICON_PROSECUTOR_AUDIT_MATRIX_V0_1.json')
SUMMARY=Path('ORGANS/CUSTODES/REPORTS/CUSTODES_ASTRONOMICON_PROSECUTOR_AUDIT_SUMMARY_V0_1.json')
REPORT=Path('ORGANS/CUSTODES/REPORTS/CUSTODES_ASTRONOMICON_PROSECUTOR_AUDIT_REPORT_V0_1.md')
RECEIPT=Path('ORGANS/CUSTODES/RECEIPTS/custodes_astronomicon_prosecutor_audit_receipt.json')
def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def load_json(p:Path):
    try: return json.loads(p.read_text(encoding='utf-8-sig'))
    except Exception: return None
def write_json(p:Path,d:Any):
    p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git_head(repo:Path):
    try:
        p=subprocess.run(['git','rev-parse','--short','HEAD'],cwd=str(repo),capture_output=True,text=True,timeout=15)
        return p.stdout.strip() if p.returncode==0 else 'UNKNOWN'
    except Exception: return 'UNKNOWN'
def pct(ok,total): return round(100.0*ok/total,2) if total else 0.0
def file_check(repo, paths):
    rows=[]
    for x in paths:
        ok=(repo/x).is_file(); rows.append({'path':x,'status':'PASS' if ok else 'FAIL'})
    return pct(sum(1 for r in rows if r['status']=='PASS'),len(rows)), rows
def verdict_from_stdout(s):
    try:
        d=json.loads(s)
        if isinstance(d,dict): return str(d.get('verdict',''))
    except Exception: pass
    m=re.search(r'"verdict"\s*:\s*"([^"]+)"',s)
    return m.group(1) if m else ''
def run_validator(repo,item):
    rel=item['path']; p=repo/rel
    if not p.is_file(): return {'path':rel,'status':'MISSING','exit_code':None,'verdict':None,'stderr_tail':'missing'}
    args=[a.replace('{repo}',str(repo)) for a in item.get('args',[])]
    try:
        r=subprocess.run([sys.executable,str(p)]+args,cwd=str(repo),capture_output=True,text=True,timeout=300)
        v=verdict_from_stdout(r.stdout); ok=(r.returncode==0 and (v.startswith('PASS') or 'PASS' in r.stdout[-1500:]))
        return {'path':rel,'status':'PASS' if ok else 'FAIL','exit_code':r.returncode,'verdict':v,'stdout_tail':r.stdout[-2500:],'stderr_tail':r.stderr[-1500:]}
    except Exception as e: return {'path':rel,'status':'FAIL','exit_code':None,'verdict':None,'stderr_tail':str(e)}
def identity(repo,matrix):
    score, rows=file_check(repo,matrix.get('required_identity_files',[])); notes=[]
    notes += ['missing '+r['path'] for r in rows if r['status']!='PASS']
    ids=[]
    for p in ['ORGANS/ASTRONOMICON/CONTRACTS/ORGAN_DUTY_CONTRACT_V0_1.json','ORGANS/ASTRONOMICON/RED_BLUE/ORGAN_RED_BLUE_SKILLS_V0_1.json']:
        d=load_json(repo/p) or {}; ids.append(d.get('organ_id')=='ASTRONOMICON')
        if d.get('organ_id')!='ASTRONOMICON': notes.append(f'{p} organ_id={d.get("organ_id")}')
    return round((score+pct(sum(1 for x in ids if x),len(ids)))/2,2), notes
def boundary(repo,matrix):
    bad=[]
    for p in ['ORGANS/ASTRONOMICON/REPORTS/ASTRONOMICON_RED_BLUE_HARDENING_SCAN_ISOLATION_SUMMARY_V0_1.json','ORGANS/ASTRONOMICON/REPORTS/ORGAN_AGENT_ADVISORY_SUMMARY_V0_1.json','ORGANS/ASTRONOMICON/RECEIPTS/red_blue_team_launcher_scan_commands_receipt.json']:
        f=repo/p
        if f.is_file():
            txt=f.read_text(encoding='utf-8',errors='replace')
            for term in matrix.get('boundary_claims_forbidden_as_assertions',[]):
                if term in txt: bad.append(f'{p} contains {term}')
    hard=load_json(repo/'ORGANS/ASTRONOMICON/REPORTS/ASTRONOMICON_RED_BLUE_HARDENING_SCAN_ISOLATION_SUMMARY_V0_1.json') or {}
    for k in ['red_team_proven_score','blue_team_proven_score','throne_confirmation_score']:
        if hard.get(k) not in (0,0.0): bad.append(f'{k}={hard.get(k)}')
    return (100.0 if not bad else 0.0), bad
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.')
    repo=Path(ap.parse_args().repo_root).resolve(); matrix=load_json(repo/MATRIX) or {}; indict=[]
    identity_score,notes=identity(repo,matrix); indict += ['identity:'+x for x in notes]
    capability_score,cap_rows=file_check(repo,matrix.get('required_capability_files',[])); indict += ['capability missing '+r['path'] for r in cap_rows if r['status']!='PASS']
    validators=[]
    for item in matrix.get('declared_active_validators',[]): validators.append(run_validator(repo,item))
    for item in matrix.get('conditional_validators_if_present',[]):
        if (repo/item['path']).is_file(): validators.append(run_validator(repo,item))
    validator_score=pct(sum(1 for v in validators if v['status']=='PASS'),len(validators)); indict += ['validator failed '+v['path'] for v in validators if v['status']!='PASS']
    boundary_score,bnotes=boundary(repo,matrix); indict += ['boundary:'+x for x in bnotes]
    ev_paths=['ORGANS/ASTRONOMICON/RECEIPTS/patch_pack_lifecycle_validation_foundation_receipt.json','ORGANS/ASTRONOMICON/RECEIPTS/patch_lifecycle_launcher_commands_receipt.json','ORGANS/ASTRONOMICON/RECEIPTS/organ_agent_advisory_scoring_validation_receipt.json','ORGANS/ASTRONOMICON/RECEIPTS/organ_agent_advisory_output_isolation_voice_receipt.json','ORGANS/ASTRONOMICON/RECEIPTS/red_blue_team_launcher_scan_commands_receipt.json','ORGANS/ASTRONOMICON/RECEIPTS/astronomicon_red_blue_hardening_scan_isolation_receipt.json']
    evidence_score,ev_rows=file_check(repo,ev_paths); indict += ['evidence missing '+r['path'] for r in ev_rows if r['status']!='PASS']
    hard=load_json(repo/'ORGANS/ASTRONOMICON/REPORTS/ASTRONOMICON_RED_BLUE_HARDENING_SCAN_ISOLATION_SUMMARY_V0_1.json') or {}
    rb_truth=100.0 if hard.get('red_team_proven_score')==0.0 and hard.get('blue_team_proven_score')==0.0 and hard.get('throne_confirmation_score')==0.0 else 0.0
    if rb_truth<100: indict.append('red/blue proof truth violated')
    w=matrix.get('score_formula',{})
    total=round(identity_score*w.get('identity_score',.15)+capability_score*w.get('capability_evidence_score',.20)+validator_score*w.get('validator_working_score',.25)+boundary_score*w.get('boundary_honesty_score',.20)+rb_truth*w.get('red_blue_truth_score',.10)+evidence_score*w.get('evidence_chain_score',.10),2)
    th=matrix.get('pass_thresholds',{})
    for k,v,floor in [('custodes_validation_score',total,th.get('custodes_validation_score_min',85)),('identity_score',identity_score,th.get('identity_score_min',80)),('capability_evidence_score',capability_score,th.get('capability_evidence_score_min',80)),('validator_working_score',validator_score,th.get('validator_working_score_min',80)),('boundary_honesty_score',boundary_score,th.get('boundary_honesty_score_min',80))]:
        if v<floor: indict.append(f'{k} below floor {floor}: {v}')
    verdict='PASS_CUSTODES_ASTRONOMICON_PROSECUTOR_VALIDATION' if not indict else 'FAIL_CUSTODES_ASTRONOMICON_PROSECUTOR_VALIDATION'
    g=utc(); summary={'summary_id':'custodes.astronomicon_prosecutor_audit_summary.v0_1','task_id':PATCH_ID,'validator_id':'custodes_audit_astronomicon.v0_1','verdict':verdict,'generated_at_utc':g,'repo_head':git_head(repo),'target_organ':'ASTRONOMICON','identity_score':identity_score,'capability_evidence_score':capability_score,'validator_working_score':validator_score,'boundary_honesty_score':boundary_score,'red_blue_truth_score':rb_truth,'evidence_chain_score':evidence_score,'custodes_validation_score':total,'throne_confirmation_score':0.0,'validators_tested':validators,'capability_evidence':cap_rows,'evidence_chain':ev_rows,'indictments':indict,'warnings':[],'not_claimed':['Throne verdict','organ assembled','global trust for all organs']}
    receipt={'receipt_id':'receipt.custodes.astronomicon_prosecutor_audit.v0_1','task_id':PATCH_ID,'validator_id':'custodes_audit_astronomicon.v0_1','verdict':verdict,'generated_at_utc':g,'summary':SUMMARY.as_posix(),'report':REPORT.as_posix(),'custodes_validation_score':total,'indictments':indict,'warnings':[]}
    write_json(repo/SUMMARY,summary); write_json(repo/RECEIPT,receipt)
    checks='\n'.join([f"- `{v['status']}` — `{v['path']}` verdict `{v.get('verdict')}` exit `{v.get('exit_code')}`" for v in validators])
    inds='\n'.join([f'- {x}' for x in indict]) if indict else '- none'
    (repo/REPORT).parent.mkdir(parents=True,exist_ok=True)
    (repo/REPORT).write_text(f'''# CUSTODES ASTRONOMICON PROSECUTOR AUDIT REPORT V0.1\n\nverdict: `{verdict}`  \ncustodes_validation_score: `{total}`  \nthrone_confirmation_score: `0.0`\n\n## Scores\n\n- identity_score: `{identity_score}`\n- capability_evidence_score: `{capability_score}`\n- validator_working_score: `{validator_score}`\n- boundary_honesty_score: `{boundary_score}`\n- red_blue_truth_score: `{rb_truth}`\n- evidence_chain_score: `{evidence_score}`\n\n## Validators prosecuted\n\n{checks}\n\n## Indictments\n\n{inds}\n\n## Not claimed\n\n- Throne verdict\n- organ assembled\n- global trust for all organs\n''',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2)); return 0 if verdict.startswith('PASS') else 1
if __name__=='__main__': raise SystemExit(main())
