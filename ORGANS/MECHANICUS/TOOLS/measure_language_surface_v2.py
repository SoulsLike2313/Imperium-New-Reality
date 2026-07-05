#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import defaultdict
from pathlib import Path
EXCLUDE={'.git','node_modules','target','dist','build','__pycache__','.venv','venv','.mypy_cache','.ruff_cache','.pytest_cache','.next','.turbo','.idea','.vscode'}
EXT={'.py':'Python','.ps1':'PowerShell','.psm1':'PowerShell','.psd1':'PowerShell','.rs':'Rust','.js':'JavaScript','.mjs':'JavaScript','.cjs':'JavaScript','.ts':'TypeScript','.tsx':'TypeScript','.jsx':'JavaScript','.css':'CSS','.scss':'CSS','.html':'HTML','.json':'JSON','.jsonl':'JSONL','.md':'Markdown','.toml':'TOML','.yaml':'YAML','.yml':'YAML','.xml':'XML','.svg':'SVG','.go':'Go','.cpp':'C++','.cc':'C++','.cxx':'C++','.hpp':'C++','.h':'C/C++ Header','.c':'C','.bat':'Batch','.cmd':'Batch','.sh':'Shell','.sql':'SQL','.txt':'Text'}
COM={'Python':['#'],'PowerShell':['#'],'Rust':['//'],'JavaScript':['//'],'TypeScript':['//'],'CSS':['/*','*'],'Go':['//'],'C++':['//'],'C':['//'],'Shell':['#'],'Batch':['REM','::'],'SQL':['--'],'TOML':['#'],'YAML':['#']}
def is_bin(p):
    try:return b'\x00' in p.read_bytes()[:4096]
    except Exception:return True
def cls(rel):
    r=rel.replace('\\','/')
    if r.startswith('WARP/PATCHES/') or '/FILES_TO_LAND/' in r:return 'patch_pack_payload'
    if any(x in r for x in ['/RECEIPTS/','/REPORTS/','/MATRICES/','/CONTRACTS/','/LAWS/','/PASSPORT/']):return 'governance_evidence'
    if r.endswith('.md') or '/README' in r:return 'documentation'
    if r.startswith('ORGANS/') and any(x in r for x in ['/VALIDATORS/','/TOOLS/','/SKILLS/']):return 'source_runtime'
    if r.startswith('SUPPORT/') or r.startswith('ORGANS/IMPERIAL_IDE/') or r.endswith(('.py','.ps1','.rs','.js','.ts','.css','.go','.cpp','.c','.h','.toml')):return 'source_runtime'
    return 'unknown'
def role(rel,lang):
    r=rel.replace('\\','/'); out=[]
    if '/VALIDATORS/' in r or 'validate_' in Path(r).name:out.append('validator')
    if '/TOOLS/' in r:out.append('tool')
    if '/MATRICES/' in r:out.append('matrix')
    if '/RECEIPTS/' in r:out.append('receipt')
    if '/REPORTS/' in r:out.append('report')
    if '/LAWS/' in r:out.append('law')
    if r.startswith('WARP/PATCHES/'):out.append('patch_pack')
    if r.endswith('.ps1') and 'RUN_' in Path(r).name:out.append('warp_runner')
    if '/SUPPORT/APP_TAURI/' in r:out.append('tauri_app')
    if '/src-tauri/src/' in r and lang=='Rust':out.append('tauri_backend')
    if '/SUPPORT/APP_TAURI/src/' in r and lang in {'JavaScript','TypeScript','CSS','HTML'}:out.append('tauri_frontend')
    return sorted(set(out or ['general']))
def counts(p,lang):
    text=p.read_text(encoding='utf-8-sig',errors='replace'); total=blank=comment=code=0; in_css=False
    for line in text.splitlines():
        total+=1; s=line.strip()
        if not s: blank+=1; continue
        c=False
        if lang=='CSS':
            if s.startswith('/*'): c=True; in_css='*/' not in s
            elif in_css: c=True; in_css='*/' not in s
            elif s.startswith('*'): c=True
        else:
            up=s.upper()
            for pref in COM.get(lang,[]):
                if pref in {'REM','::'}:
                    if up.startswith(pref): c=True; break
                elif s.startswith(pref): c=True; break
        if c: comment+=1
        else: code+=1
    return {'total':total,'code':code,'blank':blank,'comment':comment}
def add(bucket,lang,rel,roles,c,b):
    st=bucket.setdefault(lang,{'files':0,'total_lines':0,'code_lines':0,'blank_lines':0,'comment_lines':0,'bytes':0,'roles':defaultdict(lambda:{'files':0,'total_lines':0}),'largest_files':[]})
    st['files']+=1; st['total_lines']+=c['total']; st['code_lines']+=c['code']; st['blank_lines']+=c['blank']; st['comment_lines']+=c['comment']; st['bytes']+=b
    for r in roles: st['roles'][r]['files']+=1; st['roles'][r]['total_lines']+=c['total']
    st['largest_files'].append({'path':rel,'lines':c['total'],'code_lines':c['code'],'bytes':b,'roles':roles})
def norm(bucket):
    out=[]
    for lang,st in bucket.items():
        out.append({'language':lang,'files':st['files'],'total_lines':st['total_lines'],'code_lines':st['code_lines'],'blank_lines':st['blank_lines'],'comment_lines':st['comment_lines'],'bytes':st['bytes'],'roles':{k:v for k,v in sorted(st['roles'].items())},'largest_files':sorted(st['largest_files'],key=lambda x:(x['lines'],x['bytes']),reverse=True)[:20]})
    return sorted(out,key=lambda x:(x['total_lines'],x['files']),reverse=True)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('--out',default='ORGANS/MECHANICUS/REPORTS/MECHANICUS_LANGUAGE_SURFACE_V2_REPORT_V0_1.json'); a=ap.parse_args(); repo=Path(a.repo_root).resolve()
    raw={}; bycls=defaultdict(dict); scanned=unknown=0
    for p in repo.rglob('*'):
        if not p.is_file(): continue
        rel=p.relative_to(repo).as_posix(); parts=set(p.relative_to(repo).parts)
        if parts & EXCLUDE or is_bin(p): continue
        lang=EXT.get(p.suffix.lower())
        if not lang: unknown+=1; continue
        c=counts(p,lang); roles=role(rel,lang); cl=cls(rel); b=p.stat().st_size
        add(raw,lang,rel,roles,c,b); add(bycls[cl],lang,rel,roles,c,b); scanned+=1
    classes={}
    for cl,b in sorted(bycls.items()):
        langs=norm(b); classes[cl]={'language_count':len(langs),'total_lines':sum(x['total_lines'] for x in langs),'code_lines':sum(x['code_lines'] for x in langs),'files':sum(x['files'] for x in langs),'languages':langs}
    rawlangs=norm(raw)
    report={'tool_id':'mechanicus_language_surface_v2.v0_1','repo_root':str(repo),'files_scanned':scanned,'unknown_text_files':unknown,'raw_all_surface':{'language_count':len(rawlangs),'total_lines':sum(x['total_lines'] for x in rawlangs),'code_lines':sum(x['code_lines'] for x in rawlangs),'files':sum(x['files'] for x in rawlangs),'languages':rawlangs},'classes':classes,'warnings':['Raw total is not source-code total.','Use classes.source_runtime for source-code purity planning.','Use governance_evidence for receipts/reports/matrices/contracts validation planning.']}
    out=repo/a.out; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
