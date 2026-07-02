#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, json, subprocess, sys
from pathlib import Path
TASK_ID='CUSTODES-ASTRONOMICON-VALIDATION-0001'
VALIDATOR_ID='custodes_astronomicon_validation_validator.v0_1'
AUDIT=Path('ORGANS/CUSTODES/TOOLS/custodes_audit_astronomicon.py')
MATRIX=Path('ORGANS/CUSTODES/MATRICES/CUSTODES_ASTRONOMICON_PROSECUTOR_AUDIT_MATRIX_V0_1.json')
DOCTRINE=Path('ORGANS/CUSTODES/DOCTRINE/CUSTODES_ORGAN_PROSECUTOR_AUDIT_LAW_V0_1.md')
RECEIPT=Path('ORGANS/CUSTODES/RECEIPTS/custodes_astronomicon_validation_receipt.json')
SUMMARY=Path('ORGANS/CUSTODES/REPORTS/CUSTODES_ASTRONOMICON_VALIDATION_SUMMARY_V0_1.json')
REPORT=Path('ORGANS/CUSTODES/REPORTS/CUSTODES_ASTRONOMICON_VALIDATION_REPORT_V0_1.md')
def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def load_json(p):
    try: return json.loads(p.read_text(encoding='utf-8-sig')),None
    except Exception as e: return None,str(e)
def git_head(repo):
    try:
        p=subprocess.run(['git','rev-parse','HEAD'],cwd=str(repo),capture_output=True,text=True,timeout=15)
        return p.stdout.strip() if p.returncode==0 else 'UNKNOWN'
    except Exception: return 'UNKNOWN'
def add(ch,n,ok,d=None): ch.append({'name':n,'status':'PASS' if ok else 'FAIL','details':d or {}})
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('--apply',action='store_true')
    repo=Path(ap.parse_args().repo_root).resolve(); checks=[]; errors=[]; warnings=[]
    for rel in [AUDIT,MATRIX,DOCTRINE]:
        ok=(repo/rel).is_file(); add(checks,f'{rel.name}_exists',ok,{'path':rel.as_posix()})
        if not ok: errors.append(f'missing {rel.as_posix()}')
    data,err=load_json(repo/MATRIX) if (repo/MATRIX).is_file() else ({},'missing')
    add(checks,'custodes_matrix_parses',err is None,{'error':err})
    if err: errors.append('matrix parse failed')
    p=subprocess.run([sys.executable,str(repo/AUDIT),'--repo-root',str(repo)],cwd=str(repo),capture_output=True,text=True,timeout=420)
    add(checks,'custodes_audit_tool_runs',p.returncode==0,{'stderr':p.stderr[-2000:]})
    if p.returncode!=0: errors.append('custodes audit tool failed')
    audit,err=load_json(repo/'ORGANS/CUSTODES/REPORTS/CUSTODES_ASTRONOMICON_PROSECUTOR_AUDIT_SUMMARY_V0_1.json')
    add(checks,'custodes_audit_summary_parses',err is None,{'error':err})
    if err: errors.append('audit summary parse failed'); audit={}
    add(checks,'custodes_audit_passes',str(audit.get('verdict','')).startswith('PASS'),{'verdict':audit.get('verdict')})
    if not str(audit.get('verdict','')).startswith('PASS'): errors.append('Custodes audit verdict is not PASS')
    for k in ['identity_score','capability_evidence_score','validator_working_score','boundary_honesty_score','custodes_validation_score']:
        v=float(audit.get(k,0)); add(checks,f'{k}_meets_floor',v>=80.0,{'score':audit.get(k)})
        if v<80.0: errors.append(f'{k} below 80')
    add(checks,'throne_confirmation_remains_zero',audit.get('throne_confirmation_score')==0.0,{'score':audit.get('throne_confirmation_score')})
    if audit.get('throne_confirmation_score')!=0.0: errors.append('Throne confirmation must remain zero')
    add(checks,'no_indictments',not audit.get('indictments'),{'indictments':audit.get('indictments')})
    if audit.get('indictments'): errors.append('Custodes indictments exist')
    verdict='PASS_CUSTODES_ASTRONOMICON_VALIDATION_READY' if not errors else 'FAIL_CUSTODES_ASTRONOMICON_VALIDATION'
    g=utc(); summary={'summary_id':'custodes.astronomicon_validation_summary.v0_1','task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'generated_at_utc':g,'repo_head':git_head(repo),'target_organ':'ASTRONOMICON','custodes_validation_score':audit.get('custodes_validation_score'),'identity_score':audit.get('identity_score'),'capability_evidence_score':audit.get('capability_evidence_score'),'validator_working_score':audit.get('validator_working_score'),'boundary_honesty_score':audit.get('boundary_honesty_score'),'throne_confirmation_score':audit.get('throne_confirmation_score'),'checks':checks,'errors':errors,'warnings':warnings,'next_layer':'THRONE-ASTRONOMICON-STRICT-GATES-0001'}
    receipt={'receipt_id':'receipt.custodes.astronomicon_validation.v0_1','task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'generated_at_utc':g,'summary':SUMMARY.as_posix(),'report':REPORT.as_posix(),'checks':checks,'errors':errors,'warnings':warnings}
    for path,obj in [(SUMMARY,summary),(RECEIPT,receipt)]:
        (repo/path).parent.mkdir(parents=True,exist_ok=True); (repo/path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    checks_md='\n'.join([f"- `{c['status']}` — {c['name']}" for c in checks]); errors_md='\n'.join([f'- {e}' for e in errors]) if errors else '- none'
    (repo/REPORT).parent.mkdir(parents=True,exist_ok=True)
    (repo/REPORT).write_text(f'''# CUSTODES ASTRONOMICON VALIDATION REPORT V0.1\n\nverdict: `{verdict}`  \ncustodes_validation_score: `{audit.get('custodes_validation_score')}`  \nthrone_confirmation_score: `{audit.get('throne_confirmation_score')}`\n\n## Meaning\n\nCustodes prosecuted Astronomicon claims: identity, capability evidence, validator honesty, boundary discipline.\n\n## Checks\n\n{checks_md}\n\n## Errors\n\n{errors_md}\n\n## Next\n\n`THRONE-ASTRONOMICON-STRICT-GATES-0001`\n''',encoding='utf-8')
    print(json.dumps({'task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'custodes_validation_score':audit.get('custodes_validation_score'),'receipt':RECEIPT.as_posix(),'summary':SUMMARY.as_posix(),'report':REPORT.as_posix(),'errors':errors,'warnings':warnings},ensure_ascii=False,indent=2)); return 0 if verdict.startswith('PASS') else 1
if __name__=='__main__': raise SystemExit(main())
