#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, json
from collections import defaultdict
from pathlib import Path
EXCLUDE_DIRS={'.git','.github','node_modules','target','dist','build','__pycache__','.venv','venv','.mypy_cache','.ruff_cache','.pytest_cache','.next','.turbo','.idea','.vscode'}
EXT_LANGUAGE={'.py':'Python','.ps1':'PowerShell','.psm1':'PowerShell','.psd1':'PowerShell','.rs':'Rust','.js':'JavaScript','.mjs':'JavaScript','.cjs':'JavaScript','.ts':'TypeScript','.tsx':'TypeScript','.jsx':'JavaScript','.css':'CSS','.scss':'CSS','.html':'HTML','.json':'JSON','.jsonl':'JSONL','.md':'Markdown','.toml':'TOML','.yaml':'YAML','.yml':'YAML','.xml':'XML','.svg':'SVG','.go':'Go','.cpp':'C++','.cc':'C++','.cxx':'C++','.hpp':'C++','.h':'C/C++ Header','.c':'C','.bat':'Batch','.cmd':'Batch','.sh':'Shell','.sql':'SQL','.txt':'Text'}
COMMENT_PREFIX={'Python':['#'],'PowerShell':['#'],'Rust':['//'],'JavaScript':['//'],'TypeScript':['//'],'CSS':['/*','*'],'Go':['//'],'C++':['//'],'C':['//'],'Shell':['#'],'Batch':['REM','::'],'SQL':['--'],'TOML':['#'],'YAML':['#']}
def is_binary(path):
    try: return b'\x00' in path.read_bytes()[:4096]
    except Exception: return True
def classify_role(rel, lang):
    r=rel.replace('\\','/'); roles=[]; name=Path(r).name
    if '/VALIDATORS/' in r or name.endswith('_validator.py') or 'validate_' in name: roles.append('validator')
    if '/TOOLS/' in r: roles.append('tool')
    if '/MATRICES/' in r: roles.append('matrix')
    if '/RECEIPTS/' in r: roles.append('receipt')
    if '/REPORTS/' in r: roles.append('report')
    if '/LAWS/' in r: roles.append('law')
    if '/PASSPORT/' in r: roles.append('passport')
    if '/WARP/PATCHES/' in r: roles.append('patch_pack')
    if r.endswith('.ps1') and 'RUN_' in name: roles.append('warp_runner')
    if '/SUPPORT/APP_TAURI/' in r or '/src-tauri/' in r: roles.append('tauri_app')
    if '/src-tauri/src/' in r and lang=='Rust': roles.append('tauri_backend')
    if '/SUPPORT/APP_TAURI/src/' in r and lang in {'JavaScript','TypeScript','CSS','HTML'}: roles.append('tauri_frontend')
    if '/TESTS/' in r or '/tests/' in r: roles.append('test')
    return sorted(set(roles or ['general']))
def count_lines(path, lang):
    try: text=path.read_text(encoding='utf-8-sig', errors='replace')
    except Exception: text=''
    total=blank=comment=code=0; prefixes=COMMENT_PREFIX.get(lang,[]); in_css=False
    for line in text.splitlines():
        total+=1; s=line.strip()
        if not s: blank+=1; continue
        is_comment=False
        if lang=='CSS':
            if s.startswith('/*'): is_comment=True; in_css='*/' not in s
            elif in_css: is_comment=True; in_css='*/' not in s
            elif s.startswith('*'): is_comment=True
        else:
            up=s.upper()
            for p in prefixes:
                if p in {'REM','::'}:
                    if up.startswith(p): is_comment=True; break
                elif s.startswith(p): is_comment=True; break
        if is_comment: comment+=1
        else: code+=1
    return {'total':total,'code':code,'blank':blank,'comment':comment}
def iter_files(repo):
    for path in repo.rglob('*'):
        if not path.is_file(): continue
        if set(path.relative_to(repo).parts) & EXCLUDE_DIRS: continue
        if is_binary(path): continue
        yield path
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root', default='.'); ap.add_argument('--out', default='ORGANS/MECHANICUS/REPORTS/MECHANICUS_LANGUAGE_SURFACE_CENSUS_V0_1.json'); args=ap.parse_args()
    repo=Path(args.repo_root).resolve(); by=defaultdict(lambda:{'files':0,'total_lines':0,'code_lines':0,'blank_lines':0,'comment_lines':0,'bytes':0,'roles':defaultdict(lambda:{'files':0,'total_lines':0}),'largest_files':[]})
    scanned=unknown=0
    for path in iter_files(repo):
        rel=path.relative_to(repo).as_posix(); lang=EXT_LANGUAGE.get(path.suffix.lower())
        if not lang: unknown+=1; continue
        c=count_lines(path,lang); roles=classify_role(rel,lang); stat=by[lang]
        stat['files']+=1; stat['total_lines']+=c['total']; stat['code_lines']+=c['code']; stat['blank_lines']+=c['blank']; stat['comment_lines']+=c['comment']; stat['bytes']+=path.stat().st_size
        for role in roles: stat['roles'][role]['files']+=1; stat['roles'][role]['total_lines']+=c['total']
        stat['largest_files'].append({'path':rel,'lines':c['total'],'code_lines':c['code'],'bytes':path.stat().st_size,'roles':roles}); scanned+=1
    langs=[]
    for lang,stat in by.items():
        langs.append({'language':lang,'files':stat['files'],'total_lines':stat['total_lines'],'code_lines':stat['code_lines'],'blank_lines':stat['blank_lines'],'comment_lines':stat['comment_lines'],'bytes':stat['bytes'],'roles':{k:v for k,v in sorted(stat['roles'].items())},'largest_files':sorted(stat['largest_files'], key=lambda x:(x['lines'],x['bytes']), reverse=True)[:15]})
    langs.sort(key=lambda x:(x['total_lines'],x['files']), reverse=True)
    report={'tool_id':'mechanicus_language_surface_census.v0_1','repo_root':str(repo),'files_scanned':scanned,'unknown_text_files':unknown,'language_count':len(langs),'total_counted_lines':sum(x['total_lines'] for x in langs),'languages':langs,'warnings':['This is a language surface census, not a code purity verdict.','Generated/receipt/report files are included unless excluded by directory policy.','Future versions should add git-tracked-only mode and generated-artifact filtering.']}
    out=repo/args.out; out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8'); print(json.dumps(report, ensure_ascii=False, indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
