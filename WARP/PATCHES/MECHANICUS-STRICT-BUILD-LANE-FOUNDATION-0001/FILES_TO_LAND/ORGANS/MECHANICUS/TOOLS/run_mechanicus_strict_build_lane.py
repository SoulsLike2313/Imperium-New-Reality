#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, json, os, py_compile, shutil, subprocess
from pathlib import Path
TOOL_ID='mechanicus_strict_build_lane_foundation_runner.v0_1'
DEFAULT_OUT='ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_BUILD_LANE_REPORT_V0_1.json'
EXCLUDE={'.git','node_modules','target','dist','build','__pycache__','.venv','venv','.mypy_cache','.ruff_cache','.pytest_cache','.next','.turbo'}
def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def wr(path,data):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf-8')
def cand(p,repo):
    try: rel=p.relative_to(repo)
    except Exception: return False
    if set(rel.parts)&EXCLUDE: return False
    s=rel.as_posix()
    return not (s.startswith('WARP/PATCHES/') or '/FILES_TO_LAND/' in s)
def which(x): return shutil.which(x) or shutil.which(x+'.cmd') or shutil.which(x+'.exe')
def run(cmd,cwd,timeout=900):
    started=utc()
    try:
        p=subprocess.run(cmd,cwd=str(cwd),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
        return {'started_at_utc':started,'finished_at_utc':utc(),'cmd':cmd,'cwd':str(cwd),'exit_code':p.returncode,'ok':p.returncode==0,'stdout_tail':p.stdout[-12000:],'stderr_tail':p.stderr[-12000:]}
    except subprocess.TimeoutExpired as e:
        return {'started_at_utc':started,'finished_at_utc':utc(),'cmd':cmd,'cwd':str(cwd),'exit_code':None,'ok':False,'timeout':True,'error':f'timeout after {timeout}s','stdout_tail':(e.stdout or '')[-12000:] if isinstance(e.stdout,str) else '', 'stderr_tail':(e.stderr or '')[-12000:] if isinstance(e.stderr,str) else ''}
    except Exception as e:
        return {'started_at_utc':started,'finished_at_utc':utc(),'cmd':cmd,'cwd':str(cwd),'exit_code':None,'ok':False,'error':repr(e),'stdout_tail':'','stderr_tail':''}
def py_lane(repo):
    errs=[]; n=0
    for p in sorted(repo.rglob('*.py')):
        if not cand(p,repo): continue
        n+=1
        try: py_compile.compile(str(p),doraise=True)
        except Exception as e: errs.append({'path':p.relative_to(repo).as_posix(),'error':str(e)})
    return {'target_id':'python_compile_current_non_patch','lane':'python_compile','detected':n>0,'files_checked':n,'ok':not errs,'errors':errs[:80],'not_claimed':['ruff','mypy','pytest','import runtime']}
def pwsh_lane(repo):
    exe=which('pwsh')
    if not exe: return {'target_id':'powershell_host_probe','lane':'powershell_host_probe','detected':True,'ok':False,'errors':[{'error':'pwsh not found'}]}
    res=run([exe,'-NoLogo','-NoProfile','-Command','$PSVersionTable.PSVersion.ToString()'],repo,90)
    return {'target_id':'powershell_host_probe','lane':'powershell_host_probe','detected':True,'ok':bool(res.get('ok')),'toolchain':{'pwsh':exe},'command_result':res,'errors':[] if res.get('ok') else [{'error':'pwsh version probe failed'}], 'not_claimed':['PSScriptAnalyzer','all runners valid']}
def npm_lane(repo):
    app=repo/'SUPPORT'/'APP_TAURI'; pkg=app/'package.json'
    if not pkg.is_file(): return {'target_id':'support_app_tauri_npm_build','lane':'tauri_frontend_npm_build','detected':False,'ok':True,'debt':'NO_PACKAGE_JSON_PRESENT'}
    npm=which('npm')
    if not npm: return {'target_id':'support_app_tauri_npm_build','lane':'tauri_frontend_npm_build','detected':True,'ok':False,'errors':[{'error':'npm not found'}]}
    cmd=['cmd.exe','/d','/s','/c','npm run build'] if os.name=='nt' else [npm,'run','build']
    res=run(cmd,app,900)
    return {'target_id':'support_app_tauri_npm_build','lane':'tauri_frontend_npm_build','detected':True,'ok':bool(res.get('ok')),'toolchain':{'npm':npm,'node':which('node')},'dependency_state':'node_modules_present' if (app/'node_modules').exists() else 'node_modules_missing_no_install_attempted','command_result':res,'errors':[] if res.get('ok') else [{'error':'npm run build failed','exit_code':res.get('exit_code')}], 'not_claimed':['npm test','npm audit','eslint','runtime proof']}
def cargo_lane(repo):
    manifest=repo/'SUPPORT'/'APP_TAURI'/'src-tauri'/'Cargo.toml'
    if not manifest.is_file(): return {'target_id':'support_app_tauri_cargo_check','lane':'tauri_rust_cargo_check','detected':False,'ok':True,'debt':'NO_CARGO_MANIFEST_PRESENT'}
    cargo=which('cargo'); rustc=which('rustc')
    if not cargo or not rustc: return {'target_id':'support_app_tauri_cargo_check','lane':'tauri_rust_cargo_check','detected':True,'ok':False,'errors':[{'error':'cargo/rustc not found'}]}
    res=run([cargo,'check','--manifest-path',str(manifest)],repo,1200)
    return {'target_id':'support_app_tauri_cargo_check','lane':'tauri_rust_cargo_check','detected':True,'ok':bool(res.get('ok')),'toolchain':{'cargo':cargo,'rustc':rustc},'manifest':manifest.relative_to(repo).as_posix(),'command_result':res,'errors':[] if res.get('ok') else [{'error':'cargo check failed','exit_code':res.get('exit_code')}], 'not_claimed':['cargo fmt','cargo clippy','cargo test','runtime proof']}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('--out',default=DEFAULT_OUT); args=ap.parse_args(); repo=Path(args.repo_root).resolve()
    targets=[py_lane(repo),pwsh_lane(repo),npm_lane(repo),cargo_lane(repo)]
    fails=[{'target_id':t['target_id'],'lane':t['lane'],'errors':t.get('errors',[]),'command_result':t.get('command_result',{})} for t in targets if t.get('detected') and not t.get('ok')]
    debt=[{'target_id':t['target_id'],'lane':t['lane'],'debt':t.get('debt','TARGET_NOT_PRESENT')} for t in targets if not t.get('detected')]
    rep={'tool_id':TOOL_ID,'generated_at_utc':utc(),'repo_root':str(repo),'targets':targets,'target_count':len(targets),'blocking_failure_count':len(fails),'foundation_debt_count':len(debt),'blocking_failures':fails,'foundation_debt':debt,'verdict':'PASS_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION' if not fails else 'FAIL_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION','not_claimed':['tests passed','linters passed','security audit clean','runtime FPS proof','UI reference fidelity'],'warnings':['Strict build lane foundation does not install dependencies.','Build proof is separate from code cleanliness and runtime proof.']}
    wr(repo/args.out,rep); print(json.dumps(rep,ensure_ascii=False,indent=2,default=str)); return 0 if not fails else 1
if __name__=='__main__': raise SystemExit(main())
