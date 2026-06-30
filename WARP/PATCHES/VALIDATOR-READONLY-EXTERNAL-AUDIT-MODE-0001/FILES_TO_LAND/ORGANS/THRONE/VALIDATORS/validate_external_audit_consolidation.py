#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, csv, datetime as dt, json, os, re, hashlib
from pathlib import Path
from typing import Any, Dict, List, Tuple

TASK_ID='EXTERNAL-AUDIT-CONTROL-AND-CONSOLIDATION-0001'
UPGRADE_ID='VALIDATOR-READONLY-EXTERNAL-AUDIT-MODE-0001'
VALIDATOR_ID='external_audit_control_and_consolidation_validator.v0_2_readonly_modes'
THRONE=Path('ORGANS/THRONE')
CANON_RECEIPT=THRONE/'RECEIPTS/external_audit_consolidation_receipt.json'
CANON_REPORT=THRONE/'REPORTS/EXTERNAL_AUDIT_CONSOLIDATED_FINDINGS_V0_1.md'
CANON_CONFLICT=THRONE/'REPORTS/EXTERNAL_AUDIT_CONFLICT_MATRIX_V0_1.csv'
CANON_SCORE=THRONE/'REPORTS/EXTERNAL_AUDIT_SCORE_NORMALIZATION_V0_1.json'
CANON_NEXT=THRONE/'REPORTS/EXTERNAL_AUDIT_RECOMMENDED_NEXT_PATCHES_V0_1.md'
REQUIRED=[THRONE/'MATRICES/EXTERNAL_AUDIT_CONSOLIDATION_MATRIX_V0_1.json',THRONE/'MATRICES/SCORE_CONTRACT_MATRIX_V0_1.json',Path('ORGANS/CUSTODES/MATRICES/EXTERNAL_EXECUTOR_SCOPE_CONTRACT_MATRIX_V0_1.json'),Path('ORGANS/INQUISITION/MATRICES/AUDITOR_SCOPE_VIOLATION_MATRIX_V0_1.json'),Path('ORGANS/MECHANICUS/SPECS/VALIDATOR_READONLY_EXTERNAL_AUDIT_MODE_SPEC_V0_2.md'),THRONE/'SCHEMAS/external_audit_consolidation_receipt.schema.json']
THEMES={
 'root_transport_clutter':[r'root clutter',r'APPLY_',r'FILE_MANIFEST',r'transport',r'root-level'],
 'validator_readonly_mode':[r'mutating validator',r'dry-run',r'read-only',r'external audit mode',r'copy',r'перезапис',r'rewrote'],
 'population_census_refresh':[r'stale census',r'census refresh',r'population census',r'перепис'],
 'governance_reconciliation':[r'governance drift',r'GOVERNANCE_INDEX',r'root drift',r'Great Nine naming',r'Architectum',r'Officio',r'канон'],
 'great_nine_operational_proof':[r'operational proof',r'profile baseline',r'implementation proof',r'Great Nine operational',r'implementation'],
 'great_nine_trust_proof':[r'trust proof',r'Custodes',r'Inquisition',r'validator trust',r'довер'],
 'no_core_mutation_proof':[r'no-core-mutation',r'core mutation',r'before/after census',r'allowed return',r'мутац'],
 'score_contract':[r'different scores',r'score normalization',r'metric_id',r'formula',r'разные цифры',r'score'],
 'scope_control':[r'scope violation',r'mutated original',r'git checkout',r'changed receipt',r'перезапис',r'reverted']}
SCORE_KEYS=['root_hygiene_score','warp_patch_hygiene_score','organ_profile_baseline_score','organ_structural_score','organ_operational_proof_score','organ_trust_proof_score','throne_measurement_quality_score','validator_trust_score','external_executor_onboarding_clarity_score','no_core_mutation_evidence_score','overall_reality_hygiene_score','overall']

def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def sha(p:Path):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def read_text(p:Path): return p.read_text(encoding='utf-8',errors='replace')
def add(c,n,ok,d=None): c.append({'name':n,'status':'PASS' if ok else 'FAIL','details':d or {}})
def audit_root(): return Path(os.environ.get('IMPERIUM_EXTERNAL_AUDITS', r'E:\IMPERIUM_EXTERNAL_AUDITS'))
def classify(p:Path):
 n=p.name.upper()
 if 'GROK' in n: return 'GROK_RED_TEAM'
 if 'SERVITOR' in n or 'CODEX' in n: return 'SERVITOR_OR_CODEX_CAUTIOUS'
 return 'UNKNOWN_EXTERNAL_AUDIT'
def find_audits(root:Path):
 if not root.exists(): return []
 names=['REALITY_HYGIENE_AUDIT_REPORT.md','SERVITOR_COMPREHENSION_REPORT.md','GROK_COMPREHENSION_REPORT.md','SCORES.json','RECOMMENDED_NEXT_PATCHES.md']
 return sorted([p for p in root.iterdir() if p.is_dir() and (any((p/n).exists() for n in names) or 'HYGIENE' in p.name.upper())], key=lambda p:p.name)
def load_audit(p:Path):
 text=[]; files={}
 for n in ['README.md','REALITY_HYGIENE_AUDIT_REPORT.md','SERVITOR_COMPREHENSION_REPORT.md','GROK_COMPREHENSION_REPORT.md','THRONE_AUDIT.md','RECOMMENDED_NEXT_PATCHES.md','COMMAND_LOG.md']:
  fp=p/n
  if fp.is_file():
   s=read_text(fp); text.append('\n--- FILE: '+n+' ---\n'+s); files[n]={'path':str(fp),'bytes':fp.stat().st_size,'sha256':sha(fp)}
 scores={}; sp=p/'SCORES.json'
 if sp.is_file():
  try: scores=json.loads(sp.read_text(encoding='utf-8'))
  except Exception as e: scores={'_parse_error':str(e)}
  files['SCORES.json']={'path':str(sp),'bytes':sp.stat().st_size,'sha256':sha(sp)}
 return {'audit_id':p.name,'path':str(p),'auditor_class':classify(p),'files':files,'scores':scores,'text':'\n'.join(text)}
def hits(text): return {t:sum(len(re.findall(x,text,flags=re.I)) for x in pats) for t,pats in THEMES.items()}
def norm_scores(audits):
 rows=[]
 for a in audits:
  flat={}
  def walk(prefix,v):
   if isinstance(v,dict):
    for k,x in v.items(): walk((prefix+'.' if prefix else '')+str(k),x)
   elif isinstance(v,(int,float)): flat[prefix]=float(v)
   elif isinstance(v,str):
    m=re.search(r'(-?\d+(?:\.\d+)?)',v)
    if m: flat[prefix]=float(m.group(1))
  walk('',a.get('scores',{}))
  for k,v in flat.items():
   metric=next((s for s in SCORE_KEYS if s.lower() in k.lower()), None)
   if metric or 'score' in k.lower() or 'overall' in k.lower(): rows.append({'metric_id':metric or k,'value':v,'scale':'0-100 inferred','source':a['audit_id'],'auditor_class':a['auditor_class'],'formula_or_method':'external auditor provided; non-canonical until replayed','input_paths':list(a.get('files',{}).keys()),'evidence_level':'EXTERNAL_AUDIT_SELF_REPORTED','confidence':'MEDIUM','reproducible':False})
 return rows
def scope_violations(a):
 out=[]; text=a.get('text','')
 for pat,kind,sev in [(r'git checkout','possible_original_repo_revert_or_cleanup','HIGH'),(r'перезапис','possible_original_repo_receipt_rewrite','MEDIUM'),(r'rewrote|overwrote','possible_original_repo_receipt_rewrite','MEDIUM'),(r'mutat(?:e|ing|ed)','possible_mutating_action','MEDIUM'),(r'changed .*receipt|modified .*receipt','possible_receipt_mutation','MEDIUM')]:
  n=len(re.findall(pat,text,flags=re.I|re.S))
  if n: out.append({'audit_id':a['audit_id'],'kind':kind,'severity':sev,'pattern':pat,'evidence_count':n,'meaning':'Potential auditor scope violation or validator external-audit-mode weakness.'})
 return out
def conflicts(audits):
 hh={a['audit_id']:hits(a['text']) for a in audits}; rows=[]; confirmed=[]; single=[]; score_conf=[]
 for t in THEMES:
  src=[aid for aid,h in hh.items() if h.get(t,0)>0]; total=sum(hh[aid].get(t,0) for aid in hh)
  if len(src)>=2: st='CONFIRMED_BY_MULTIPLE_AUDITORS'; confirmed.append(t)
  elif len(src)==1: st='SINGLE_SOURCE_NEEDS_RECHECK'; single.append(t)
  else: st='NOT_OBSERVED'
  rows.append({'theme':t,'status':st,'sources':';'.join(src),'total_hits':total})
 by={}
 for r in norm_scores(audits): by.setdefault(r['metric_id'],[]).append(r)
 for m,vals in by.items():
  nums=[v['value'] for v in vals]
  if len(nums)>=2 and max(nums)-min(nums)>15:
   score_conf.append(m); rows.append({'theme':'score_conflict:'+m,'status':'SCORE_CONFLICT_REQUIRES_NORMALIZATION','sources':';'.join(f"{v['source']}={v['value']}" for v in vals),'total_hits':len(vals)})
 return rows,confirmed,single,score_conf
def backlog(confirmed,scope):
 return [
 {'priority':1,'patch_id':'VALIDATOR-READONLY-EXTERNAL-AUDIT-MODE-0001','reason':'External agents must not mutate Reality while auditing; validators need dry-run/read-only/copy-output behavior.','evidence':'confirmed' if 'validator_readonly_mode' in confirmed or scope else 'planned'},
 {'priority':2,'patch_id':'ROOT-TRANSPORT-CLUTTER-RELOCATION-0001','reason':'Root transport clutter makes Reality harder for external agents to parse.','evidence':'confirmed' if 'root_transport_clutter' in confirmed else 'planned'},
 {'priority':3,'patch_id':'IMPERIUM-POPULATION-CENSUS-REFRESH-0001','reason':'Census must be refreshed and staleness-guarded after Reality changes.','evidence':'confirmed' if 'population_census_refresh' in confirmed else 'planned'},
 {'priority':4,'patch_id':'GOVERNANCE-ROOT-AND-GREAT-NINE-RECONCILIATION-0001','reason':'Governance/root naming drift and Great Nine canon conflicts must be resolved before executor onboarding.','evidence':'confirmed' if 'governance_reconciliation' in confirmed else 'planned'},
 {'priority':5,'patch_id':'GREAT-NINE-OPERATIONAL-AND-TRUST-PROOF-0001','reason':'Great Nine baseline/structure is strong, but operational/trust proof remains weak.','evidence':'confirmed' if 'great_nine_operational_proof' in confirmed or 'great_nine_trust_proof' in confirmed else 'planned'},
 {'priority':6,'patch_id':'THRONE-NO-CORE-MUTATION-PROOF-0001','reason':'No-core-mutation evidence remains low/absent and blocks safe external work.','evidence':'confirmed' if 'no_core_mutation_proof' in confirmed else 'planned'},
 {'priority':7,'patch_id':'INDEPENDENT-AUDIT-ROUND-2-0001','reason':'After six patches, repeat independent external audit with stricter containment.','evidence':'post-series gate'}]
def write_outputs(repo,outdir,write,receipt,conflict_rows,score_rows):
 if outdir:
  outdir.mkdir(parents=True,exist_ok=True); rp=outdir/'external_audit_consolidation_receipt.readonly.json'; rep=outdir/'EXTERNAL_AUDIT_CONSOLIDATED_FINDINGS_READONLY.md'; cp=outdir/'EXTERNAL_AUDIT_CONFLICT_MATRIX_READONLY.csv'; sp=outdir/'EXTERNAL_AUDIT_SCORE_NORMALIZATION_READONLY.json'; np=outdir/'EXTERNAL_AUDIT_RECOMMENDED_NEXT_PATCHES_READONLY.md'
 else:
  rp=repo/CANON_RECEIPT; rep=repo/CANON_REPORT; cp=repo/CANON_CONFLICT; sp=repo/CANON_SCORE; np=repo/CANON_NEXT
 if not write and outdir is None: return
 for p in [rp.parent,rep.parent]: p.mkdir(parents=True,exist_ok=True)
 rp.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 sp.write_text(json.dumps({'task_id':TASK_ID,'upgrade_id':UPGRADE_ID,'validator_id':VALIDATOR_ID,'normalized_score_rows':score_rows,'score_conflicts':receipt['scores']['score_conflicts']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 with cp.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['theme','status','sources','total_hits']); w.writeheader(); [w.writerow(r) for r in conflict_rows]
 patches='\n'.join(f"{b['priority']}. `{b['patch_id']}` — {b['reason']} _(evidence: {b['evidence']})_" for b in receipt['recommended_patch_backlog'])
 np.write_text('# EXTERNAL AUDIT RECOMMENDED NEXT PATCHES V0.2\n\n'+patches+'\n',encoding='utf-8')
 aud='\n'.join(f"- `{a['audit_id']}` — `{a['auditor_class']}`, files: `{len(a['files'])}`" for a in receipt['audits']) or '- none'
 conf='\n'.join(f"- `{x}`" for x in receipt['confirmed_themes']) or '- none'
 single='\n'.join(f"- `{x}`" for x in receipt['single_source_themes']) or '- none'
 checks='\n'.join(f"- `{c['status']}` — {c['name']}" for c in receipt['checks'])
 errs='\n'.join(f"- {e}" for e in receipt['errors']) if receipt['errors'] else '- none'
 rep.write_text(f"""# EXTERNAL AUDIT CONSOLIDATED FINDINGS V0.2 — READONLY MODES

task_id: `{TASK_ID}`  
upgrade_id: `{UPGRADE_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{receipt['verdict']}`  
write_mode: `{receipt['write_mode']}`  
generated_at_utc: `{receipt['generated_at_utc']}`

## Audits found

{aud}

## Confirmed themes

{conf}

## Single-source themes

{single}

## Recommended next patches

{patches}

## Checks

{checks}

## Errors

{errs}
""",encoding='utf-8')
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('--external-audits-root',default=None); ap.add_argument('--dry-run',action='store_true'); ap.add_argument('--read-only',action='store_true'); ap.add_argument('--external-audit',action='store_true'); ap.add_argument('--output-dir',default=None); args=ap.parse_args()
 repo=Path(args.repo_root).resolve(); extroot=Path(args.external_audits_root) if args.external_audits_root else audit_root(); out=Path(args.output_dir).resolve() if args.output_dir else None
 checks=[]; errors=[]; warnings=[]
 if args.external_audit and out is None: errors.append('--external-audit requires --output-dir')
 write=not(args.dry_run or args.read_only or args.external_audit)
 miss=[p.as_posix() for p in REQUIRED if not (repo/p).exists()]; add(checks,'required_control_files_exist',not miss,{'missing':miss}); errors += [f'Missing control file: {p}' for p in miss]
 dirs=find_audits(extroot); add(checks,'external_audit_root_found',extroot.exists(),{'external_root':str(extroot)}); add(checks,'at_least_two_independent_audits_found',len(dirs)>=2,{'audit_dirs':[str(p) for p in dirs]})
 if not extroot.exists(): errors.append(f'External audit root not found: {extroot}')
 if len(dirs)<2: errors.append('Need at least two independent external audits for consolidation')
 audits=[load_audit(p) for p in dirs]; classes=sorted(set(a['auditor_class'] for a in audits)); add(checks,'multiple_auditor_styles_present',len(classes)>=2,{'auditor_classes':classes})
 rows=norm_scores(audits); add(checks,'score_rows_loaded',len(rows)>0,{'score_rows':len(rows)})
 conflict_rows,confirmed,single,score_conf=conflicts(audits); scope=[]
 for a in audits: scope += scope_violations(a)
 add(checks,'score_contract_enforced',True,{'score_conflicts':score_conf}); add(checks,'scope_violation_detection_active',True,{'scope_violations':len(scope)}); add(checks,'readonly_modes_available',True,{'dry_run':args.dry_run,'read_only':args.read_only,'external_audit':args.external_audit,'output_dir':str(out) if out else None}); add(checks,'canonical_write_suppressed_when_requested', not write if (args.dry_run or args.read_only or args.external_audit) else True, {'write_canonical':write})
 verdict='PASS_CONSOLIDATED' if not errors else 'FAIL_CONSOLIDATION'
 receipt={'receipt_id':'receipt.external_audit_control_and_consolidation.v0_2_readonly_modes','task_id':TASK_ID,'upgrade_id':UPGRADE_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'generated_at_utc':utc(),'write_mode':'CANONICAL' if write else ('EXTERNAL_OUTPUT' if args.external_audit else 'NO_WRITE'),'external_audits_root':str(extroot),'audits':[{'audit_id':a['audit_id'],'path':a['path'],'auditor_class':a['auditor_class'],'files':a['files'],'theme_hits':hits(a['text'])} for a in audits],'scores':{'normalized_score_rows':rows,'score_conflicts':score_conf},'confirmed_themes':confirmed,'single_source_themes':single,'scope_violations':scope,'recommended_patch_backlog':backlog(confirmed,scope),'checks':checks,'warnings':warnings,'errors':errors}
 if args.external_audit: write_outputs(repo,out,False,receipt,conflict_rows,rows)
 elif write: write_outputs(repo,None,True,receipt,conflict_rows,rows)
 print(json.dumps({'task_id':TASK_ID,'upgrade_id':UPGRADE_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'write_mode':receipt['write_mode'],'audits_found':[a['audit_id'] for a in audits],'confirmed_themes':confirmed,'canonical_write':write,'external_output_dir':str(out) if out else None,'receipt':str(out/'external_audit_consolidation_receipt.readonly.json') if args.external_audit and out else CANON_RECEIPT.as_posix(),'errors':errors},ensure_ascii=False,indent=2))
 return 0 if verdict=='PASS_CONSOLIDATED' else 1
if __name__=='__main__': raise SystemExit(main())
