#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, json, subprocess, sys
from pathlib import Path
TASK_ID='MECHANICUS-JSON-EVIDENCE-STRICT-LANE-0001'; VALIDATOR_ID='mechanicus_json_evidence_strict_lane_validator.v0_1'
LAW=Path('ORGANS/MECHANICUS/LAWS/MECHANICUS_JSON_EVIDENCE_STRICT_LANE_LAW_V0_1.json'); MATRIX=Path('ORGANS/MECHANICUS/MATRICES/MECHANICUS_JSON_EVIDENCE_STRICT_LANE_MATRIX_V0_1.json'); CUST=Path('ORGANS/CUSTODES/MATRICES/CUSTODES_MECHANICUS_JSON_EVIDENCE_STRICT_LANE_PROSECUTOR_MATRIX_V0_1.json'); THRONE=Path('ORGANS/THRONE/MATRICES/THRONE_MECHANICUS_JSON_EVIDENCE_STRICT_LANE_CROWN_GATE_MATRIX_V0_1.json')
SCANNER=Path('ORGANS/MECHANICUS/TOOLS/scan_mechanicus_json_evidence_strict_lane.py'); DISPATCH=Path('ORGANS/MECHANICUS/TOOLS/run_language_validation_dispatch.py'); READOUT=Path('ORGANS/MECHANICUS/TOOLS/generate_strict_language_lane_readout.py')
STRICT=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_JSON_EVIDENCE_STRICT_LANE_REPORT_V0_1.json'); DISPATCH_R=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_LANGUAGE_VALIDATION_BASELINE_V0_1.json'); READOUT_R=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_LANGUAGE_LANE_READOUT_V0_1.json')
RECEIPT=Path('ORGANS/MECHANICUS/RECEIPTS/mechanicus_json_evidence_strict_lane_receipt.json'); SUMMARY=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_JSON_EVIDENCE_STRICT_LANE_SUMMARY_V0_1.json'); REPORT=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_JSON_EVIDENCE_STRICT_LANE_VALIDATION_REPORT_V0_1.md')
def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def load(p):
    try: return json.loads(p.read_text(encoding='utf-8-sig')), None
    except Exception as e: return None, str(e)
def write(p,o): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(o,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf-8')
def add(ch,n,ok,d=None): ch.append({'name':n,'status':'PASS' if ok else 'FAIL','details':d or {}})
def contains(p,needles):
    if not p.is_file(): return False
    t=p.read_text(encoding='utf-8',errors='replace'); return all(n in t for n in needles)
def run(repo,script,args,timeout=300):
    p=subprocess.run([sys.executable,str(repo/script)]+args,cwd=str(repo),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
    return {'exit_code':p.returncode,'stdout_tail':p.stdout[-5000:],'stderr_tail':p.stderr[-3000:]}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('--apply',action='store_true'); a=ap.parse_args(); repo=Path(a.repo_root).resolve(); checks=[]; errors=[]; warnings=[]
    for name,path,needles in [('json_evidence_law',LAW,['Canonical evidence JSON','Expected negative fixtures','Quarantine evidence debt']),('json_evidence_matrix',MATRIX,['canonical_json_parse_clean','negative_fixtures_classified','quarantine_debt_visible']),('custodes_json_evidence_matrix',CUST,['prosecutor_not_helper','canonical_parse_error_hidden','quarantine_debt_hidden']),('throne_json_evidence_matrix',THRONE,['Canonical JSON evidence','Quarantine debt remains visible','JSON parse cleanliness cannot become global truth'])]:
        ok=contains(repo/path,needles); add(checks,f'{name}_exists_and_declares_boundaries',ok,{'path':path.as_posix()});
        if not ok: errors.append(f'{name} missing or incomplete')
    scanner_ok=(repo/SCANNER).is_file() and 'mechanicus_json_evidence_strict_lane_scanner.v0_1' in (repo/SCANNER).read_text(encoding='utf-8',errors='replace'); add(checks,'json_evidence_strict_scanner_installed',scanner_ok,{'path':SCANNER.as_posix()});
    if not scanner_ok: errors.append('JSON evidence strict scanner missing')
    dispatch_ok=(repo/DISPATCH).is_file() and 'mechanicus_language_validator_dispatch_baseline.v0_4_json_strict_lane_aware' in (repo/DISPATCH).read_text(encoding='utf-8',errors='replace'); add(checks,'language_dispatch_is_json_strict_lane_aware',dispatch_ok,{'path':DISPATCH.as_posix()});
    if not dispatch_ok: errors.append('language dispatch was not updated to JSON strict lane aware mode')
    strict={}
    if not errors:
        r=run(repo,SCANNER,['--repo-root',str(repo),'--out',STRICT.as_posix()]); strict,err=load(repo/STRICT) if (repo/STRICT).is_file() else ({},'missing'); ok=r['exit_code']==0 and err is None; add(checks,'json_strict_scanner_runs_and_writes_report',ok,{'run':r,'load_error':err,'verdict':strict.get('verdict') if isinstance(strict,dict) else None});
        if not ok: errors.append('JSON strict scanner did not produce pass report')
    if not errors:
        canonical=int(strict.get('canonical_parse_debt_count',-1))==0; add(checks,'canonical_json_parse_debt_is_zero',canonical,{'canonical_parse_debt_count':strict.get('canonical_parse_debt_count'),'canonical_parse_debt':strict.get('canonical_parse_debt',[])[:10]});
        if not canonical: errors.append('canonical JSON parse debt is not zero')
        visible=int(strict.get('parse_error_count',0))>=int(strict.get('expected_negative_fixture_count',0))+int(strict.get('quarantine_parse_debt_count',0)); add(checks,'noncanonical_parse_errors_are_classified_visible',visible,{'parse_error_count':strict.get('parse_error_count'),'expected_negative_fixture_count':strict.get('expected_negative_fixture_count'),'quarantine_parse_debt_count':strict.get('quarantine_parse_debt_count')});
        if not visible: errors.append('noncanonical parse errors were not classified visibly')
    dispatch_data={}
    if not errors:
        r=run(repo,DISPATCH,['--repo-root',str(repo),'--out',DISPATCH_R.as_posix()]); dispatch_data,err=load(repo/DISPATCH_R) if (repo/DISPATCH_R).is_file() else ({},'missing'); ok=r['exit_code']==0 and err is None; add(checks,'language_dispatch_runs_after_json_strict_lane',ok,{'run':r,'load_error':err});
        if not ok: errors.append('language dispatch did not run after JSON strict lane patch')
        else:
            jc=[c for c in dispatch_data.get('checks',[]) if c.get('lane_id')=='json_evidence']; jok=bool(jc) and all(bool(c.get('ok')) for c in jc); add(checks,'dispatch_json_evidence_lane_is_ok_after_classification',jok,{'json_checks':jc});
            if not jok: errors.append('dispatch still marks json_evidence lane as debt')
    readout={}
    if not errors:
        if not (repo/READOUT).is_file(): add(checks,'strict_language_lane_readout_tool_exists',False,{'path':READOUT.as_posix()}); errors.append('strict language lane readout tool missing')
        else:
            add(checks,'strict_language_lane_readout_tool_exists',True,{'path':READOUT.as_posix()}); r=run(repo,READOUT,['--repo-root',str(repo),'--out',READOUT_R.as_posix()],240); readout,err=load(repo/READOUT_R) if (repo/READOUT_R).is_file() else ({},'missing'); ok=r['exit_code']==0 and err is None; add(checks,'strict_language_lane_readout_runs_after_json_strict_lane',ok,{'run':r,'load_error':err});
            if not ok: errors.append('strict language lane readout did not run after JSON strict lane')
            else:
                lanes={l.get('lane_id'):l for l in readout.get('lanes',[]) if isinstance(l,dict)}; state=(lanes.get('json_evidence') or {}).get('state'); ok=state=='LANE_READY_BASELINE'; add(checks,'json_evidence_lane_state_is_ready_baseline',ok,{'json_state':state});
                if not ok: errors.append('json_evidence lane did not become LANE_READY_BASELINE')
    if isinstance(strict,dict):
        if strict.get('expected_negative_fixture_count'): warnings.append(f"Expected negative fixtures classified: {strict.get('expected_negative_fixture_count')}")
        if strict.get('quarantine_parse_debt_count'): warnings.append(f"Quarantine parse debt visible: {strict.get('quarantine_parse_debt_count')}")
        warnings += (strict.get('warnings',[]) or [])[:5]
    verdict='PASS_MECHANICUS_JSON_EVIDENCE_STRICT_LANE_READY' if not errors else 'FAIL_MECHANICUS_JSON_EVIDENCE_STRICT_LANE'; gen=utc()
    summary={'summary_id':'mechanicus.json_evidence_strict_lane_summary.v0_1','task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'generated_at_utc':gen,'checks':checks,'errors':errors,'warnings':warnings,'strict_report':STRICT.as_posix(),'dispatch_report':DISPATCH_R.as_posix(),'lane_readout':READOUT_R.as_posix(),'strict_counts':{'files_checked':strict.get('files_checked') if isinstance(strict,dict) else None,'parse_error_count':strict.get('parse_error_count') if isinstance(strict,dict) else None,'canonical_parse_debt_count':strict.get('canonical_parse_debt_count') if isinstance(strict,dict) else None,'expected_negative_fixture_count':strict.get('expected_negative_fixture_count') if isinstance(strict,dict) else None,'quarantine_parse_debt_count':strict.get('quarantine_parse_debt_count') if isinstance(strict,dict) else None},'meaning':'JSON evidence lane distinguishes canonical parse debt from expected malformed fixtures and quarantine debt.'}
    receipt={'receipt_id':'receipt.mechanicus.json_evidence_strict_lane.v0_1','task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'generated_at_utc':gen,'checks':checks,'errors':errors,'warnings':warnings,'strict_report':STRICT.as_posix(),'dispatch_report':DISPATCH_R.as_posix(),'lane_readout':READOUT_R.as_posix()}
    write(repo/SUMMARY,summary); write(repo/RECEIPT,receipt)
    cm='\n'.join(f"- `{c['status']}` — {c['name']}" for c in checks); em='\n'.join(f'- {e}' for e in errors) if errors else '- none'; wm='\n'.join(f'- {w}' for w in warnings) if warnings else '- none'
    (repo/REPORT).write_text(f"# MECHANICUS JSON EVIDENCE STRICT LANE VALIDATION REPORT V0.1\n\ntask_id: `{TASK_ID}`  \nvalidator_id: `{VALIDATOR_ID}`  \nverdict: `{verdict}`  \ngenerated_at_utc: `{gen}`\n\n## Meaning\n\nCanonical parse debt blocks the lane; expected fixtures and quarantine debt stay visible but nonblocking for canonical readiness.\n\n## Checks\n\n{cm}\n\n## Warnings\n\n{wm}\n\n## Errors\n\n{em}\n",encoding='utf-8')
    print(json.dumps({'task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'receipt':RECEIPT.as_posix(),'summary':SUMMARY.as_posix(),'strict_report':STRICT.as_posix(),'dispatch_report':DISPATCH_R.as_posix(),'lane_readout':READOUT_R.as_posix(),'errors':errors,'warnings':warnings},ensure_ascii=False,indent=2,default=str)); return 0 if verdict.startswith('PASS') else 1
if __name__=='__main__': raise SystemExit(main())
