#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse,csv,datetime as dt,hashlib,json
from pathlib import Path
TASK_ID='IMPERIUM-POPULATION-CENSUS-0001'; VALIDATOR_ID='population_census_validator.v0_1.fix_0001'
PATCH=Path('WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001'); OUT=PATCH/'OUTPUTS'; REC=PATCH/'RECEIPTS'; REP=PATCH/'REPORTS'
CENSUS_JSON=OUT/'IMPERIUM_POPULATION_CENSUS_V0_1.json'; CENSUS_CSV=OUT/'IMPERIUM_POPULATION_CENSUS_V0_1.csv'; SUMMARY_JSON=OUT/'IMPERIUM_POPULATION_SUMMARY_V0_1.json'; GAP_JSON=OUT/'IMPERIUM_POPULATION_GAP_MAP_V0_1.json'
RECEIPT_JSON=REC/'population_census_receipt.json'; VALIDATION_REPORT_MD=REP/'POPULATION_CENSUS_VALIDATION_REPORT_V0_1.md'
def now(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def readj(p): return json.loads(p.read_text(encoding='utf-8'))
def chk(checks,name,ok,details=None): checks.append({'name':name,'status':'PASS' if ok else 'FAIL','details':details or {}})
def validate(root):
    checks=[]; errors=[]; req=[CENSUS_JSON,CENSUS_CSV,SUMMARY_JSON,GAP_JSON]
    missing=[p.as_posix() for p in req if not (root/p).is_file()]; chk(checks,'required_outputs_exist',not missing,{'missing':missing}); errors += [f'Missing output: {p}' for p in missing]
    census={}; summary={}; gaps={}
    if not missing:
        try: census=readj(root/CENSUS_JSON); summary=readj(root/SUMMARY_JSON); gaps=readj(root/GAP_JSON); chk(checks,'json_outputs_parse',True)
        except Exception as e: chk(checks,'json_outputs_parse',False,{'error':str(e)}); errors.append(f'JSON parse failed: {e}')
    res=census.get('residents',[]) if isinstance(census,dict) else []; scan=census.get('scan_scope',{}) if isinstance(census,dict) else {}; cs=census.get('summary',{}) if isinstance(census,dict) else {}
    chk(checks,'fix_0001_marker_present',bool(census.get('fix_0001_applied') and summary.get('fix_0001_applied')),{'census_fix':census.get('fix_0001_applied'),'summary_fix':summary.get('fix_0001_applied')})
    if not (census.get('fix_0001_applied') and summary.get('fix_0001_applied')): errors.append('FIX-0001 marker missing')
    chk(checks,'residents_is_non_empty_list',isinstance(res,list) and len(res)>0,{'count':len(res) if isinstance(res,list) else None})
    if not isinstance(res,list) or not res: errors.append('Residents list missing or empty')
    required=['imperium_id','kind','class','status','owner_candidate','path','root_zone','bytes','sha256']; miss=[]; ids=[]; phys=[]; badhash=[]; badsha=[]; rootbug=[]; pycache=[]
    for r in res if isinstance(res,list) else []:
        m=[f for f in required if f not in r or r[f] in (None,'')]
        if m and len(miss)<20: miss.append({'path':r.get('path'),'missing':m})
        ids.append(r.get('imperium_id'))
        pv=r.get('path')
        if pv:
            if '/' not in pv and r.get('root_zone')!='ROOT': rootbug.append({'path':pv,'root_zone':r.get('root_zone')})
            if '__pycache__' in pv.replace('\\','/'): pycache.append(pv)
            p=root/pv
            if not p.is_file(): phys.append(pv)
            else:
                if sha(p)!=r.get('sha256'): badhash.append(pv)
        if 'sha256' in r and len(str(r.get('sha256')))!=64: badsha.append(pv or r.get('imperium_id'))
    dup=sorted({x for x in ids if ids.count(x)>1})
    chk(checks,'all_residents_have_required_fields',not miss,{'examples':miss}); errors += ['Residents missing required fields'] if miss else []
    chk(checks,'imperium_ids_unique',not dup,{'duplicate_count':len(dup),'duplicates_sample':dup[:20]}); errors += [f'Duplicate imperium_id values found: {dup[:5]}'] if dup else []
    chk(checks,'resident_paths_exist',not phys,{'missing_count':len(phys),'missing_sample':phys[:20]}); errors += [f'Resident paths missing: {phys[:5]}'] if phys else []
    chk(checks,'resident_sha256_matches_files',not badhash,{'bad_hash_count':len(badhash),'bad_hash_sample':badhash[:20]}); errors += [f'SHA mismatch: {badhash[:5]}'] if badhash else []
    chk(checks,'resident_sha256_shape_valid',not badsha,{'bad_sha_len_count':len(badsha),'sample':badsha[:20]}); errors += [f'Bad sha shape: {badsha[:5]}'] if badsha else []
    chk(checks,'root_level_files_have_root_zone_ROOT',not rootbug,{'bad':rootbug[:20]}); errors += [f'Root-zone bug still present: {rootbug[:5]}'] if rootbug else []
    chk(checks,'no_pycache_residents',not pycache,{'pycache_residents':pycache[:20]}); errors += [f'__pycache__ residents found: {pycache[:5]}'] if pycache else []
    total=scan.get('total_files_scanned'); chk(checks,'scan_scope_count_matches_residents',isinstance(total,int) and total==len(res),{'scan_scope_total_files_scanned':total,'resident_count':len(res)}); errors += ['scan_scope.total_files_scanned does not match residents count'] if not (isinstance(total,int) and total==len(res)) else []
    chk(checks,'summary_counts_match_residents',summary.get('population_total')==len(res) and cs.get('population_total')==len(res),{'summary_json_population_total':summary.get('population_total'),'census_summary_population_total':cs.get('population_total'),'resident_count':len(res)})
    if summary.get('population_total')!=len(res) or cs.get('population_total')!=len(res): errors.append('Summary population totals do not match residents count')
    try:
        rows=sum(1 for _ in csv.DictReader((root/CENSUS_CSV).open('r',encoding='utf-8',newline='')))
        chk(checks,'csv_row_count_matches_residents',rows==len(res),{'csv_rows':rows,'resident_count':len(res)}); errors += ['CSV row count does not match resident count'] if rows!=len(res) else []
    except Exception as e: chk(checks,'csv_row_count_matches_residents',False,{'error':str(e)}); errors.append(f'CSV read failed: {e}')
    reqg=['unknown_root_zones','unknown_owner_residents','unknown_class_residents','organs_detected','great_nine_organs_detected','unknown_organ_candidates','organs_without_readme','schemas_without_obvious_validator','validators_without_obvious_receipt','receipts_without_obvious_report','warp_packs_detected','decode_warning_residents','root_level_residents']
    missingg=[k for k in reqg if k not in gaps]; chk(checks,'gap_map_has_required_keys',not missingg,{'missing_gap_keys':missingg}); errors += [f'Gap map missing keys: {missingg}'] if missingg else []
    badroot=any('/' not in str(x) for x in gaps.get('unknown_root_zones',[])); chk(checks,'unknown_root_zones_no_root_files',not badroot,{'unknown_root_zones':gaps.get('unknown_root_zones',[])})
    if badroot: errors.append('unknown_root_zones still contains root-level filenames')
    fake=False
    if len(res)>100:
        unknown=summary.get('unknown_owner_count',0)+summary.get('unknown_class_count',0); gap_sizes=sum(len(v) for v in gaps.values() if isinstance(v,list))
        fake = unknown==0 and gap_sizes==0
    chk(checks,'fake_green_guard_not_perfect_without_gaps',not fake,{'suspicion':fake}); errors += ['Fake-green suspicion'] if fake else []
    verdict='PASS' if not errors else 'FAIL'
    return {'receipt_id':'receipt.population_census.v0_1.fix_0001','task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'generated_at_utc':now(),'mode':'WARP_VALIDATION','fix_0001_applied':True,'organ_responsibility':{'sovereign_owner':'THRONE','registry_owner':'ADMINISTRATUM','implementation_custodian':'MECHANICUS','trust_auditor':'CUSTODES','adversarial_checker':'INQUISITION','canon_reference':'DOCTRINARIUM','strategy_consumer':'STRATEGIUM'},'outputs':{'census_json':CENSUS_JSON.as_posix(),'census_csv':CENSUS_CSV.as_posix(),'summary_json':SUMMARY_JSON.as_posix(),'gap_json':GAP_JSON.as_posix()},'population_total':len(res),'summary':summary,'checks':checks,'errors':errors,'meaning':'PASS means fixed census lens is structurally valid, not that Imperium is healthy.'}
def write(root,receipt):
    (root/REC).mkdir(parents=True,exist_ok=True); (root/REP).mkdir(parents=True,exist_ok=True); (root/RECEIPT_JSON).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    checks='\n'.join(f"- `{c['status']}` — {c['name']}" for c in receipt['checks']); errors='\n'.join(f'- {e}' for e in receipt['errors']) if receipt['errors'] else '- none'
    (root/VALIDATION_REPORT_MD).write_text(f'''# POPULATION CENSUS VALIDATION REPORT V0.1\n\ntask_id: `{TASK_ID}`  \nvalidator_id: `{VALIDATOR_ID}`  \nverdict: `{receipt['verdict']}`  \ngenerated_at_utc: `{receipt['generated_at_utc']}`  \nfix: `0001`\n\n## Population\n\npopulation_total: `{receipt['population_total']}`\n\n## Checks\n\n{checks}\n\n## Errors\n\n{errors}\n\n## Receipt\n\n`{RECEIPT_JSON.as_posix()}`\n''',encoding='utf-8')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); args=ap.parse_args(); root=Path(args.repo_root).resolve(); receipt=validate(root); write(root,receipt)
    print(json.dumps({'task_id':TASK_ID,'validator_id':VALIDATOR_ID,'fix_0001_applied':True,'verdict':receipt['verdict'],'population_total':receipt['population_total'],'owner_coverage_score':receipt['summary'].get('owner_coverage_score'),'classification_coverage_score':receipt['summary'].get('classification_coverage_score'),'unknown_owner_count':receipt['summary'].get('unknown_owner_count'),'unknown_class_count':receipt['summary'].get('unknown_class_count'),'rogue_candidate_count':receipt['summary'].get('rogue_candidate_count'),'receipt':RECEIPT_JSON.as_posix(),'report':VALIDATION_REPORT_MD.as_posix(),'errors':receipt['errors']},ensure_ascii=False,indent=2))
    return 0 if receipt['verdict']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
