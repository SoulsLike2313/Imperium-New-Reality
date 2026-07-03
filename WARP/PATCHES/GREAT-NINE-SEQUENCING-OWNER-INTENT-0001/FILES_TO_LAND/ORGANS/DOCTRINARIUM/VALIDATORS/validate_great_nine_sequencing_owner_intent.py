#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, json
from pathlib import Path
from typing import Any, Dict, List
TASK_ID='GREAT-NINE-SEQUENCING-OWNER-INTENT-0001'
VALIDATOR_ID='doctrinarium_great_nine_sequencing_owner_intent_validator.v0_1'
OWNER_INTENT=Path('ORGANS/_CORE_GOVERNANCE/OWNER_DECISIONS/OWNER_INTENT_ADMINISTRATUM_LAST_IN_GREAT_NINE_V0_1.md')
SCHEMA=Path('ORGANS/DOCTRINARIUM/SCHEMAS/NEXT_ORGAN_SELECTION_SCHEMA_V0_1.json')
MATRIX=Path('ORGANS/DOCTRINARIUM/MATRICES/NEXT_PRIMARY_ORGAN_SELECTION_MATRIX_V0_1.json')
READOUT=Path('ORGANS/DOCTRINARIUM/REPORTS/NEXT_ORGAN_SELECTION_READOUT_V0_1.md')
RECEIPT=Path('ORGANS/DOCTRINARIUM/RECEIPTS/great_nine_sequencing_owner_intent_receipt.json')
SUMMARY=Path('ORGANS/DOCTRINARIUM/REPORTS/GREAT_NINE_SEQUENCING_OWNER_INTENT_SUMMARY_V0_1.json')
REPORT=Path('ORGANS/DOCTRINARIUM/REPORTS/GREAT_NINE_SEQUENCING_OWNER_INTENT_REPORT_V0_1.md')
def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def load_json(p:Path):
    try: return json.loads(p.read_text(encoding='utf-8-sig')), None
    except Exception as e: return None, str(e)
def write_json(p:Path,d:Any):
    p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def add(ch:List[Dict[str,Any]],name:str,ok:bool,details:Dict[str,Any]|None=None): ch.append({'name':name,'status':'PASS' if ok else 'FAIL','details':details or {}})
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('--apply',action='store_true'); args=ap.parse_args(); repo=Path(args.repo_root).resolve()
    checks=[]; errors=[]; warnings=[]
    op=repo/OWNER_INTENT; txt=op.read_text(encoding='utf-8') if op.is_file() else ''
    add(checks,'owner_intent_administratum_last_file_exists',op.is_file(),{'path':OWNER_INTENT.as_posix(),'bytes':op.stat().st_size if op.is_file() else 0})
    if not op.is_file(): errors.append('owner intent file missing')
    missing=[p for p in ['Administratum is to be built last among the Great Nine organs','registrar of emptiness','other organs first producing their own truthful self-description','does not claim','Core v1 ready'] if p not in txt]
    add(checks,'owner_intent_contains_last_sequence_and_boundary_law',not missing,{'missing_phrases':missing})
    if missing: errors.append('owner intent missing required sequencing/boundary phrases')
    schema,s_err=load_json(repo/SCHEMA) if (repo/SCHEMA).is_file() else ({},'missing')
    add(checks,'next_organ_selection_schema_exists_and_parses',s_err is None,{'path':SCHEMA.as_posix(),'error':s_err})
    if s_err: errors.append('next organ selection schema missing or invalid')
    matrix,m_err=load_json(repo/MATRIX) if (repo/MATRIX).is_file() else ({},'missing')
    add(checks,'next_organ_selection_matrix_exists_and_parses',m_err is None,{'path':MATRIX.as_posix(),'error':m_err})
    if m_err: errors.append('next organ selection matrix missing or invalid')
    weights=matrix.get('weights',{}) if isinstance(matrix,dict) else {}; weight_sum=sum(weights.values()) if isinstance(weights,dict) else 0
    add(checks,'selection_weights_sum_to_100',weight_sum==100,{'weight_sum':weight_sum,'weights':weights})
    if weight_sum!=100: errors.append('selection weights do not sum to 100')
    candidates=matrix.get('candidates',[]) if isinstance(matrix,dict) else []; by_id={c.get('organ_id'):c for c in candidates if isinstance(c,dict)}
    required=['MECHANICUS','DOCTRINARIUM','INQUISITION','CUSTODES','STRATEGIUM','ADMINISTRATUM','THRONE']; missing_c=[x for x in required if x not in by_id]
    add(checks,'selection_matrix_contains_required_candidate_organs',not missing_c,{'missing':missing_c,'actual':list(by_id.keys())})
    if missing_c: errors.append('selection matrix missing required candidate organs')
    adm=by_id.get('ADMINISTRATUM',{}); adm_ok=adm.get('sequence_status')=='DEFERRED_TO_LAST_GREAT_NINE'
    add(checks,'administratum_is_deferred_to_last_great_nine',adm_ok,{'sequence_status':adm.get('sequence_status'),'reasoning':adm.get('reasoning')})
    if not adm_ok: errors.append('Administratum is not deferred to last Great Nine')
    throne=by_id.get('THRONE',{}); th_ok=throne.get('sequence_status')=='SPECIAL_CROWN_ORGAN'
    add(checks,'throne_is_marked_special_crown_organ_not_ordinary_next',th_ok,{'sequence_status':throne.get('sequence_status')})
    if not th_ok: errors.append('Throne is not marked as special crown organ')
    rec=matrix.get('recommended_next_primary_organ') if isinstance(matrix,dict) else None
    add(checks,'recommended_next_primary_organ_is_mechanicus',rec=='MECHANICUS',{'recommended':rec})
    if rec!='MECHANICUS': errors.append('recommended next primary organ is not Mechanicus')
    eligible=[c for c in candidates if c.get('sequence_status')=='ELIGIBLE']; elig_sorted=sorted(eligible,key=lambda c:c.get('weighted_score_0_to_100',0),reverse=True); top=elig_sorted[0].get('organ_id') if elig_sorted else None
    add(checks,'mechanicus_has_highest_eligible_weighted_score',top=='MECHANICUS',{'top_eligible':top,'eligible_scores':[{'organ_id':c.get('organ_id'),'score':c.get('weighted_score_0_to_100')} for c in elig_sorted]})
    if top!='MECHANICUS': errors.append('Mechanicus does not have highest eligible weighted score')
    cons=matrix.get('owner_constraints',[]) if isinstance(matrix,dict) else []; cons_text=json.dumps(cons,ensure_ascii=False)
    cons_ok='ADMINISTRATUM_LAST_IN_GREAT_NINE' in cons_text and 'THRONE_IS_SPECIAL_CROWN_ORGAN' in cons_text
    add(checks,'selection_matrix_contains_owner_constraints',cons_ok,{'owner_constraints':cons})
    if not cons_ok: errors.append('selection matrix missing owner constraints')
    rp=repo/READOUT; rt=rp.read_text(encoding='utf-8') if rp.is_file() else ''; ro_ok=rp.is_file() and 'MECHANICUS' in rt and 'Administratum is deferred' in rt
    add(checks,'readout_exists_and_states_mechanicus_recommendation',ro_ok,{'path':READOUT.as_posix(),'bytes':rp.stat().st_size if rp.is_file() else 0})
    if not ro_ok: errors.append('selection readout missing or incomplete')
    verdict='PASS_GREAT_NINE_SEQUENCING_OWNER_INTENT_READY' if not errors else 'FAIL_GREAT_NINE_SEQUENCING_OWNER_INTENT'; generated=utc()
    summary={'summary_id':'doctrinarium.great_nine_sequencing_owner_intent_summary.v0_1','task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'generated_at_utc':generated,'checks':checks,'errors':errors,'warnings':warnings,'recommended_next_primary_organ':rec,'owner_intent':'Administratum deferred to last Great Nine consolidation.'}
    receipt={'receipt_id':'receipt.doctrinarium.great_nine_sequencing_owner_intent.v0_1','task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'generated_at_utc':generated,'checks':checks,'errors':errors,'warnings':warnings,'owner_intent':OWNER_INTENT.as_posix(),'schema':SCHEMA.as_posix(),'matrix':MATRIX.as_posix(),'readout':READOUT.as_posix()}
    write_json(repo/SUMMARY,summary); write_json(repo/RECEIPT,receipt)
    checks_md='\n'.join(f"- `{c['status']}` — {c['name']}" for c in checks); errors_md='\n'.join(f'- {e}' for e in errors) if errors else '- none'; warnings_md='\n'.join(f'- {w}' for w in warnings) if warnings else '- none'
    (repo/REPORT).write_text(f'''# GREAT NINE SEQUENCING OWNER INTENT REPORT V0.1\n\ntask_id: `{TASK_ID}`  \nvalidator_id: `{VALIDATOR_ID}`  \nverdict: `{verdict}`  \ngenerated_at_utc: `{generated}`\n\n## Meaning\n\nThis validator proves Owner intent that Administratum is last among the Great Nine, and validates the mathematical next-organ selection matrix.\n\nRecommended next primary organ:\n\n```text\n{rec}\n```\n\n## Checks\n\n{checks_md}\n\n## Warnings\n\n{warnings_md}\n\n## Errors\n\n{errors_md}\n''',encoding='utf-8')
    print(json.dumps({'task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'receipt':RECEIPT.as_posix(),'summary':SUMMARY.as_posix(),'recommended_next_primary_organ':rec,'errors':errors,'warnings':warnings},ensure_ascii=False,indent=2))
    return 0 if verdict.startswith('PASS') else 1
if __name__=='__main__': raise SystemExit(main())
