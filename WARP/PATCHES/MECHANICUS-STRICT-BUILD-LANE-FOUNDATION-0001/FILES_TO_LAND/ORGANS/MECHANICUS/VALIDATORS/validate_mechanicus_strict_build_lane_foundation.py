#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, json, subprocess, sys
from pathlib import Path
TASK_ID='MECHANICUS-STRICT-BUILD-LANE-FOUNDATION-0001'; VALIDATOR_ID='mechanicus_strict_build_lane_foundation_validator.v0_1'
RUNNER=Path('ORGANS/MECHANICUS/TOOLS/run_mechanicus_strict_build_lane.py'); PLANNER=Path('ORGANS/MECHANICUS/TOOLS/plan_mechanicus_task_tool_composition.py')
BUILD=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_BUILD_LANE_REPORT_V0_1.json'); PLAN=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_TASK_TOOL_COMPOSITION_PLAN_V0_1.json')
RECEIPT=Path('ORGANS/MECHANICUS/RECEIPTS/mechanicus_strict_build_lane_foundation_receipt.json'); SUMMARY=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_BUILD_LANE_FOUNDATION_SUMMARY_V0_1.json'); REPORT=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_BUILD_LANE_FOUNDATION_VALIDATION_REPORT_V0_1.md')
def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def load(p):
    try: return json.loads(p.read_text(encoding='utf-8-sig')),None
    except Exception as e: return None,str(e)
def write(p,d): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf-8')
def add(ch,name,ok,details=None): ch.append({'name':name,'status':'PASS' if ok else 'FAIL','details':details or {}})
def run(repo,script,args,timeout=1500):
    p=subprocess.run([sys.executable,str(repo/script)]+args,cwd=str(repo),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
    return {'exit_code':p.returncode,'stdout_tail':p.stdout[-7000:],'stderr_tail':p.stderr[-5000:]}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('--apply',action='store_true'); a=ap.parse_args(); repo=Path(a.repo_root).resolve(); checks=[]; errors=[]; warnings=[]
    for rel,mark in [('ORGANS/MECHANICUS/LAWS/MECHANICUS_STRICT_BUILD_LANE_FOUNDATION_LAW_V0_1.json','Build proof is not code cleanliness'),('ORGANS/MECHANICUS/MATRICES/MECHANICUS_STRICT_BUILD_LANE_FOUNDATION_MATRIX_V0_1.json','BUILD_COMMAND_FAILED'),('ORGANS/CUSTODES/MATRICES/CUSTODES_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION_PROSECUTOR_MATRIX_V0_1.json','prosecutor_not_helper'),('ORGANS/THRONE/MATRICES/THRONE_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION_CROWN_GATE_MATRIX_V0_1.json','claim runtime proof from build pass')]:
        p=repo/rel; ok=p.is_file() and mark in p.read_text(encoding='utf-8',errors='replace'); add(checks,Path(rel).stem+'_exists',ok,{'path':rel});
        if not ok: errors.append(rel+' missing or incomplete')
    runner_ok=(repo/RUNNER).is_file() and 'mechanicus_strict_build_lane_foundation_runner.v0_1' in (repo/RUNNER).read_text(encoding='utf-8',errors='replace')
    add(checks,'strict_build_lane_runner_installed',runner_ok,{'path':RUNNER.as_posix()});
    if not runner_ok: errors.append('strict build lane runner missing')
    planner_ok=(repo/PLANNER).is_file() and 'mechanicus_task_tool_composition_planner.v0_4_strict_build_lane_aware' in (repo/PLANNER).read_text(encoding='utf-8',errors='replace')
    add(checks,'planner_is_strict_build_lane_aware',planner_ok,{'path':PLANNER.as_posix()});
    if not planner_ok: errors.append('planner not updated')
    build={}
    if not errors:
        rr=run(repo,RUNNER,['--repo-root',str(repo),'--out',BUILD.as_posix()]); build,be=load(repo/BUILD) if (repo/BUILD).is_file() else ({},'missing')
        ok=rr['exit_code']==0 and be is None and build.get('verdict')=='PASS_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION'
        add(checks,'strict_build_lane_runner_runs_and_passes_discovered_targets',ok,{'run':rr,'load_error':be,'verdict':build.get('verdict') if isinstance(build,dict) else None,'blocking_failure_count':build.get('blocking_failure_count') if isinstance(build,dict) else None})
        if not ok: errors.append('strict build lane runner did not pass discovered targets')
    if not errors and isinstance(build,dict):
        targets={t.get('target_id'):t for t in build.get('targets',[]) if isinstance(t,dict)}
        for tid in ['python_compile_current_non_patch','powershell_host_probe']:
            ok=tid in targets and targets[tid].get('ok'); add(checks,tid+'_passes',ok,{'target':targets.get(tid)});
            if not ok: errors.append(tid+' did not pass')
        for tid in ['support_app_tauri_npm_build','support_app_tauri_cargo_check']:
            if tid in targets and targets[tid].get('detected'):
                ok=targets[tid].get('ok'); add(checks,tid+'_detected_and_passes',ok,{'target_summary':{k:targets[tid].get(k) for k in ['target_id','lane','detected','ok','dependency_state','errors']}});
                if not ok: errors.append(tid+' detected but failed')
            else: add(checks,tid+'_not_present_is_nonblocking_foundation_debt',True,{'target':targets.get(tid)})
    plan={}
    if not errors:
        sample='Register a Patch Pack for Tauri UI cockpit polish with CSS ornament animation, runtime FPS proof, JSON receipts, PowerShell WARP runner, and possible future game engine projection.'
        pr=run(repo,PLANNER,['--repo-root',str(repo),'--task-text',sample,'--out',PLAN.as_posix()],timeout=300); plan,pe=load(repo/PLAN) if (repo/PLAN).is_file() else ({},'missing')
        ok=pr['exit_code']==0 and pe is None and plan.get('strict_build_report')==BUILD.as_posix(); add(checks,'planner_runs_with_strict_build_report_awareness',ok,{'run':pr,'load_error':pe,'strict_build_report':plan.get('strict_build_report') if isinstance(plan,dict) else None});
        if not ok: errors.append('planner did not use strict build report')
        missing=[m.get('capability_id') for m in plan.get('missing_capabilities',[])] if isinstance(plan,dict) else []
        ok='STRICT_BUILD_LANE_REQUIRED' not in missing; add(checks,'planner_no_longer_reports_strict_build_lane_required_gap_after_pass',ok,{'missing_capabilities':missing});
        if not ok: errors.append('planner still reports STRICT_BUILD_LANE_REQUIRED')
    if isinstance(build,dict):
        warnings += build.get('warnings',[])[:6]
        for f in build.get('foundation_debt',[]): warnings.append(f"Foundation debt: {f.get('target_id')} => {f.get('debt')}")
    if isinstance(plan,dict):
        rec=plan.get('recommended_tool_stack')
        if isinstance(rec,dict): warnings.append(f"Planner recommended demand after build lane: {rec.get('demand_id')} score={rec.get('score_0_to_100')} verdict={rec.get('verdict')}")
        for m in plan.get('missing_capabilities',[])[:6]: warnings.append(f"Remaining planner gap: {m.get('capability_id')} => {m.get('severity')}")
    verdict='PASS_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION_READY' if not errors else 'FAIL_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION'; gen=utc()
    summary={'summary_id':'mechanicus.strict_build_lane_foundation_summary.v0_1','task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'generated_at_utc':gen,'checks':checks,'errors':errors,'warnings':warnings,'build_report':BUILD.as_posix(),'plan':PLAN.as_posix()}
    receipt={'receipt_id':'receipt.mechanicus.strict_build_lane_foundation.v0_1','task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'generated_at_utc':gen,'checks':checks,'errors':errors,'warnings':warnings,'build_report':BUILD.as_posix(),'plan':PLAN.as_posix()}
    write(repo/SUMMARY,summary); write(repo/RECEIPT,receipt); (repo/REPORT).parent.mkdir(parents=True,exist_ok=True); (repo/REPORT).write_text('# MECHANICUS STRICT BUILD LANE FOUNDATION VALIDATION REPORT V0.1\n\nverdict: `'+verdict+'`\n',encoding='utf-8')
    print(json.dumps({'task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'receipt':RECEIPT.as_posix(),'summary':SUMMARY.as_posix(),'build_report':BUILD.as_posix(),'plan':PLAN.as_posix(),'errors':errors,'warnings':warnings},ensure_ascii=False,indent=2,default=str)); return 0 if verdict.startswith('PASS') else 1
if __name__=='__main__': raise SystemExit(main())
