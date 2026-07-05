#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,subprocess,sys
from pathlib import Path
def npm_cmd(*args): return ['cmd.exe','/d','/s','/c','npm '+' '.join(args)] if os.name=='nt' else ['npm',*args]
def run(name,cmd,cwd,timeout=30,required=False):
    try:
        p=subprocess.run(cmd,cwd=str(cwd),capture_output=True,text=True,timeout=timeout,encoding='utf-8',errors='replace')
        return {'name':name,'cmd':cmd,'required':required,'exit_code':p.returncode,'ok':p.returncode==0,'stdout':p.stdout[-2000:],'stderr':p.stderr[-2000:]}
    except FileNotFoundError as e: return {'name':name,'cmd':cmd,'required':required,'exit_code':None,'ok':False,'stderr':str(e),'missing_executable':True}
    except Exception as e: return {'name':name,'cmd':cmd,'required':required,'exit_code':None,'ok':False,'stderr':str(e)}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('--out',default='ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOLCHAIN_PROOF_REPORT_V0_1.json'); a=ap.parse_args(); repo=Path(a.repo_root).resolve()
    cmds=[('python_version',[sys.executable,'--version'],True),('pwsh_version',['pwsh','--version'],True),('git_version',['git','--version'],True),('node_version',['node','--version'],False),('npm_version',npm_cmd('--version'),False),('rustc_version',['rustc','--version'],False),('cargo_version',['cargo','--version'],False),('go_version',['go','version'],False)]
    res=[run(n,c,repo,required=req) for n,c,req in cmds]
    app=repo/'SUPPORT'/'APP_TAURI'
    if (app/'package.json').is_file(): res.append(run('npm_build_app_tauri_if_present',npm_cmd('run','build'),app,180,False))
    manifest=repo/'SUPPORT'/'APP_TAURI'/'src-tauri'/'Cargo.toml'
    if manifest.is_file(): res.append(run('cargo_check_app_tauri_if_present',['cargo','check','--manifest-path',str(manifest)],repo,180,False))
    report={'tool_id':'mechanicus_toolchain_probe.v0_1','repo_root':str(repo),'results':res,'required_ok':all(r['ok'] for r in res if r.get('required')),'optional_available':[r['name'] for r in res if r['ok'] and not r.get('required')],'optional_missing_or_failed':[r['name'] for r in res if not r['ok'] and not r.get('required')],'warnings':['Local toolchain proof is local machine truth, not universal readiness.','npm audit fix --force is intentionally not run.','Optional toolchain absence is validation debt or future capability gap, not a patch failure.']}
    out=repo/a.out; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2)); return 0 if report['required_ok'] else 1
if __name__=='__main__': raise SystemExit(main())
