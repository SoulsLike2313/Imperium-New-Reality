#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, csv, datetime as dt, hashlib, json, os, re, sys
from collections import Counter, defaultdict
from pathlib import Path

TASK_ID='IMPERIUM-POPULATION-CENSUS-0001'
CENSUS_ID='imperium.population_census.v0_1.fix_0001'
PATCH=Path('WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001')
OUT=PATCH/'OUTPUTS'; REP=PATCH/'REPORTS'
CENSUS_JSON=OUT/'IMPERIUM_POPULATION_CENSUS_V0_1.json'
CENSUS_CSV=OUT/'IMPERIUM_POPULATION_CENSUS_V0_1.csv'
SUMMARY_JSON=OUT/'IMPERIUM_POPULATION_SUMMARY_V0_1.json'
GAP_JSON=OUT/'IMPERIUM_POPULATION_GAP_MAP_V0_1.json'
REPORT_MD=REP/'IMPERIUM_POPULATION_CENSUS_REPORT_V0_1.md'
GAP_MD=REP/'IMPERIUM_POPULATION_GAP_MAP_V0_1.md'
GREAT_NINE={'ASTRONOMICON','ADMINISTRATUM','DOCTRINARIUM','MECHANICUS','INQUISITION','CUSTODES','STRATEGIUM','SCHOLA_IMPERIALIS','OFFICIO_AGENTIS'}
CROWN={'THRONE'}; GOV={'_CORE_GOVERNANCE'}; RINGS={'_POST_WORK_RING'}; PLATFORM={'IMPERIAL_IDE','SPECULUM'}
KNOWN_ROOTS={'ROOT','ORGANS','_CORE','_HARNESS','WARP','REPORTS','SUPPORT','SCHEMAS','DOCTRINARIUM','_CORE_GOVERNANCE','.imperium_patch_backups'}
EXCLUDE={'.git','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','.cache','.venv','venv','node_modules'}
TEXT_EXT={'.md','.txt','.json','.jsonl','.py','.ps1','.yaml','.yml','.toml','.ini','.cfg','.csv','.tsv','.js','.ts','.tsx','.jsx','.html','.css','.scss','.svg','.xml','.rs','.lock'}

def now(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def rel(p,root): return p.relative_to(root).as_posix()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def ph(s): return hashlib.sha1(s.encode('utf-8')).hexdigest()[:12]
def slug(s):
    s=re.sub(r'[^a-z0-9а-яё]+','_',s.lower(),flags=re.I); s=re.sub(r'_+','_',s).strip('_')
    return (s or 'resident')[:54].strip('_') or 'resident'
def utf8(p):
    if p.suffix.lower() not in TEXT_EXT: return 'NOT_TEXT',None
    try: p.read_text(encoding='utf-8'); return 'UTF8_OK',None
    except UnicodeDecodeError as e: return 'UTF8_FAIL',str(e)
    except Exception as e: return 'READ_FAIL',str(e)
def gen_out(r):
    prefs=['WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/OUTPUTS/','WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/RECEIPTS/','WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/REPORTS/']
    return (not r.endswith('.gitkeep')) and any(r.startswith(x) for x in prefs)
def walk(root):
    files=[]; excl=[]
    for cur,dirs,names in os.walk(root):
        curp=Path(cur); currel='.' if curp==root else rel(curp,root)
        keep=[]
        for d in dirs:
            if d in EXCLUDE: excl.append((Path(currel)/d).as_posix() if currel!='.' else d)
            else: keep.append(d)
        dirs[:]=keep
        for n in names:
            p=curp/n; r=rel(p,root)
            if gen_out(r): excl.append(r); continue
            files.append(p)
    return sorted(files), {'excluded_dir_names':sorted(EXCLUDE),'excluded_paths_count':len(excl),'excluded_paths_sample':excl[:200],'generated_outputs_excluded':True}
def root_zone(parts): return 'ROOT' if len(parts)<=1 else parts[0]
def organ_group(parts):
    if len(parts)<2 or parts[0]!='ORGANS': return None
    o=parts[1].upper()
    if o in GREAT_NINE: return 'GREAT_NINE_ORGAN'
    if o in CROWN: return 'CROWN_ORGAN'
    if o in GOV: return 'GOVERNANCE_ZONE'
    if o in RINGS: return 'SPECIAL_RING'
    if o in PLATFORM: return 'PLATFORM_TOOL_ORGAN'
    return 'UNKNOWN_ORGAN_CANDIDATE'
def owner(parts,name,r):
    u=r.upper(); n=name.upper()
    if len(parts)==1:
        if n.startswith('APPLY_'): return 'MECHANICUS'
        if n.endswith('_MANIFEST_SHA256.JSON'): return 'ADMINISTRATUM'
        if n=='AGENTS.MD': return 'OFFICIO_AGENTIS'
        if name.startswith('.'): return 'MECHANICUS'
        return 'UNKNOWN'
    if parts[0]=='_HARNESS':
        if len(parts)>1 and parts[1].upper() in {'_FIXTURES','_NEGATIVE_EXPERIENCE'}: return 'INQUISITION'
        if len(parts)>1 and parts[1].upper() in {'_RUNS','RUNNER'}: return 'MECHANICUS'
        return 'MECHANICUS'
    if parts[0]=='DOCTRINARIUM': return 'DOCTRINARIUM'
    if len(parts)>=2 and parts[0]=='ORGANS':
        o=parts[1].upper()
        if o in GREAT_NINE: return o
        if o=='_CORE_GOVERNANCE':
            if 'THRONE' in u: return 'THRONE'
            return 'OWNER'
        if o in {'IMPERIAL_IDE','SPECULUM'}: return 'MECHANICUS'
        if o=='_POST_WORK_RING': return 'ADMINISTRATUM'
        if o=='THRONE': return 'THRONE'
    for x in sorted(GREAT_NINE|{'THRONE','OWNER'},key=len,reverse=True):
        if x in u: return x
    return 'UNKNOWN'
def root_class(name):
    n=name.upper(); s=Path(name).suffix.lower()
    if name.startswith('.'): return 'ROOT_CONFIG'
    if n.startswith('APPLY_') and s=='.ps1': return 'ROOT_SCRIPT'
    if n.endswith('_MANIFEST_SHA256.JSON'): return 'ROOT_MANIFEST'
    if s=='.lock': return 'LOCKFILE'
    if s in {'.md','.txt'}: return 'ROOT_DOC'
    if s in {'.json','.jsonl'}: return 'ROOT_MANIFEST'
    if s in {'.ps1','.py','.bat','.cmd','.sh'}: return 'ROOT_SCRIPT'
    return 'UNKNOWN'
def cls(parts,name,r):
    if len(parts)==1: return root_class(name)
    u=r.upper(); n=name.upper(); s=Path(name).suffix.lower()
    if '/COCKPIT/' in u or '/APP-TS/' in u or '/SHELL-RS/' in u or s in {'.tsx','.jsx','.rs'}: return 'IDE_SOURCE'
    if n in {'PNPM-LOCK.YAML','CARGO.LOCK','PACKAGE-LOCK.JSON'}: return 'LOCKFILE'
    if s in {'.toml','.ini','.cfg','.npmrc'}: return 'CONFIG'
    if '/_FIXTURES/' in u: return 'FIXTURE'
    if 'GOLDEN' in u: return 'GOLDEN'
    if '/_RUNS/' in u or 'EXECUTION_LOG' in n or n=='RESULTS.JSON': return 'RUN_OUTPUT'
    if n=='README.MD' and len(parts)>=2 and parts[0]=='ORGANS': return 'ORGAN_README'
    if 'ORGAN_CARD' in n: return 'ORGAN_CARD'
    if 'MANIFEST' in n: return 'MANIFEST'
    if n.endswith('.SCHEMA.JSON') or '/SCHEMAS/' in u or '/SCHEMA_SEEDS/' in u: return 'SCHEMA'
    if '/VALIDATORS/' in u or n.startswith('VALIDATE_'): return 'VALIDATOR'
    if '/RECEIPTS/' in u or 'RECEIPT' in n: return 'RECEIPT'
    if '/REPORTS/' in u or 'REPORT' in n: return 'REPORT'
    if '/MATRICES/' in u or 'MATRIX' in n: return 'MATRIX'
    if 'CHARTER' in n or '/CHARTERS/' in u: return 'CHARTER'
    if 'CONSTITUTION' in n or '/CONSTITUTION/' in u: return 'CONSTITUTION'
    if 'PASSPORT' in n or '/PASSPORT' in u: return 'PASSPORT'
    if 'CONTRACT' in n: return 'CONTRACT'
    if '/METRICS/' in u or 'METRIC' in n: return 'METRIC'
    if '/TEMPLATES/' in u or 'TEMPLATE' in n: return 'TEMPLATE'
    if 'DOCTRINE' in n or '/LAWS/' in u or '/ANATOMY/' in u: return 'DOCTRINE'
    if n=='TASK_PACK.MD' or 'TASK_PACK' in n or '/TASK' in u: return 'TASK_PACK'
    if n=='PATCH_PACK.MD' or 'PATCH_PACK' in n or '/PATCHES/' in u: return 'PATCH_PACK'
    if 'NEGATIVE' in u or 'LESSON' in u or 'ANTIPATTERN' in u: return 'NEGATIVE_LESSON'
    if '/TUI/' in u: return 'TUI'
    if 'DASHBOARD' in u: return 'DASHBOARD'
    if 'EYES' in u or 'GRAPH' in u: return 'EYES_EXPORT'
    if 'BACKUP' in u or s in {'.zip','.bundle','.7z','.tar','.gz'}: return 'BACKUP'
    if 'ARCHIVE' in u: return 'ARCHIVE'
    if s in {'.py','.ps1','.js','.ts','.tsx','.jsx','.bat','.cmd','.sh','.rs'}: return 'TOOL_CODE'
    if parts and parts[0]=='WARP': return 'WARP_ARTIFACT'
    return 'UNKNOWN'
def status(parts,r,c):
    u=r.upper(); rz=root_zone(parts)
    if rz=='WARP': return 'WARP'
    if 'QUARANTINE' in u: return 'QUARANTINE'
    if 'NEGATIVE' in u or 'BAD_EXAMPLES' in u or 'ANTIPATTERN' in u: return 'NEGATIVE_EXAMPLE'
    if 'ARCHIVE' in u or c=='ARCHIVE': return 'ARCHIVE'
    if 'GARBAGE' in u or 'TRASH' in u: return 'GARBAGE_CANDIDATE'
    if rz not in KNOWN_ROOTS: return 'ROGUE_CANDIDATE'
    return 'ACTIVE'
def resident(root,p):
    r=rel(p,root); parts=r.split('/'); name=p.name; c=cls(parts,name,r); enc,err=utf8(p)
    return {'imperium_id':f'imp:file:{slug(c)}:{slug(p.stem)}:{ph(r)}','kind':'FILE','class':c,'status':status(parts,r,c),'owner_candidate':owner(parts,name,r),'path':r,'root_zone':root_zone(parts),'organ_group':organ_group(parts),'name':name,'extension':p.suffix.lower(),'bytes':p.stat().st_size,'sha256':sha(p),'path_hash':ph(r),'encoding_status':enc,'encoding_error':err}
def gaps(res):
    byc=defaultdict(list); byr=defaultdict(list); paths={x['path'] for x in res}
    for x in res: byc[x['class']].append(x); byr[x['root_zone']].append(x)
    all_org=sorted({x['path'].split('/')[1] for x in res if x['path'].startswith('ORGANS/') and len(x['path'].split('/'))>1})
    g9=sorted([o for o in all_org if o.upper() in GREAT_NINE]); unknown_org=sorted([o for o in all_org if o.upper() not in GREAT_NINE|CROWN|GOV|RINGS|PLATFORM])
    no_read=[]; no_card=[]; no_manifest=[]
    for o in g9:
        pref=f'ORGANS/{o}/'
        if pref+'README.md' not in paths: no_read.append(o)
        if not any(p.startswith(pref) and 'ORGAN_CARD' in Path(p).name.upper() for p in paths): no_card.append(o)
        if not any(p.startswith(pref) and 'MANIFEST' in Path(p).name.upper() for p in paths): no_manifest.append(o)
    schemas=byc.get('SCHEMA',[]); vals=byc.get('VALIDATOR',[]); recs=byc.get('RECEIPT',[]); reps=byc.get('REPORT',[])
    vt='\n'.join(x['path'].lower() for x in vals); rt='\n'.join(x['path'].lower() for x in recs); rpt='\n'.join(x['path'].lower() for x in reps)
    return {'unknown_root_zones':sorted(set(byr)-KNOWN_ROOTS),'unknown_owner_residents':[x['path'] for x in res if x['owner_candidate']=='UNKNOWN'][:2000],'unknown_owner_count':sum(1 for x in res if x['owner_candidate']=='UNKNOWN'),'unknown_class_residents':[x['path'] for x in res if x['class']=='UNKNOWN'][:2000],'unknown_class_count':sum(1 for x in res if x['class']=='UNKNOWN'),'organs_detected':all_org,'great_nine_organs_detected':g9,'unknown_organ_candidates':unknown_org,'organs_without_readme':no_read,'organs_without_organ_card':no_card,'organs_without_manifest':no_manifest,'schemas_without_obvious_validator':[x['path'] for x in schemas if Path(x['path']).stem.replace('.schema','').lower() not in vt][:2000],'validators_without_obvious_receipt':[x['path'] for x in vals if Path(x['path']).stem.lower().replace('validate_','').replace('run_','') not in rt][:2000],'receipts_without_obvious_report':[x['path'] for x in recs if Path(x['path']).stem.lower().replace('_receipt','') not in rpt][:2000],'warp_packs_detected':sorted({'/'.join(x['path'].split('/')[:3]) for x in res if x['path'].startswith('WARP/PATCHES/') and len(x['path'].split('/'))>=3}),'decode_warning_residents':[x['path'] for x in res if x['encoding_status'] in {'UTF8_FAIL','READ_FAIL'}],'garbage_candidates':[x['path'] for x in res if x['status']=='GARBAGE_CANDIDATE'],'rogue_candidates':[x['path'] for x in res if x['status']=='ROGUE_CANDIDATE'],'negative_examples':[x['path'] for x in res if x['status']=='NEGATIVE_EXAMPLE'],'root_level_residents':[x['path'] for x in res if x['root_zone']=='ROOT']}
def pct(a,b): return round(a*100.0/b,2) if b else 0.0
def summary(res,g):
    total=len(res); cc=Counter(x['class'] for x in res); oc=Counter(x['owner_candidate'] for x in res); sc=Counter(x['status'] for x in res); rc=Counter(x['root_zone'] for x in res); og=Counter(str(x.get('organ_group') or 'NONE') for x in res)
    return {'population_total':total,'class_counts':dict(sorted(cc.items())),'owner_counts':dict(sorted(oc.items())),'status_counts':dict(sorted(sc.items())),'root_zone_counts':dict(sorted(rc.items())),'organ_group_counts':dict(sorted(og.items())),'known_owner_count':total-oc.get('UNKNOWN',0),'unknown_owner_count':oc.get('UNKNOWN',0),'known_class_count':total-cc.get('UNKNOWN',0),'unknown_class_count':cc.get('UNKNOWN',0),'schema_count':cc.get('SCHEMA',0),'validator_count':cc.get('VALIDATOR',0),'receipt_count':cc.get('RECEIPT',0),'report_count':cc.get('REPORT',0),'owner_coverage_score':pct(total-oc.get('UNKNOWN',0),total),'classification_coverage_score':pct(total-cc.get('UNKNOWN',0),total),'schema_to_validator_ratio':round(cc.get('VALIDATOR',0)/cc.get('SCHEMA',1),3) if cc.get('SCHEMA',0) else 0,'validator_to_receipt_ratio':round(cc.get('RECEIPT',0)/cc.get('VALIDATOR',1),3) if cc.get('VALIDATOR',0) else 0,'receipt_to_report_ratio':round(cc.get('REPORT',0)/cc.get('RECEIPT',1),3) if cc.get('RECEIPT',0) else 0,'warp_debt_count':sc.get('WARP',0),'garbage_candidate_count':len(g.get('garbage_candidates',[])),'rogue_candidate_count':len(g.get('rogue_candidates',[])),'root_level_resident_count':len(g.get('root_level_residents',[])),'organ_passport_readiness':{'great_nine_organs_detected':len(g.get('great_nine_organs_detected',[])),'organs_without_readme':len(g.get('organs_without_readme',[])),'organs_without_organ_card':len(g.get('organs_without_organ_card',[])),'organs_without_manifest':len(g.get('organs_without_manifest',[]))},'fix_0001_applied':True}
def write_csv(path,res):
    fields=['imperium_id','kind','class','status','owner_candidate','root_zone','organ_group','path','name','extension','bytes','sha256','encoding_status','encoding_error']
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(res)
def write_reports(root,s,g):
    (root/REP).mkdir(parents=True,exist_ok=True)
    topc='\n'.join(f'- `{k}`: {v}' for k,v in sorted(s['class_counts'].items(),key=lambda x:(-x[1],x[0]))[:40])
    topo='\n'.join(f'- `{k}`: {v}' for k,v in sorted(s['owner_counts'].items(),key=lambda x:(-x[1],x[0]))[:40])
    (root/REPORT_MD).write_text(f'''# IMPERIUM POPULATION CENSUS REPORT V0.1\n\ntask_id: `{TASK_ID}`  \ncensus_id: `{CENSUS_ID}`  \nmode: `MEASURE_ONLY`  \nfix: `0001`\n\n## Summary\n\n- population_total: `{s['population_total']}`\n- owner_coverage_score: `{s['owner_coverage_score']}`\n- classification_coverage_score: `{s['classification_coverage_score']}`\n- schema_count: `{s['schema_count']}`\n- validator_count: `{s['validator_count']}`\n- receipt_count: `{s['receipt_count']}`\n- report_count: `{s['report_count']}`\n- warp_debt_count: `{s['warp_debt_count']}`\n- rogue_candidate_count: `{s['rogue_candidate_count']}`\n- root_level_resident_count: `{s['root_level_resident_count']}`\n\n## Top classes\n\n{topc}\n\n## Owners\n\n{topo}\n\nPASS means measurement baseline, not health certificate.\n''',encoding='utf-8')
    lines=['# IMPERIUM POPULATION GAP MAP V0.1','','fix: `0001`','']
    for k,v in g.items():
        lines += [f'## {k}']
        if isinstance(v,list):
            lines += ['- none'] if not v else [f'- `{x}`' for x in v[:300]] + ([f'- ... truncated, total `{len(v)}`'] if len(v)>300 else [])
        else: lines += [f'`{v}`']
        lines.append('')
    (root/GAP_MD).write_text('\n'.join(lines),encoding='utf-8')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); args=ap.parse_args(); root=Path(args.repo_root).resolve()
    if not root.is_dir(): print('Repo root does not exist',file=sys.stderr); return 2
    (root/OUT).mkdir(parents=True,exist_ok=True); (root/REP).mkdir(parents=True,exist_ok=True)
    files,excl=walk(root); res=[resident(root,p) for p in files]; g=gaps(res); s=summary(res,g)
    census={'census_id':CENSUS_ID,'task_id':TASK_ID,'generated_at_utc':now(),'mode':'MEASURE_ONLY','fix_0001_applied':True,'scan_scope':{'repo_root':str(root),'total_files_scanned':len(files),'known_root_zones':sorted(KNOWN_ROOTS),'exclusions':excl},'summary':s,'gaps':g,'residents':res}
    (root/CENSUS_JSON).write_text(json.dumps(census,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (root/SUMMARY_JSON).write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (root/GAP_JSON).write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    write_csv(root/CENSUS_CSV,res); write_reports(root,s,g)
    print(json.dumps({'task_id':TASK_ID,'census_id':CENSUS_ID,'fix_0001_applied':True,'population_total':len(res),'owner_coverage_score':s['owner_coverage_score'],'classification_coverage_score':s['classification_coverage_score'],'unknown_owner_count':s['unknown_owner_count'],'unknown_class_count':s['unknown_class_count'],'rogue_candidate_count':s['rogue_candidate_count'],'unknown_root_zones':g['unknown_root_zones'],'census_json':CENSUS_JSON.as_posix(),'report':REPORT_MD.as_posix()},ensure_ascii=False,indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
