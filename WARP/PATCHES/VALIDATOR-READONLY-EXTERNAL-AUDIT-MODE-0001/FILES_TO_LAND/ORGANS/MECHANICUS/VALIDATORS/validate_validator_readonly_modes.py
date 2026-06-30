#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, json, shutil, subprocess, sys
from pathlib import Path
from typing import Any, Dict, List
TASK_ID='VALIDATOR-READONLY-EXTERNAL-AUDIT-MODE-0001'
VALIDATOR_ID='validator_readonly_external_audit_mode_validator.v0_1'
TARGETS=['ORGANS/THRONE/VALIDATORS/validate_throne_target_gap.py','ORGANS/THRONE/VALIDATORS/validate_external_audit_consolidation.py']
RECEIPT=Path('ORGANS/MECHANICUS/RECEIPTS/validator_readonly_external_audit_mode_receipt.json')
REPORT=Path('ORGANS/MECHANICUS/REPORTS/VALIDATOR_READONLY_EXTERNAL_AUDIT_MODE_REPORT_V0_1.md')
def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def add(c,n,ok,d=None): c.append({'name':n,'status':'PASS' if ok else 'FAIL','details':d or {}})
def run(cmd,cwd,timeout=120):
 p=subprocess.run(cmd,cwd=str(cwd),text=True,capture_output=True,timeout=timeout)
 return {'cmd':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def status(repo): return subprocess.run(['git','status','--porcelain'],cwd=str(repo),text=True,capture_output=True).stdout
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('--external-output-root',default=r'E:\IMPERIUM_EXTERNAL_AUDITS\VALIDATOR-READONLY-EXTERNAL-AUDIT-MODE-0001'); args=ap.parse_args()
 repo=Path(args.repo_root).resolve(); outroot=Path(args.external_output_root).resolve(); outroot.mkdir(parents=True,exist_ok=True)
 checks=[]; errors=[]; warnings=[]; results={}
 spec=repo/'ORGANS/MECHANICUS/SPECS/VALIDATOR_READONLY_EXTERNAL_AUDIT_MODE_SPEC_V0_2.md'; matrix=repo/'ORGANS/MECHANICUS/MATRICES/VALIDATOR_IO_MODE_MATRIX_V0_1.json'
 add(checks,'spec_exists',spec.is_file(),{'path':str(spec)}); add(checks,'matrix_exists',matrix.is_file(),{'path':str(matrix)})
 if not spec.is_file(): errors.append('Spec missing')
 if not matrix.is_file(): errors.append('Matrix missing')
 for rel in TARGETS:
  path=repo/rel; res={'path':rel,'exists':path.is_file(),'flags_in_source':{},'help_ok':False,'read_only_ok':False,'status_unchanged':False,'external_audit_ok':False,'external_audit_status_unchanged':False,'errors':[]}
  if not path.is_file():
   res['errors'].append('validator file missing'); errors.append('Missing validator: '+rel); results[rel]=res; continue
  src=path.read_text(encoding='utf-8',errors='replace')
  for flag in ['--dry-run','--read-only','--external-audit','--output-dir']:
   res['flags_in_source'][flag]=flag in src
   if flag not in src: res['errors'].append('flag not found in source: '+flag)
  hp=run([sys.executable,rel,'--help'],repo); res['help_ok']=hp['returncode']==0 and all(f in hp['stdout'] for f in ['--dry-run','--read-only','--external-audit','--output-dir'])
  if not res['help_ok']: res['errors'].append('help does not expose all required flags')
  before=status(repo); ro=run([sys.executable,rel,'--repo-root',str(repo),'--read-only'],repo); after=status(repo)
  res['read_only_ok']=ro['returncode']==0; res['status_unchanged']=before==after
  if not res['read_only_ok']: res['errors'].append('read-only run failed: '+ro['stderr'][-500:])
  if not res['status_unchanged']: res['errors'].append('git status changed after --read-only')
  ext=outroot/'validator_external_outputs'/Path(rel).stem
  if ext.exists(): shutil.rmtree(ext)
  ea=run([sys.executable,rel,'--repo-root',str(repo),'--external-audit','--output-dir',str(ext)],repo); after2=status(repo)
  res['external_audit_ok']=ea['returncode']==0 and ext.exists() and any(ext.rglob('*')); res['external_audit_status_unchanged']=before==after2
  if not res['external_audit_ok']: res['errors'].append('external-audit failed or wrote no external outputs: '+ea['stderr'][-500:])
  if not res['external_audit_status_unchanged']: res['errors'].append('git status changed after --external-audit')
  results[rel]=res
  if res['errors']: errors.append(rel+': '+'; '.join(res['errors']))
 add(checks,'target_validators_exist',all(results[r]['exists'] for r in TARGETS),{})
 add(checks,'required_flags_present',all(all(v['flags_in_source'].values()) for v in results.values()),{})
 add(checks,'help_exposes_required_flags',all(v['help_ok'] for v in results.values()),{})
 add(checks,'read_only_runs_pass',all(v['read_only_ok'] for v in results.values()),{})
 add(checks,'read_only_does_not_change_git_status',all(v['status_unchanged'] for v in results.values()),{})
 add(checks,'external_audit_writes_outside_repo',all(v['external_audit_ok'] for v in results.values()),{})
 add(checks,'external_audit_does_not_change_git_status',all(v['external_audit_status_unchanged'] for v in results.values()),{})
 verdict='PASS_READONLY_MODE_BASELINE' if not errors else 'FAIL_READONLY_MODE_BASELINE'
 receipt={'receipt_id':'receipt.mechanicus.validator_readonly_external_audit_mode.v0_1','task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'generated_at_utc':utc(),'target_validators':TARGETS,'external_output_root':str(outroot),'validator_results':results,'checks':checks,'warnings':warnings,'errors':errors,'meaning':'This proves the first high-risk Throne validators support read-only and external-audit modes. It does not prove all validators are converted.'}
 (repo/RECEIPT).parent.mkdir(parents=True,exist_ok=True); (repo/REPORT).parent.mkdir(parents=True,exist_ok=True); (repo/RECEIPT).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 checks_md='\n'.join(f"- `{c['status']}` — {c['name']}" for c in checks); errors_md='\n'.join(f"- {e}" for e in errors) if errors else '- none'; target_md='\n'.join(f"- `{rel}` — errors: {', '.join(results[rel]['errors']) if results[rel]['errors'] else 'none'}" for rel in TARGETS)
 (repo/REPORT).write_text(f"""# VALIDATOR READONLY EXTERNAL AUDIT MODE REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{receipt['generated_at_utc']}`

## Meaning

This report proves the first converted validators can be evaluated by external auditors without writing canonical outputs into Reality.

It does not prove all validators are safe yet.

## Target validators

{target_md}

## Checks

{checks_md}

## Errors

{errors_md}

## External output root

`{outroot}`

## Receipt

`{RECEIPT.as_posix()}`
""",encoding='utf-8')
 print(json.dumps({'task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'target_validators':TARGETS,'external_output_root':str(outroot),'receipt':RECEIPT.as_posix(),'report':REPORT.as_posix(),'errors':errors},ensure_ascii=False,indent=2))
 return 0 if verdict=='PASS_READONLY_MODE_BASELINE' else 1
if __name__=='__main__': raise SystemExit(main())
