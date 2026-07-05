#!/usr/bin/env python3
from __future__ import annotations
import argparse,datetime as dt,json,subprocess,sys
from pathlib import Path
TASK_ID='MECHANICUS-LANGUAGE-SURFACE-V2-TOOLCHAIN-VALIDATOR-DISPATCH-0001'
VALIDATOR_ID='mechanicus_language_surface_v2_toolchain_validator_dispatch_validator.v0_1'
SURFACE_MATRIX=Path('ORGANS/MECHANICUS/MATRICES/MECHANICUS_LANGUAGE_SURFACE_V2_CLASSIFICATION_MATRIX_V0_1.json')
TOOLCHAIN_MATRIX=Path('ORGANS/MECHANICUS/MATRICES/MECHANICUS_TOOLCHAIN_PROOF_AND_LANGUAGE_VALIDATOR_DISPATCH_MATRIX_V0_1.json')
CUSTODES=Path('ORGANS/CUSTODES/MATRICES/CUSTODES_MECHANICUS_TOOLCHAIN_AND_LANGUAGE_VALIDATOR_DISPATCH_PROSECUTOR_MATRIX_V0_1.json')
THRONE=Path('ORGANS/THRONE/MATRICES/THRONE_MECHANICUS_TOOLCHAIN_LANGUAGE_VALIDATION_CROWN_GATE_MATRIX_V0_1.json')
SURFACE_TOOL=Path('ORGANS/MECHANICUS/TOOLS/measure_language_surface_v2.py'); PROBE_TOOL=Path('ORGANS/MECHANICUS/TOOLS/prove_toolchains.py'); DISPATCH_TOOL=Path('ORGANS/MECHANICUS/TOOLS/run_language_validation_dispatch.py')
SURFACE_REPORT=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_LANGUAGE_SURFACE_V2_REPORT_V0_1.json'); TOOLCHAIN_REPORT=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOLCHAIN_PROOF_REPORT_V0_1.json'); DISPATCH_REPORT=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_LANGUAGE_VALIDATION_BASELINE_V0_1.json')
RECEIPT=Path('ORGANS/MECHANICUS/RECEIPTS/mechanicus_language_surface_v2_toolchain_validator_dispatch_receipt.json'); SUMMARY=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_VALIDATOR_DISPATCH_SUMMARY_V0_1.json'); REPORT=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_VALIDATOR_DISPATCH_REPORT_V0_1.md')
def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def load(p):
    try:return json.loads(p.read_text(encoding='utf-8-sig')),None
    except Exception as e:return {},str(e)
def writej(p,d): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def add(ch,n,ok,det=None): ch.append({'name':n,'status':'PASS' if ok else 'FAIL','details':det or {}})
def has(text,needles): return all(n in text for n in needles)
def run(repo,tool,out,timeout=300):
    p=subprocess.run([sys.executable,str(repo/tool),'--repo-root',str(repo),'--out',out.as_posix()],cwd=str(repo),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
    return {'exit_code':p.returncode,'stdout_tail':p.stdout[-2500:],'stderr_tail':p.stderr[-2500:],'out_exists':(repo/out).is_file()}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('--apply',action='store_true'); a=ap.parse_args(); repo=Path(a.repo_root).resolve(); checks=[]; errors=[]; warnings=[]
    for name,path,needles in [('surface_matrix',SURFACE_MATRIX,['Raw total is not source-code total','source_runtime','governance_evidence']),('toolchain_matrix',TOOLCHAIN_MATRIX,['PASS_100_CLEAN is forbidden','Tool unavailable is validation debt','A build pass does not prove code purity']),('custodes_matrix',CUSTODES,['baseline_validation_claimed_as_100_clean','tool_unavailable_reported_as_pass']),('throne_matrix',THRONE,['No automatic audit fix','Baseline validation may create a measured debt map'])]:
        data,err=load(repo/path) if (repo/path).is_file() else ({},'missing'); ok=err is None and has(json.dumps(data,ensure_ascii=False),needles); add(checks,name+'_exists_and_has_laws',ok,{'path':path.as_posix(),'error':err})
        if not ok: errors.append(name+' missing/incomplete')
    for name,path in [('surface_tool',SURFACE_TOOL),('probe_tool',PROBE_TOOL),('dispatch_tool',DISPATCH_TOOL)]:
        ok=(repo/path).is_file(); add(checks,name+'_exists',ok,{'path':path.as_posix()});
        if not ok: errors.append(name+' missing')
    surface={}; toolchain={}; dispatch={}
    if not errors:
        r=run(repo,SURFACE_TOOL,SURFACE_REPORT); add(checks,'language_surface_v2_tool_runs',r['exit_code']==0 and r['out_exists'],r)
        if r['exit_code'] or not r['out_exists']: errors.append('surface v2 tool failed')
        else:
            surface,_=load(repo/SURFACE_REPORT); classes=set((surface.get('classes') or {}).keys()); ok='source_runtime' in classes and 'governance_evidence' in classes; add(checks,'surface_v2_splits_source_from_evidence',ok,{'classes':sorted(classes)})
            if not ok: errors.append('surface/evidence split missing')
    if not errors:
        r=run(repo,PROBE_TOOL,TOOLCHAIN_REPORT); add(checks,'toolchain_probe_runs',r['exit_code']==0 and r['out_exists'],r)
        if r['exit_code'] or not r['out_exists']: errors.append('toolchain probe failed required tools')
        else:
            toolchain,_=load(repo/TOOLCHAIN_REPORT)
            if toolchain.get('optional_missing_or_failed'): warnings.append('Optional toolchains/builds missing or failed; recorded as debt, not 100% clean failure.')
    if not errors:
        r=run(repo,DISPATCH_TOOL,DISPATCH_REPORT); add(checks,'language_validation_dispatch_runs',r['exit_code']==0 and r['out_exists'],r)
        if r['exit_code'] or not r['out_exists']: errors.append('validation dispatch failed')
        else:
            dispatch,_=load(repo/DISPATCH_REPORT); ok=dispatch.get('verdict')!='PASS_100_CLEAN' and '100% code cleanliness' in json.dumps(dispatch,ensure_ascii=False); add(checks,'dispatch_does_not_claim_100_clean',ok,{'dispatch_verdict':dispatch.get('verdict')})
            if not ok: errors.append('fake 100 clean risk')
            if dispatch.get('validation_debt'): warnings.append('Validation baseline contains debt; expected for first baseline.')
    verdict='PASS_MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_VALIDATOR_DISPATCH_READY' if not errors else 'FAIL_MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_VALIDATOR_DISPATCH'; gen=utc()
    summary={'summary_id':'mechanicus.language_surface_v2_toolchain_validator_dispatch_summary.v0_1','task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'generated_at_utc':gen,'checks':checks,'errors':errors,'warnings':warnings,'surface_report':SURFACE_REPORT.as_posix(),'toolchain_report':TOOLCHAIN_REPORT.as_posix(),'dispatch_report':DISPATCH_REPORT.as_posix()}
    receipt={'receipt_id':'receipt.mechanicus.language_surface_v2_toolchain_validator_dispatch.v0_1',**summary}
    writej(repo/SUMMARY,summary); writej(repo/RECEIPT,receipt)
    source=[]
    if isinstance(surface,dict):
        for x in surface.get('classes',{}).get('source_runtime',{}).get('languages',[])[:10]: source.append(f"- `{x.get('language')}` — files: `{x.get('files')}`, total: `{x.get('total_lines')}`, code: `{x.get('code_lines')}`")
    checks_md='\n'.join(f"- `{c['status']}` — {c['name']}" for c in checks); warnings_md='\n'.join(f'- {w}' for w in warnings) if warnings else '- none'; errors_md='\n'.join(f'- {e}' for e in errors) if errors else '- none'; source_md='\n'.join(source) if source else '- none'
    (repo/REPORT).write_text(f"""# MECHANICUS LANGUAGE SURFACE V2 TOOLCHAIN VALIDATOR DISPATCH REPORT V0.1\n\ntask_id: `{TASK_ID}`  \nvalidator_id: `{VALIDATOR_ID}`  \nverdict: `{verdict}`  \ngenerated_at_utc: `{gen}`\n\n## Meaning\n\nMechanicus separates raw language mass from source-runtime code and governance evidence. It also establishes first toolchain and baseline language validation dispatch.\n\n## Source-runtime language surface preview\n\n{source_md}\n\n## Boundary\n\n```text\nThis is not a 100% clean verdict.\nThis is baseline measurement and validation-debt discovery.\n```\n\n## Checks\n\n{checks_md}\n\n## Warnings\n\n{warnings_md}\n\n## Errors\n\n{errors_md}\n""",encoding='utf-8')
    print(json.dumps({'task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'receipt':RECEIPT.as_posix(),'summary':SUMMARY.as_posix(),'surface_report':SURFACE_REPORT.as_posix(),'toolchain_report':TOOLCHAIN_REPORT.as_posix(),'dispatch_report':DISPATCH_REPORT.as_posix(),'errors':errors,'warnings':warnings},ensure_ascii=False,indent=2)); return 0 if verdict.startswith('PASS') else 1
if __name__=='__main__': raise SystemExit(main())
