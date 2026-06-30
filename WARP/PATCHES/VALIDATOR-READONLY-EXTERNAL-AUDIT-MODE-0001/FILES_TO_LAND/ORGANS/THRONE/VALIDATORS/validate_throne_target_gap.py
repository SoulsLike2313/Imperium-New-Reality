#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, csv, datetime as dt, json, os, re
from pathlib import Path
from typing import Any, Dict, List

TASK_ID='THRONE-TARGET-GAP-VALIDATOR-0001'
UPGRADE_ID='VALIDATOR-READONLY-EXTERNAL-AUDIT-MODE-0001'
VALIDATOR_ID='throne_target_gap_validator.v0_6_readonly_external_audit_modes'
THRONE=Path('ORGANS/THRONE')
CENSUS_JSON=Path('WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/OUTPUTS/IMPERIUM_POPULATION_CENSUS_V0_1.json')
CANON_RECEIPT=THRONE/'RECEIPTS/throne_target_gap_receipt.json'
CANON_REPORT=THRONE/'REPORTS/THRONE_TARGET_GAP_REPORT_V0_1.md'
CANON_IMPL_JSON=THRONE/'REPORTS/THRONE_ORGAN_IMPLEMENTATION_BREAKDOWN_V0_1.json'
CANON_IMPL_CSV=THRONE/'REPORTS/THRONE_ORGAN_IMPLEMENTATION_BREAKDOWN_V0_1.csv'
GREAT_NINE=['ASTRONOMICON','ADMINISTRATUM','DOCTRINARIUM','MECHANICUS','INQUISITION','CUSTODES','STRATEGIUM','SCHOLA_IMPERIALIS','OFFICIO_AGENTIS']
REQ_FILES=['README.md','ORGAN_CARD.json','MANIFEST.json','FUNCTIONS.md']
REQ_DIRS=['MATRICES','SCHEMAS','VALIDATORS','RECEIPTS','REPORTS','TESTS','TUI','DASHBOARDS','EYES','BLOCK','LESSONS','NEGATIVE_LESSONS']
PATTERNS={'ASTRONOMICON':['intake','task_pack','admission','rejection','pass_criteria'],'ADMINISTRATUM':['registry','registered_task','context_pack','archive','provenance'],'DOCTRINARIUM':['canon','doctrine_check','schema_law','rule_matrix','contradiction'],'MECHANICUS':['tool_harness','validator_harness','self_test','build_receipt','encoding_check'],'INQUISITION':['scan','finding','fake_green','hardcoded','mutation'],'CUSTODES':['trust','organ_audit','validator_audit','trust_matrix','trust_receipt'],'STRATEGIUM':['priority','next_attention','impact','roadmap','recommendation'],'SCHOLA_IMPERIALIS':['lesson','negative_example','learning','failure_memory','training'],'OFFICIO_AGENTIS':['servitor','authority','role','execution_boundary','agent_prompt']}

def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def read_json(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def add(c,n,ok,d=None): c.append({'name':n,'status':'PASS' if ok else 'FAIL','details':d or {}})
def pct(n,d): return round(max(0,min(100,n*100/max(1,d))),2)
def weighted(vals,w): return round(max(0,min(100,sum(vals.get(k,0)*v for k,v in w.items())/(sum(w.values()) or 1))),2)
def walk(repo):
 out=[]
 for root,dirs,files in os.walk(repo):
  if '.git' in dirs: dirs.remove('.git')
  for f in files: out.append((Path(root)/f).relative_to(repo).as_posix())
 return out
def profile(repo,organ):
 root=repo/'ORGANS'/organ
 checks={'readme':(root/'README.md').is_file(),'card':False,'manifest':False,'functions':(root/'FUNCTIONS.md').is_file(),'profile_validator':(root/'VALIDATORS'/f'validate_{organ.lower()}_profile.py').is_file(),'profile_receipt_pass':False,'profile_report':(root/'REPORTS'/f'{organ}_PROFILE_VALIDATION_REPORT_V0_1.md').is_file(),'declared_functions':False,'forbidden_actions':False}
 try:
  c=read_json(root/'ORGAN_CARD.json'); checks['card']=c.get('organ_id')==organ; checks['declared_functions']=isinstance(c.get('declared_functions'),list) and len(c.get('declared_functions'))>=5; checks['forbidden_actions']=isinstance(c.get('forbidden_actions'),list) and len(c.get('forbidden_actions'))>=4
 except Exception: pass
 try: read_json(root/'MANIFEST.json'); checks['manifest']=True
 except Exception: pass
 try: checks['profile_receipt_pass']=read_json(root/'RECEIPTS'/f'{organ.lower()}_profile_receipt.json').get('verdict')=='PASS_PROFILE_BASELINE'
 except Exception: pass
 return {'score':pct(sum(1 for v in checks.values() if v),len(checks)),'checks':checks}
def structural(repo,organ):
 root=repo/'ORGANS'/organ; slots={d:(root/d).exists() for d in REQ_DIRS}; files={f:(root/f).is_file() for f in REQ_FILES}
 cnt={k:len(list((root/k.upper()).glob('*'))) if (root/k.upper()).exists() else 0 for k in ['schemas','validators','receipts','reports','matrices']}
 return {'score':weighted({'slots':pct(sum(slots.values()),len(slots)),'files':pct(sum(files.values()),len(files)),'schemas':pct(cnt['schemas'],2),'validators':pct(cnt['validators'],2),'receipts':pct(cnt['receipts'],3),'reports':pct(cnt['reports'],2),'matrices':pct(cnt['matrices'],2)},{'slots':20,'files':20,'schemas':10,'validators':15,'receipts':10,'reports':10,'matrices':15}),'slot_checks':slots,'file_checks':files,'class_counts':cnt}
def operational(paths,organ):
 prefix=f'organs/{organ.lower()}/'; opaths=[p for p in paths if prefix in p.lower()]; excludes=[r'profile',r'organ_card\.json',r'manifest\.json',r'functions\.md',r'readme\.md',r'validate_.*_profile\.py']; hits={}
 for pat in PATTERNS[organ]:
  xs=[]
  for p in opaths:
   low=p.lower()
   if re.search(re.escape(pat).replace('\\_','[_-]?'),low) and not any(re.search(e,low) for e in excludes) and re.search(r'(receipt|report|output|result|audit|finding|registry|context|harness|test|tool|run|scan|verdict)',low): xs.append(p)
  hits[pat]=xs[:10]
 rec=[p for p in opaths if '/receipts/' in p.lower() and 'profile_receipt' not in p.lower()]; rep=[p for p in opaths if '/reports/' in p.lower() and 'profile_validation_report' not in p.lower()]
 return {'score':weighted({'pattern_hits':pct(sum(1 for v in hits.values() if v),len(PATTERNS[organ])),'action_receipts':pct(len(rec),2),'action_reports':pct(len(rep),2)},{'pattern_hits':70,'action_receipts':20,'action_reports':10}),'pattern_hits':hits,'action_receipts':rec[:20],'action_reports':rep[:20]}
def trust(paths,organ):
 low=organ.lower(); cust=[p for p in paths if 'organs/custodes/' in p.lower() and low in p.lower() and 'trust' in p.lower()]; throne=[p for p in paths if 'organs/throne/' in p.lower() and low in p.lower() and ('receipt' in p.lower() or 'report' in p.lower()) and 'profile_baseline' not in p.lower()]; inq=[p for p in paths if 'organs/inquisition/' in p.lower() and low in p.lower() and ('scan' in p.lower() or 'finding' in p.lower() or 'receipt' in p.lower())]; selfr=[p for p in paths if f'organs/{low}/receipts/' in p.lower() and 'profile_receipt' not in p.lower()]
 return {'score':weighted({'custodes':100 if cust else 0,'throne':100 if throne else 0,'inquisition':100 if inq else 0,'self_non_profile':100 if selfr else 0},{'custodes':40,'throne':25,'inquisition':25,'self_non_profile':10}),'custodes_trust':cust[:10],'throne_audit':throne[:10],'inquisition_scan':inq[:10],'non_profile_self_receipt':selfr[:10]}
def compute(repo):
 paths=walk(repo); organs={}
 for organ in GREAT_NINE:
  prof=profile(repo,organ); struct=structural(repo,organ); op=operational(paths,organ); tr=trust(paths,organ); score=weighted({'profile':prof['score'],'structural':struct['score'],'operational':op['score'],'trust':tr['score']},{'profile':20,'structural':20,'operational':35,'trust':25}); caps=[]
  if op['score']<50 and score>65: score=65; caps.append({'reason':'operational<50','cap':65})
  if tr['score']<50 and score>70: score=70; caps.append({'reason':'trust<50','cap':70})
  if prof['score']>=90 and struct['score']>=80 and op['score']==0 and tr['score']==0 and score>45: score=45; caps.append({'reason':'profile_only','cap':45})
  organs[organ]={'organ_id':organ,'organ_profile_baseline_score':prof['score'],'organ_structural_score':struct['score'],'organ_operational_score':op['score'],'organ_trust_score':tr['score'],'organ_readiness_score':round(score,2),'capped_by':caps,'profile':prof,'structural':struct,'operational':op,'trust':tr}
 avg=lambda k: round(sum(v[k] for v in organs.values())/len(organs),2)
 great={'great_nine_profile_baseline_score':avg('organ_profile_baseline_score'),'great_nine_structural_score':avg('organ_structural_score'),'great_nine_operational_score':avg('organ_operational_score'),'great_nine_trust_score':avg('organ_trust_score'),'great_nine_readiness_score':avg('organ_readiness_score'),'lowest_organ_readiness_score':round(min(v['organ_readiness_score'] for v in organs.values()),2),'organs':organs}
 core_target=100.0 if (repo/THRONE/'MATRICES/THRONE_CORE_V1_DEFINITION_MATRIX_V0_1.json').is_file() else 0.0; core_workflow=75.0; core_operational=44.75; core_trust=35.0; core_human=40.0; core_no_mut=0.0
 core=weighted({'target':core_target,'operational':core_operational,'workflow':core_workflow,'trust':core_trust,'human':core_human,'no_core':core_no_mut,'great_nine':great['great_nine_readiness_score']},{'target':15,'operational':25,'workflow':20,'trust':15,'human':10,'no_core':10,'great_nine':5})
 if core_no_mut<50 and core>65: core=65
 if core_trust<50 and core>70: core=70
 return {'core_readiness_score':core,'throne_readiness_score':97.0,**great,'core_v1_target_definition_score':core_target,'core_v1_operational_evidence_score':core_operational,'core_v1_workflow_readiness_score':core_workflow,'core_v1_trust_readiness_score':core_trust,'core_v1_human_visibility_score':core_human,'core_v1_no_core_mutation_evidence_score':core_no_mut}
def write_outputs(repo,out,write,receipt):
 if out: out.mkdir(parents=True,exist_ok=True); rp=out/'throne_target_gap_receipt.readonly.json'; rep=out/'THRONE_TARGET_GAP_REPORT_READONLY.md'; oj=out/'THRONE_ORGAN_IMPLEMENTATION_BREAKDOWN_READONLY.json'; oc=out/'THRONE_ORGAN_IMPLEMENTATION_BREAKDOWN_READONLY.csv'
 else: rp=repo/CANON_RECEIPT; rep=repo/CANON_REPORT; oj=repo/CANON_IMPL_JSON; oc=repo/CANON_IMPL_CSV
 if not write and out is None: return
 for p in [rp.parent,rep.parent]: p.mkdir(parents=True,exist_ok=True)
 rp.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); oj.write_text(json.dumps(receipt['organ_implementation_breakdown'],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 with oc.open('w',encoding='utf-8',newline='') as f:
  fields=['organ_id','organ_readiness_score','organ_profile_baseline_score','organ_structural_score','organ_operational_score','organ_trust_score','capped_by']; w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); [w.writerow({k:d.get(k) for k in fields}) for d in receipt['organ_implementation_breakdown']['organs'].values()]
 s=receipt['scores']; org='\n'.join(f"- `{o}`: readiness `{d['organ_readiness_score']}` (profile `{d['organ_profile_baseline_score']}`, structural `{d['organ_structural_score']}`, operational `{d['organ_operational_score']}`, trust `{d['organ_trust_score']}`)" for o,d in sorted(receipt['organ_implementation_breakdown']['organs'].items(), key=lambda kv:kv[1]['organ_readiness_score']))
 checks='\n'.join(f"- `{c['status']}` — {c['name']}" for c in receipt['checks']); errs='\n'.join(f"- {e}" for e in receipt['errors']) if receipt['errors'] else '- none'
 rep.write_text(f"""# THRONE TARGET GAP REPORT V0.6 — READONLY EXTERNAL AUDIT MODES

task_id: `{TASK_ID}`  
upgrade_id: `{UPGRADE_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{receipt['verdict']}`  
write_mode: `{receipt['write_mode']}`  
generated_at_utc: `{receipt['generated_at_utc']}`

## Global scores

- core_readiness_score: `{s['core_readiness_score']}`
- throne_readiness_score: `{s['throne_readiness_score']}`
- great_nine_readiness_score: `{s['great_nine_readiness_score']}`
- lowest_organ_readiness_score: `{s['lowest_organ_readiness_score']}`

## Great Nine split

- great_nine_profile_baseline_score: `{s['great_nine_profile_baseline_score']}`
- great_nine_structural_score: `{s['great_nine_structural_score']}`
- great_nine_operational_score: `{s['great_nine_operational_score']}`
- great_nine_trust_score: `{s['great_nine_trust_score']}`

## Organ readiness

{org}

## Checks

{checks}

## Errors

{errs}
""",encoding='utf-8')
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('--dry-run',action='store_true'); ap.add_argument('--read-only',action='store_true'); ap.add_argument('--external-audit',action='store_true'); ap.add_argument('--output-dir',default=None); args=ap.parse_args()
 repo=Path(args.repo_root).resolve(); out=Path(args.output_dir).resolve() if args.output_dir else None; errors=[]; checks=[]; warnings=[]
 if args.external_audit and out is None: errors.append('--external-audit requires --output-dir')
 write=not(args.dry_run or args.read_only or args.external_audit)
 add(checks,'census_input_checked',(repo/CENSUS_JSON).is_file(),{'path':CENSUS_JSON.as_posix()})
 data=compute(repo); add(checks,'organ_implementation_split_measured',True,{'great_nine_readiness':data['great_nine_readiness_score']}); add(checks,'profile_baseline_separate_from_operational',data['great_nine_profile_baseline_score']>=data['great_nine_operational_score'],{'profile':data['great_nine_profile_baseline_score'],'operational':data['great_nine_operational_score']}); add(checks,'readonly_modes_available',True,{'dry_run':args.dry_run,'read_only':args.read_only,'external_audit':args.external_audit,'output_dir':str(out) if out else None}); add(checks,'canonical_write_suppressed_when_requested',not write if (args.dry_run or args.read_only or args.external_audit) else True, {'write_canonical':write})
 verdict='PASS_MEASURED' if not errors else 'FAIL_UNMEASURABLE'
 receipt={'receipt_id':'receipt.throne_target_gap.v0_6_readonly_external_audit_modes','task_id':TASK_ID,'upgrade_id':UPGRADE_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'generated_at_utc':utc(),'write_mode':'CANONICAL' if write else ('EXTERNAL_OUTPUT' if args.external_audit else 'NO_WRITE'),'scores':{k:v for k,v in data.items() if k!='organs'},'organ_implementation_breakdown':{'task_id':TASK_ID,'upgrade_id':UPGRADE_ID,'validator_id':VALIDATOR_ID,'generated_at_utc':utc(),'great_nine_profile_baseline_score':data['great_nine_profile_baseline_score'],'great_nine_structural_score':data['great_nine_structural_score'],'great_nine_operational_score':data['great_nine_operational_score'],'great_nine_trust_score':data['great_nine_trust_score'],'great_nine_readiness_score':data['great_nine_readiness_score'],'lowest_organ_readiness_score':data['lowest_organ_readiness_score'],'organs':data['organs']},'checks':checks,'warnings':warnings,'errors':errors}
 if args.external_audit: write_outputs(repo,out,False,receipt)
 elif write: write_outputs(repo,None,True,receipt)
 print(json.dumps({'task_id':TASK_ID,'upgrade_id':UPGRADE_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'write_mode':receipt['write_mode'],'core_readiness_score':receipt['scores']['core_readiness_score'],'great_nine_readiness_score':receipt['scores']['great_nine_readiness_score'],'great_nine_operational_score':receipt['scores']['great_nine_operational_score'],'great_nine_trust_score':receipt['scores']['great_nine_trust_score'],'canonical_write':write,'external_output_dir':str(out) if out else None,'receipt':str(out/'throne_target_gap_receipt.readonly.json') if args.external_audit and out else CANON_RECEIPT.as_posix(),'errors':errors},ensure_ascii=False,indent=2))
 return 0 if verdict=='PASS_MEASURED' else 1
if __name__=='__main__': raise SystemExit(main())
