#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, json, subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple
TASK_ID='DOCTRINARIUM-PACK-TAXONOMY-AND-SERVITOR-TASK-LAW-0001'
VALIDATOR_ID='doctrinarium_pack_taxonomy_law_validator.v0_1'
TAXONOMY=Path('ORGANS/DOCTRINARIUM/MATRICES/PACK_TAXONOMY_MATRIX_V0_1.json')
SERVITOR_LAW=Path('ORGANS/DOCTRINARIUM/MATRICES/SERVITOR_TASK_PACK_LAW_MATRIX_V0_1.json')
PATCH_LAW=Path('ORGANS/DOCTRINARIUM/MATRICES/PATCH_PACK_LAW_MATRIX_V0_1.json')
SCHEMA=Path('ORGANS/DOCTRINARIUM/SCHEMAS/pack_taxonomy_law.schema.json')
DOCTRINE=Path('ORGANS/DOCTRINARIUM/DOCTRINE/PACK_TAXONOMY_AND_SERVITOR_TASK_LAW_V0_1.md')
RECEIPT=Path('ORGANS/DOCTRINARIUM/RECEIPTS/pack_taxonomy_law_receipt.json')
REPORT=Path('ORGANS/DOCTRINARIUM/REPORTS/PACK_TAXONOMY_LAW_REPORT_V0_1.md')
SUMMARY=Path('ORGANS/DOCTRINARIUM/REPORTS/PACK_TAXONOMY_LAW_SUMMARY_V0_1.json')
REQUIRED_LAWS=['INTAKE_DRAFT is not VALID_TASK_PACK','TASK_PACK is for SERVITOR work only','VALID_TASK_PACK requires SERVITOR context and authority envelope','SERVITOR_OUTPUT is not PATCH_PACK','SERVITOR_OUTPUT cannot mutate Reality','Reality mutation path is PATCH_PACK under Owner + Logos Prime control','Patch Pack does not require Servitor','Task Pack cannot be dispatched without validation','00_INTAKE folder must not be counted as valid Task Pack','Receipt existence is not task completion proof']
REQUIRED_SERVITOR_SECTIONS=['servitor_identity_or_class','authority_envelope','context_pack_manifest','allowed_read_scope','allowed_write_scope','forbidden_actions','output_contract','stop_conditions','validation_plan','quarantine_or_return_path']
REQUIRED_PATCH_SECTIONS=['patch_id','patch_pack_doc','files_to_land_or_explicit_no_land','runner_or_explicit_no_runner','validator_or_validation_gap','expected_verdict_or_expected_output','manifest_hashes','receipt_path_or_expected_receipt']
def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def git_head(repo:Path):
    try:
        p=subprocess.run(['git','rev-parse','HEAD'],cwd=str(repo),capture_output=True,text=True,timeout=20)
        return p.stdout.strip() if p.returncode==0 else 'UNKNOWN'
    except Exception: return 'UNKNOWN'
def add(checks,name,ok,details=None): checks.append({'name':name,'status':'PASS' if ok else 'FAIL','details':details or {}})
def load_json(path:Path):
    try: return json.loads(path.read_text(encoding='utf-8')), None
    except Exception as e: return None, str(e)
def discover_intake_drafts(repo:Path):
    roots=[]
    for base in [repo/'WARP/TASKS', repo/'ORGANS/ASTRONOMICON/REPORTS/DRY_RUN_SELFTEST_TASKS']:
        if base.is_dir():
            roots += [p.relative_to(repo).as_posix() for p in base.glob('*/00_INTAKE') if p.is_dir()]
    return sorted(roots)
def discover_patch_packs(repo:Path):
    base=repo/'WARP/PATCHES'
    if not base.is_dir(): return []
    out=[]
    for d in base.iterdir():
        if d.is_dir() and ((d/'PATCH_PACK.md').is_file() or (d/'PATCH_FILE_MANIFEST_SHA256.json').is_file() or any(p.name.upper().startswith('RUN_') and p.suffix.lower()=='.ps1' for p in d.iterdir() if p.is_file())):
            out.append(d.relative_to(repo).as_posix())
    return sorted(out)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('--apply',action='store_true'); args=ap.parse_args(); repo=Path(args.repo_root).resolve()
    checks=[]; errors=[]; warnings=[]
    for rel in [TAXONOMY,SERVITOR_LAW,PATCH_LAW,SCHEMA,DOCTRINE]:
        ok=(repo/rel).is_file(); add(checks,f'{rel.name}_exists',ok,{'path':rel.as_posix()})
        if not ok: errors.append(f'missing {rel.as_posix()}')
    taxonomy,err=load_json(repo/TAXONOMY) if (repo/TAXONOMY).is_file() else ({},'missing')
    add(checks,'pack_taxonomy_matrix_parses',err is None,{'error':err});
    if err: errors.append('taxonomy parse failed: '+err); taxonomy={}
    servitor,err=load_json(repo/SERVITOR_LAW) if (repo/SERVITOR_LAW).is_file() else ({},'missing')
    add(checks,'servitor_task_pack_law_parses',err is None,{'error':err});
    if err: errors.append('servitor law parse failed: '+err); servitor={}
    patchlaw,err=load_json(repo/PATCH_LAW) if (repo/PATCH_LAW).is_file() else ({},'missing')
    add(checks,'patch_pack_law_parses',err is None,{'error':err});
    if err: errors.append('patch law parse failed: '+err); patchlaw={}
    missing=[x for x in REQUIRED_LAWS if x not in taxonomy.get('hard_laws',[])]
    add(checks,'required_pack_hard_laws_present',not missing,{'missing_laws':missing});
    if missing: errors.append('missing hard laws: '+', '.join(missing))
    formulae=taxonomy.get('core_formulae',{})
    formula_ok=formulae.get('patch_pack_formula')=='OWNER + LOGOS_PRIME = PATCH_PACK' and formulae.get('task_pack_formula')=='OWNER + LOGOS_PRIME + SERVITOR = TASK_PACK'
    add(checks,'owner_logos_servitor_formulae_present',formula_ok,{'formulae':formulae})
    if not formula_ok: errors.append('core formulae incorrect')
    entities=taxonomy.get('entities',{})
    required_entities=['INTAKE_DRAFT','PATCH_PACK','TASK_PACK_CANDIDATE','VALID_TASK_PACK','SERVITOR_OUTPUT','PATCH_PACK_FROM_SERVITOR_OUTPUT']
    missing_entities=[x for x in required_entities if x not in entities]
    add(checks,'required_pack_entities_defined',not missing_entities,{'missing_entities':missing_entities})
    if missing_entities: errors.append('missing pack entities: '+', '.join(missing_entities))
    intake=entities.get('INTAKE_DRAFT',{})
    intake_ok=intake.get('servitor_dispatch_allowed') is False and intake.get('reality_mutation_allowed') is False and 'VALID_TASK_PACK' in intake.get('must_not_claim',[])
    add(checks,'intake_draft_cannot_be_task_pack_or_dispatch',intake_ok,intake)
    if not intake_ok: errors.append('INTAKE_DRAFT law weak')
    task=entities.get('VALID_TASK_PACK',{})
    task_ok=task.get('servitor_dispatch_allowed') is True and task.get('reality_mutation_allowed') is False and 'PATCH_PACK' in task.get('must_not_claim',[])
    add(checks,'valid_task_pack_is_servitor_only_not_reality_mutation',task_ok,task)
    if not task_ok: errors.append('VALID_TASK_PACK law weak')
    output=entities.get('SERVITOR_OUTPUT',{})
    output_ok=output.get('reality_mutation_allowed') is False and 'PATCH_PACK' in output.get('must_not_claim',[]) and 'REALITY_MUTATION' in output.get('must_not_claim',[])
    add(checks,'servitor_output_not_patch_pack_or_reality',output_ok,output)
    if not output_ok: errors.append('SERVITOR_OUTPUT law weak')
    miss_sec=[x for x in REQUIRED_SERVITOR_SECTIONS if x not in servitor.get('required_sections_for_valid_task_pack',[])]
    add(checks,'valid_task_pack_required_sections_present',not miss_sec,{'missing':miss_sec});
    if miss_sec: errors.append('missing valid task pack sections: '+', '.join(miss_sec))
    miss_patch=[x for x in REQUIRED_PATCH_SECTIONS if x not in patchlaw.get('required_sections_for_patch_pack',[])]
    add(checks,'patch_pack_required_sections_present',not miss_patch,{'missing':miss_patch});
    if miss_patch: errors.append('missing patch sections: '+', '.join(miss_patch))
    fs=servitor.get('forbidden_shortcuts',[]); short_ok='INTAKE_DRAFT -> DISPATCHED_TO_SERVITOR' in fs and 'SERVITOR_OUTPUT -> REALITY_MUTATION' in fs
    add(checks,'servitor_forbidden_shortcuts_present',short_ok,{'forbidden_shortcuts':fs})
    if not short_ok: errors.append('servitor forbidden shortcuts incomplete')
    intake_drafts=discover_intake_drafts(repo); patch_packs=discover_patch_packs(repo)
    add(checks,'existing_00_intake_discovered_as_intake_drafts_only',True,{'intake_draft_count':len(intake_drafts),'sample':intake_drafts[:10]})
    add(checks,'existing_patch_packs_discovered_as_patch_packs',True,{'patch_pack_count':len(patch_packs),'sample':patch_packs[-10:]})
    violations=[]
    for rel in intake_drafts:
        f=repo/rel/'ASTRONOMICON_DRY_RUN_RECEIPT.json'
        if f.is_file():
            data,e=load_json(f)
            if not e and data.get('execution_allowed') is not False: violations.append(rel)
    add(checks,'dry_run_receipts_block_execution',not violations,{'violations':violations})
    if violations: errors.append('dry-run receipts allow execution: '+', '.join(violations))
    verdict='PASS_PACK_TAXONOMY_LAW_VALIDATED' if not errors else 'FAIL_PACK_TAXONOMY_LAW'
    generated=utc()
    summary={'summary_id':'doctrinarium.pack_taxonomy_law_summary.v0_1','task_id':TASK_ID,'validator_id':VALIDATOR_ID,'generated_at_utc':generated,'repo_head':git_head(repo),'verdict':verdict,'intake_draft_count':len(intake_drafts),'patch_pack_count':len(patch_packs),'core_formulae':formulae,'law_state':'MACHINE_VALIDATED' if not errors else 'FAILED','meaning':'Pack taxonomy laws are readable and enforce that Task Pack is Servitor-only while Patch Pack is Owner+Logos Prime Reality patch path.'}
    receipt={'receipt_id':'receipt.doctrinarium.pack_taxonomy_law.v0_1','task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'generated_at_utc':generated,'repo_head':git_head(repo),'checks':checks,'warnings':warnings,'errors':errors,'summary':SUMMARY.as_posix(),'report':REPORT.as_posix(),'meaning':summary['meaning']}
    for out in [RECEIPT,REPORT,SUMMARY]: (repo/out).parent.mkdir(parents=True,exist_ok=True)
    (repo/SUMMARY).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (repo/RECEIPT).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    checks_md='\n'.join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md='\n'.join(f'- {e}' for e in errors) if errors else '- none'
    warnings_md='\n'.join(f'- {w}' for w in warnings) if warnings else '- none'
    (repo/REPORT).write_text(f"""# PACK TAXONOMY LAW REPORT V0.1\n\ntask_id: `{TASK_ID}`  \nvalidator_id: `{VALIDATOR_ID}`  \nverdict: `{verdict}`  \ngenerated_at_utc: `{generated}`  \nrepo_head: `{git_head(repo)}`\n\n## Core formulae\n\n```text\nOwner + Logos Prime = Patch Pack\nOwner + Logos Prime + Servitor = Task Pack\n```\n\n## Meaning\n\nTask Pack is a Servitor work order, not every task. Patch Pack is the manual WARP package created by Owner + Logos Prime. Current Astronomicon `00_INTAKE` folders are Intake Drafts, not valid Task Packs.\n\n## Current discovery\n\n- intake_draft_count: `{len(intake_drafts)}`\n- patch_pack_count: `{len(patch_packs)}`\n\n## Checks\n\n{checks_md}\n\n## Warnings\n\n{warnings_md}\n\n## Errors\n\n{errors_md}\n""",encoding='utf-8')
    print(json.dumps({'task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'intake_draft_count':len(intake_drafts),'patch_pack_count':len(patch_packs),'receipt':RECEIPT.as_posix(),'report':REPORT.as_posix(),'summary':SUMMARY.as_posix(),'errors':errors,'warnings':warnings},ensure_ascii=False,indent=2))
    return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
