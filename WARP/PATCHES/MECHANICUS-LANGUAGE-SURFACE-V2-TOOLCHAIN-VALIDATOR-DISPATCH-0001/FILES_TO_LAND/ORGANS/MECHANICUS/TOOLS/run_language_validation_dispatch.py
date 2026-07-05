#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,py_compile,subprocess,sys,tomllib
from pathlib import Path
EXCLUDE={'.git','node_modules','target','dist','build','__pycache__','.venv','venv','.mypy_cache','.ruff_cache','.pytest_cache'}
def files(repo,sufs):
    out=[]
    for p in repo.rglob('*'):
        if p.is_file() and p.suffix.lower() in sufs and not (set(p.relative_to(repo).parts)&EXCLUDE): out.append(p)
    return out
def cap(x,n=50): return x[:n]
def v_json(repo):
    errs=[]; fs=files(repo,{'.json','.jsonl'})
    for p in fs:
        try:
            if p.suffix.lower()=='.jsonl':
                for i,l in enumerate(p.read_text(encoding='utf-8-sig',errors='replace').splitlines(),1):
                    if l.strip(): json.loads(l)
            else: json.loads(p.read_text(encoding='utf-8-sig'))
        except Exception as e: errs.append({'path':p.relative_to(repo).as_posix(),'error':str(e)})
    return {'language':'JSON/JSONL','files_checked':len(fs),'ok':not errs,'errors':cap(errs)}
def v_toml(repo):
    errs=[]; fs=files(repo,{'.toml'})
    for p in fs:
        try: tomllib.loads(p.read_text(encoding='utf-8-sig'))
        except Exception as e: errs.append({'path':p.relative_to(repo).as_posix(),'error':str(e)})
    return {'language':'TOML','files_checked':len(fs),'ok':not errs,'errors':cap(errs)}
def v_py(repo):
    errs=[]; fs=files(repo,{'.py'})
    for p in fs:
        try: py_compile.compile(str(p),doraise=True)
        except Exception as e: errs.append({'path':p.relative_to(repo).as_posix(),'error':str(e)})
    return {'language':'Python','files_checked':len(fs),'ok':not errs,'errors':cap(errs)}
def v_md(repo):
    fs=files(repo,{'.md'}); empty=[]
    for p in fs:
        if not p.read_text(encoding='utf-8',errors='replace').strip(): empty.append(p.relative_to(repo).as_posix())
    return {'language':'Markdown','files_checked':len(fs),'ok':not empty,'errors':[{'path':x,'error':'empty markdown'} for x in cap(empty)]}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('--out',default='ORGANS/MECHANICUS/REPORTS/MECHANICUS_LANGUAGE_VALIDATION_BASELINE_V0_1.json'); a=ap.parse_args(); repo=Path(a.repo_root).resolve()
    checks=[v_json(repo),v_toml(repo),v_py(repo),v_md(repo)]
    debt=[{'language':c['language'],'files_checked':c['files_checked'],'error_count_visible':len(c.get('errors',[])),'errors':c.get('errors',[])} for c in checks if not c.get('ok')]
    report={'tool_id':'mechanicus_language_validator_dispatch_baseline.v0_1','repo_root':str(repo),'mode':'BASELINE_MEASURED_WITH_VALIDATION_DEBT','checks':checks,'all_baseline_checks_clean':not debt,'validation_debt':debt,'verdict':'PASS_BASELINE_CLEAN_FOR_IMPLEMENTED_CHECKS' if not debt else 'PASS_BASELINE_MEASURED_WITH_VALIDATION_DEBT','not_claimed':['100% code cleanliness','all linters present','all language validators complete','architecture clean','dependency security clean'],'warnings':['This baseline intentionally does not claim 100% clean.','Missing lint/type/security tools remain future validation debt.','Build proof is not code purity proof.']}
    out=repo/a.out; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
