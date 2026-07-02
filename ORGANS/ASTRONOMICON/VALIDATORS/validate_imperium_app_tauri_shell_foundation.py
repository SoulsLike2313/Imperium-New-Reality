
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, datetime as dt, json, shutil, subprocess
from pathlib import Path
TASK_ID='IMPERIUM-APP-TAURI-SHELL-FOUNDATION-0001'; VALIDATOR_ID='imperium_app_tauri_shell_foundation_validator.v0_1'
MATRIX=Path('ORGANS/ASTRONOMICON/MATRICES/IMPERIUM_APP_TAURI_SHELL_FOUNDATION_MATRIX_V0_1.json')
RECEIPT=Path('ORGANS/ASTRONOMICON/RECEIPTS/imperium_app_tauri_shell_foundation_receipt.json')
SUMMARY=Path('ORGANS/ASTRONOMICON/REPORTS/IMPERIUM_APP_TAURI_SHELL_FOUNDATION_SUMMARY_V0_1.json')
REPORT=Path('ORGANS/ASTRONOMICON/REPORTS/IMPERIUM_APP_TAURI_SHELL_FOUNDATION_REPORT_V0_1.md')
def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def load(p):
    try: return json.loads(p.read_text(encoding='utf-8-sig')), None
    except Exception as e: return None, str(e)
def write_json(p,d): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def add(ch,n,ok,details=None): ch.append({'name':n,'status':'PASS' if ok else 'FAIL','details':details or {}})
def ver(cmd,args):
    exe=shutil.which(cmd)
    if not exe: return {'exists':False}
    try:
        p=subprocess.run([cmd]+args,capture_output=True,text=True,timeout=20,encoding='utf-8',errors='replace')
        return {'exists':True,'path':exe,'exit_code':p.returncode,'version':(p.stdout or p.stderr).strip()[:240]}
    except Exception as e: return {'exists':True,'error':str(e)}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('--apply',action='store_true'); a=ap.parse_args(); repo=Path(a.repo_root).resolve()
    checks=[]; errors=[]; warnings=[]
    matrix,err=load(repo/MATRIX) if (repo/MATRIX).is_file() else ({},'missing')
    add(checks,'tauri_foundation_matrix_parses',err is None,{'error':err})
    if err: errors.append('matrix missing or invalid'); matrix={}
    miss=[rel for rel in matrix.get('required_files',[]) if not (repo/rel).is_file()]
    add(checks,'required_tauri_files_exist',not miss,{'missing':miss})
    if miss: errors.append('missing required files')
    bad=[]
    for rel in ['SUPPORT/APP_TAURI/package.json','SUPPORT/APP_TAURI/src-tauri/tauri.conf.json','SUPPORT/APP_TAURI/src-tauri/capabilities/default.json','SUPPORT/APP_TAURI/IMPERIUM_APP_TAURI_MANIFEST_V0_1.json','SUPPORT/APP_TAURI/contracts/IMPERIUM_TAURI_60FPS_PERFORMANCE_GATE_V0_1.json','SUPPORT/APP_TAURI/contracts/IMPERIUM_EYES_ROOM_CONTRACT_V0_1.json','SUPPORT/APP_TAURI/contracts/IMPERIUM_SEED_CORE_CONTRACT_DRAFT_V0_1.json']:
        _,e=load(repo/rel)
        if e: bad.append({'path':rel,'error':e})
    add(checks,'tauri_json_files_parse',not bad,{'bad_json':bad})
    if bad: errors.append('json parse failure')
    js=(repo/'SUPPORT/APP_TAURI/src/main.js').read_text(encoding='utf-8',errors='replace') if (repo/'SUPPORT/APP_TAURI/src/main.js').exists() else ''
    css=(repo/'SUPPORT/APP_TAURI/src/styles.css').read_text(encoding='utf-8',errors='replace') if (repo/'SUPPORT/APP_TAURI/src/styles.css').exists() else ''
    front=js+'\n'+css
    mf=[m for m in matrix.get('required_frontend_markers',[]) if m not in front]
    add(checks,'frontend_has_required_markers',not mf,{'missing':mf})
    if mf: errors.append('frontend missing markers')
    rust=(repo/'SUPPORT/APP_TAURI/src-tauri/src/main.rs').read_text(encoding='utf-8',errors='replace') if (repo/'SUPPORT/APP_TAURI/src-tauri/src/main.rs').exists() else ''
    mr=[m for m in matrix.get('required_rust_commands',[]) if m not in rust]
    add(checks,'rust_bridge_has_required_commands',not mr,{'missing':mr})
    if mr: errors.append('rust commands missing')
    hits=[p for p in ['git commit','git push'] if p in (front+'\n'+rust).lower()]
    add(checks,'tauri_shell_has_no_git_land',not hits,{'hits':hits})
    if hits: errors.append('forbidden git land marker')
    fps,_=load(repo/'SUPPORT/APP_TAURI/contracts/IMPERIUM_TAURI_60FPS_PERFORMANCE_GATE_V0_1.json')
    fps_ok=isinstance(fps,dict) and fps.get('target_fps')==60 and 'requestAnimationFrame' in js and 'reduceMotionMode' in js
    add(checks,'fps_gate_60_declared_and_frontend_watchdog_exists',fps_ok,{'target_fps':fps.get('target_fps') if isinstance(fps,dict) else None})
    if not fps_ok: errors.append('fps gate missing')
    eyes,_=load(repo/'SUPPORT/APP_TAURI/contracts/IMPERIUM_EYES_ROOM_CONTRACT_V0_1.json')
    eyes_ok=isinstance(eyes,dict) and 'v0.5.3.1' in eyes.get('target_baseline','') and 'EYES_ROOM' in js
    add(checks,'eyes_room_contract_declared',eyes_ok,{})
    if not eyes_ok: errors.append('eyes contract missing')
    seed,_=load(repo/'SUPPORT/APP_TAURI/contracts/IMPERIUM_SEED_CORE_CONTRACT_DRAFT_V0_1.json')
    seed_ok=isinstance(seed,dict) and 'Seed Core' in seed.get('meaning','') and 'SEED_CORE' in js
    add(checks,'seed_core_contract_declared',seed_ok,{})
    if not seed_ok: errors.append('seed contract missing')
    env={k:ver(k,['--version']) for k in ['node','npm','cargo','rustc']}
    env_ready=all(v.get('exists') for v in env.values())
    add(checks,'local_tauri_build_environment_detected_optional',env_ready,env)
    if not env_ready: warnings.append('Node/npm/Rust/Cargo not all detected; scaffold ready but local build not claimed.')
    verdict='PASS_IMPERIUM_APP_TAURI_SHELL_FOUNDATION_READY' if not errors else 'FAIL_IMPERIUM_APP_TAURI_SHELL_FOUNDATION'
    generated=utc(); summary={'summary_id':'astronomicon.imperium_app_tauri_shell_foundation_summary.v0_1','task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'generated_at_utc':generated,'checks':checks,'errors':errors,'warnings':warnings,'environment':env,'environment_ready_for_tauri_build':env_ready,'run_next':'cd SUPPORT/APP_TAURI && npm install && npm run tauri:dev','not_claimed':matrix.get('not_claimed',[])}
    receipt={'receipt_id':'receipt.astronomicon.imperium_app_tauri_shell_foundation.v0_1','task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'generated_at_utc':generated,'summary':SUMMARY.as_posix(),'report':REPORT.as_posix(),'checks':checks,'errors':errors,'warnings':warnings}
    write_json(repo/SUMMARY,summary); write_json(repo/RECEIPT,receipt)
    checks_md='\n'.join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md='\n'.join(f'- {e}' for e in errors) if errors else '- none'
    warnings_md='\n'.join(f'- {w}' for w in warnings) if warnings else '- none'
    (repo/REPORT).parent.mkdir(parents=True,exist_ok=True); (repo/REPORT).write_text(f"# IMPERIUM APP TAURI SHELL FOUNDATION VALIDATION REPORT V0.1\n\nverdict: `{verdict}`\ngenerated_at_utc: `{generated}`\n\n## Checks\n\n{checks_md}\n\n## Warnings\n\n{warnings_md}\n\n## Errors\n\n{errors_md}\n",encoding='utf-8')
    print(json.dumps({'task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'environment_ready_for_tauri_build':env_ready,'receipt':RECEIPT.as_posix(),'summary':SUMMARY.as_posix(),'report':REPORT.as_posix(),'errors':errors,'warnings':warnings},ensure_ascii=False,indent=2))
    return 0 if verdict.startswith('PASS') else 1
if __name__=='__main__': raise SystemExit(main())
