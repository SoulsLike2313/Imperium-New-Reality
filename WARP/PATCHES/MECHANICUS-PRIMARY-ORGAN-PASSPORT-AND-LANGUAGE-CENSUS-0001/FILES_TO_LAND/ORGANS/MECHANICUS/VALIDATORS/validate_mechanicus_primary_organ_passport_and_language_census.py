#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, json, subprocess, sys
from pathlib import Path
TASK_ID='MECHANICUS-PRIMARY-ORGAN-PASSPORT-AND-LANGUAGE-CENSUS-0001'
VALIDATOR_ID='mechanicus_primary_organ_passport_and_language_census_validator.v0_1'
README=Path('ORGANS/MECHANICUS/README.md'); PASSPORT=Path('ORGANS/MECHANICUS/PASSPORT/MECHANICUS_ORGAN_PASSPORT_V0_1.json'); MACHINE_LAW=Path('ORGANS/MECHANICUS/LAWS/MECHANICUS_MACHINE_REALITY_LAW_V0_1.json'); LANGUAGE_LAW=Path('ORGANS/MECHANICUS/LAWS/MECHANICUS_LANGUAGE_CENSUS_AND_CODE_PURITY_LAW_V0_1.json'); ROLE_MATRIX=Path('ORGANS/MECHANICUS/MATRICES/MECHANICUS_LANGUAGE_ROLE_TAXONOMY_MATRIX_V0_1.json'); PURITY_MATRIX=Path('ORGANS/MECHANICUS/MATRICES/MECHANICUS_CODE_PURITY_GATE_MATRIX_V0_1.json'); VALIDATOR_STACK=Path('ORGANS/MECHANICUS/MATRICES/MECHANICUS_LANGUAGE_VALIDATOR_STACK_MATRIX_V0_1.json'); CUSTODES=Path('ORGANS/CUSTODES/MATRICES/CUSTODES_MECHANICUS_LANGUAGE_CENSUS_PROSECUTOR_MATRIX_V0_1.json'); THRONE=Path('ORGANS/THRONE/MATRICES/THRONE_MECHANICUS_MACHINE_REALITY_CROWN_GATE_MATRIX_V0_1.json'); TOOL=Path('ORGANS/MECHANICUS/TOOLS/measure_language_surface.py'); CENSUS_REPORT=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_LANGUAGE_SURFACE_CENSUS_V0_1.json')
RECEIPT=Path('ORGANS/MECHANICUS/RECEIPTS/mechanicus_primary_organ_passport_and_language_census_receipt.json'); SUMMARY=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_PRIMARY_ORGAN_PASSPORT_AND_LANGUAGE_CENSUS_SUMMARY_V0_1.json'); REPORT=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_PRIMARY_ORGAN_PASSPORT_AND_LANGUAGE_CENSUS_REPORT_V0_1.md')
def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def load_json(path):
    try: return json.loads(path.read_text(encoding='utf-8-sig')), None
    except Exception as e: return None, str(e)
def write_json(path,data): path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def add(checks,name,ok,details=None): checks.append({'name':name,'status':'PASS' if ok else 'FAIL','details':details or {}})
def txt(o): return json.dumps(o, ensure_ascii=False) if isinstance(o,(dict,list)) else str(o)
def has_all(t,needles): return all(n in t for n in needles)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('--apply',action='store_true'); args=ap.parse_args(); repo=Path(args.repo_root).resolve(); checks=[]; errors=[]; warnings=[]
    readme_ok=(repo/README).is_file() and has_all((repo/README).read_text(encoding='utf-8',errors='replace'), ['Mechanicus is the organ of machine reality','Form may change','Function must not be lost']); add(checks,'mechanicus_readme_exists_and_declares_machine_reality',readme_ok,{'path':README.as_posix()});
    if not readme_ok: errors.append('Mechanicus README missing or incomplete')
    passport,err=load_json(repo/PASSPORT) if (repo/PASSPORT).is_file() else ({},'missing'); ptxt=txt(passport); pok=err is None and passport.get('organ_id')=='MECHANICUS' and has_all(ptxt,['toolchain proof authority','language power registry owner','build/runtime proof owner','Code cleanliness target is 100%','Form may change; function must not be lost']); add(checks,'mechanicus_passport_exists_and_declares_scope',pok,{'path':PASSPORT.as_posix(),'error':err});
    if not pok: errors.append('Mechanicus passport missing or incomplete')
    ml,err=load_json(repo/MACHINE_LAW) if (repo/MACHINE_LAW).is_file() else ({},'missing'); mok=err is None and has_all(txt(ml), ['Machine reality is what can be built','A toolchain is not available because an LLM names it','Form may change; function must not be lost']); add(checks,'machine_reality_law_exists',mok,{'path':MACHINE_LAW.as_posix(),'error':err});
    if not mok: errors.append('Machine reality law missing or incomplete')
    ll,err=load_json(repo/LANGUAGE_LAW) if (repo/LANGUAGE_LAW).is_file() else ({},'missing'); lok=err is None and has_all(txt(ll), ['Every language used by the repo must be counted','Every counted language must have a role description','100% cleanliness','A build pass does not prove clean code']); add(checks,'language_census_and_code_purity_law_exists',lok,{'path':LANGUAGE_LAW.as_posix(),'error':err});
    if not lok: errors.append('Language census/code purity law missing or incomplete')
    rm,err=load_json(repo/ROLE_MATRIX) if (repo/ROLE_MATRIX).is_file() else ({},'missing'); langs={x.get('language') for x in rm.get('languages',[]) if isinstance(x,dict)} if isinstance(rm,dict) else set(); req={'Python','PowerShell','Rust','TypeScript/JavaScript','CSS','JSON','Markdown','Go','C++'}; rok=err is None and req.issubset(langs); add(checks,'language_role_taxonomy_matrix_exists_and_covers_core_languages',rok,{'path':ROLE_MATRIX.as_posix(),'error':err,'missing':sorted(req-langs)}); 
    if not rok: errors.append('Language role taxonomy matrix missing core languages')
    pm,err=load_json(repo/PURITY_MATRIX) if (repo/PURITY_MATRIX).is_file() else ({},'missing'); weight=sum(int(d.get('weight',0)) for d in pm.get('dimensions',[]) if isinstance(d,dict)) if isinstance(pm,dict) else 0; puok=err is None and pm.get('target')=='100_PERCENT_CODE_CLEANLINESS' and weight==100; add(checks,'code_purity_gate_matrix_exists_and_weights_100',puok,{'path':PURITY_MATRIX.as_posix(),'error':err,'weight_sum':weight});
    if not puok: errors.append('Code purity gate matrix missing or weights != 100')
    st,err=load_json(repo/VALIDATOR_STACK) if (repo/VALIDATOR_STACK).is_file() else ({},'missing'); sok=err is None and has_all(txt(st), ['toolchain','syntax','format','lint','build','test','security','architecture','receipt']); add(checks,'language_validator_stack_matrix_exists',sok,{'path':VALIDATOR_STACK.as_posix(),'error':err});
    if not sok: errors.append('Language validator stack matrix missing or incomplete')
    cu,err=load_json(repo/CUSTODES) if (repo/CUSTODES).is_file() else ({},'missing'); cuok=err is None and has_all(txt(cu), ['prosecutor_not_helper','language_surface_not_counted','partial_lint_claimed_as_100_clean','build_proof_claimed_as_code_purity']); add(checks,'custodes_mechanicus_language_census_prosecutor_matrix_exists',cuok,{'path':CUSTODES.as_posix(),'error':err});
    if not cuok: errors.append('Custodes matrix missing or weak')
    th,err=load_json(repo/THRONE) if (repo/THRONE).is_file() else ({},'missing'); thok=err is None and has_all(txt(th), ['No local toolchain proof may become global language readiness','No code purity claim may become Crown truth without full evidence','No UI/backend/game shell may own functional truth']); add(checks,'throne_mechanicus_machine_reality_crown_gate_matrix_exists',thok,{'path':THRONE.as_posix(),'error':err});
    if not thok: errors.append('Throne matrix missing or weak')
    tool_exists=(repo/TOOL).is_file(); add(checks,'language_surface_census_tool_exists',tool_exists,{'path':TOOL.as_posix()});
    if not tool_exists: errors.append('Language census tool missing')
    census_ok=False; census={}
    if tool_exists and not errors:
        p=subprocess.run([sys.executable, str(repo/TOOL), '--repo-root', str(repo), '--out', CENSUS_REPORT.as_posix()], cwd=str(repo), capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
        if p.returncode!=0: warnings.append('Language census tool returned non-zero exit code'); warnings.append(p.stderr[-1000:])
        if (repo/CENSUS_REPORT).is_file():
            census,cerr=load_json(repo/CENSUS_REPORT); census_ok=cerr is None and census.get('language_count',0)>0 and census.get('total_counted_lines',0)>0
    add(checks,'language_surface_census_tool_runs_and_writes_report',census_ok,{'path':CENSUS_REPORT.as_posix(),'language_count':census.get('language_count') if isinstance(census,dict) else None,'total_counted_lines':census.get('total_counted_lines') if isinstance(census,dict) else None})
    if not census_ok: errors.append('Language census tool did not produce valid report')
    verdict='PASS_MECHANICUS_PRIMARY_ORGAN_PASSPORT_AND_LANGUAGE_CENSUS_READY' if not errors else 'FAIL_MECHANICUS_PRIMARY_ORGAN_PASSPORT_AND_LANGUAGE_CENSUS'; gen=utc(); top=[]
    if isinstance(census,dict): top=[{'language':x.get('language'),'files':x.get('files'),'total_lines':x.get('total_lines'),'code_lines':x.get('code_lines'),'roles':x.get('roles')} for x in census.get('languages',[])[:12]]
    summary={'summary_id':'mechanicus.primary_organ_passport_and_language_census_summary.v0_1','task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'generated_at_utc':gen,'checks':checks,'errors':errors,'warnings':warnings,'census_report':CENSUS_REPORT.as_posix(),'top_languages':top,'meaning':'Establishes Mechanicus as primary machine reality organ and measures the repository language surface.'}; receipt={**summary,'receipt_id':'receipt.mechanicus.primary_organ_passport_and_language_census.v0_1','readme':README.as_posix(),'passport':PASSPORT.as_posix(),'machine_law':MACHINE_LAW.as_posix(),'language_law':LANGUAGE_LAW.as_posix(),'role_matrix':ROLE_MATRIX.as_posix(),'purity_matrix':PURITY_MATRIX.as_posix(),'validator_stack':VALIDATOR_STACK.as_posix(),'census_tool':TOOL.as_posix()}; write_json(repo/SUMMARY,summary); write_json(repo/RECEIPT,receipt)
    checks_md='\n'.join(f"- `{c['status']}` — {c['name']}" for c in checks); errors_md='\n'.join(f'- {e}' for e in errors) if errors else '- none'; warnings_md='\n'.join(f'- {w}' for w in warnings) if warnings else '- none'; langs_md='\n'.join(f"- `{x['language']}` — files: `{x['files']}`, total lines: `{x['total_lines']}`, code lines: `{x['code_lines']}`" for x in top) if top else '- none'
    (repo/REPORT).write_text(f'# MECHANICUS PRIMARY ORGAN PASSPORT AND LANGUAGE CENSUS REPORT V0.1\n\ntask_id: `{TASK_ID}`  \nvalidator_id: `{VALIDATOR_ID}`  \nverdict: `{verdict}`  \ngenerated_at_utc: `{gen}`\n\n## Meaning\n\nMechanicus begins as the primary organ of machine reality. This patch establishes identity, laws, language role taxonomy, code purity target and a first language surface census.\n\n## Code purity law\n\n```text\n100% cleanliness is the target.\nA build pass does not prove clean code.\nMissing language validators are debt, not pass.\n```\n\n## Top counted languages\n\n{langs_md}\n\n## Checks\n\n{checks_md}\n\n## Warnings\n\n{warnings_md}\n\n## Errors\n\n{errors_md}\n', encoding='utf-8')
    print(json.dumps({'task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'receipt':RECEIPT.as_posix(),'summary':SUMMARY.as_posix(),'census_report':CENSUS_REPORT.as_posix(),'errors':errors,'warnings':warnings}, ensure_ascii=False, indent=2)); return 0 if verdict.startswith('PASS') else 1
if __name__=='__main__': raise SystemExit(main())
