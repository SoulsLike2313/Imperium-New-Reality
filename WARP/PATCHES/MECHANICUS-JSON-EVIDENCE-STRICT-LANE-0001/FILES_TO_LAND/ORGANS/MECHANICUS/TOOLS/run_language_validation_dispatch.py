#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, py_compile, subprocess, sys, tomllib
from pathlib import Path
TOOL_ID='mechanicus_language_validator_dispatch_baseline.v0_4_json_strict_lane_aware'
EXCLUDE={'.git','node_modules','target','dist','build','__pycache__','.venv','venv','.mypy_cache','.ruff_cache','.pytest_cache','.next','.turbo','.idea','.vscode'}
JSON_SCANNER=Path('ORGANS/MECHANICUS/TOOLS/scan_mechanicus_json_evidence_strict_lane.py')
JSON_REPORT=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_JSON_EVIDENCE_STRICT_LANE_REPORT_V0_1.json')
def is_src(p,repo):
    rel=p.relative_to(repo).as_posix()
    if rel.startswith('WARP/PATCHES/') or '/FILES_TO_LAND/' in rel: return False
    return not bool(set(p.relative_to(repo).parts)&EXCLUDE)
def files(repo,sufs): return [p for p in repo.rglob('*') if p.is_file() and p.suffix.lower() in sufs and is_src(p,repo)]
def cap(xs,n=80): return xs[:n]
def load(path):
    try: return json.loads(path.read_text(encoding='utf-8-sig')) if path.is_file() else {}
    except Exception: return {}
def tool_ok(tc,names):
    rs={r.get('name'):r for r in tc.get('results',[]) or []}
    return all(bool(rs.get(n,{}).get('ok')) for n in names)
def val_json(repo):
    if (repo/JSON_SCANNER).is_file(): subprocess.run([sys.executable,str(repo/JSON_SCANNER),'--repo-root',str(repo),'--out',JSON_REPORT.as_posix()],cwd=str(repo),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=300)
    r=load(repo/JSON_REPORT); canonical=r.get('canonical_parse_debt',[]) or []
    return {'language':'JSON/JSONL','lane_id':'json_evidence','files_checked':r.get('files_checked',0),'ok':int(r.get('canonical_parse_debt_count',999999))==0,'baseline_type':'json_evidence_strict_lane_canonical_parse_with_classified_debt','errors':cap(canonical),'strict_lane_report':JSON_REPORT.as_posix(),'classified_nonblocking_debt':{'expected_negative_fixture_count':r.get('expected_negative_fixture_count',0),'quarantine_parse_debt_count':r.get('quarantine_parse_debt_count',0),'patch_candidate_parse_error_count':r.get('patch_candidate_parse_error_count',0)},'not_claimed':['schema correctness','semantic evidence truth','receipt honesty']}
def val_py(repo):
    err=[]
    for p in files(repo,{'.py'}):
        try: py_compile.compile(str(p),doraise=True)
        except Exception as e: err.append({'path':p.relative_to(repo).as_posix(),'error':str(e)})
    return {'language':'Python','lane_id':'python','files_checked':len(files(repo,{'.py'})),'ok':not err,'baseline_type':'py_compile_current_non_patch_python','errors':cap(err)}
def val_toml(repo):
    err=[]
    for p in files(repo,{'.toml'}):
        try: tomllib.loads(p.read_text(encoding='utf-8-sig'))
        except Exception as e: err.append({'path':p.relative_to(repo).as_posix(),'error':str(e)})
    return {'language':'TOML','lane_id':'toml_config','files_checked':len(files(repo,{'.toml'})),'ok':not err,'baseline_type':'parse_all_current_toml','errors':cap(err)}
def val_md(repo):
    fs=files(repo,{'.md'}); empty=[p.relative_to(repo).as_posix() for p in fs if not p.read_text(encoding='utf-8',errors='replace').strip()]
    return {'language':'Markdown','lane_id':'markdown_docs','files_checked':len(fs),'ok':not empty,'baseline_type':'non_empty_markdown_current_non_patch','errors':[{'path':x,'error':'empty markdown'} for x in cap(empty)]}
def val_ps(repo,tc):
    fs=files(repo,{'.ps1','.psm1','.psd1'}); ok=tool_ok(tc,['pwsh_version']) or len(fs)==0
    return {'language':'PowerShell','lane_id':'powershell','files_checked':len(fs),'ok':ok,'baseline_type':'powershell_surface_and_toolchain_detection_no_parser_yet','toolchain_ok':tool_ok(tc,['pwsh_version']),'errors':[] if ok else [{'path':'','error':'PowerShell files exist but pwsh unavailable'}]}
def val_rust(repo,tc):
    fs=files(repo,{'.rs'}); ok=tool_ok(tc,['rustc_version','cargo_version']) or len(fs)==0
    return {'language':'Rust','lane_id':'rust','files_checked':len(fs),'ok':ok,'baseline_type':'rust_surface_and_toolchain_detection_no_cargo_check','toolchain_ok':tool_ok(tc,['rustc_version','cargo_version']),'errors':[] if ok else [{'path':'','error':'Rust files exist but rust/cargo unavailable'}]}
def val_node(repo,tc):
    fs=files(repo,{'.js','.mjs','.cjs','.ts','.tsx','.jsx'}); ok=tool_ok(tc,['node_version','npm_version']) or len(fs)==0
    return {'language':'JavaScript/TypeScript','lane_id':'node_frontend','files_checked':len(fs),'ok':ok,'baseline_type':'node_frontend_surface_and_toolchain_detection_no_npm_build','toolchain_ok':tool_ok(tc,['node_version','npm_version']),'errors':[] if ok else [{'path':'','error':'JS/TS files exist but node/npm unavailable'}]}
def val_css(repo,tc):
    err=[]; fs=files(repo,{'.css','.scss'})
    for p in fs:
        text=p.read_text(encoding='utf-8',errors='replace')
        if text.count('{')!=text.count('}'): err.append({'path':p.relative_to(repo).as_posix(),'error':'brace count mismatch'})
    return {'language':'CSS','lane_id':'css_ui','files_checked':len(fs),'ok':not err,'baseline_type':'css_structural_brace_balance_current_non_patch','errors':cap(err)}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('--out',default='ORGANS/MECHANICUS/REPORTS/MECHANICUS_LANGUAGE_VALIDATION_BASELINE_V0_1.json'); a=ap.parse_args(); repo=Path(a.repo_root).resolve(); tc=load(repo/'ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOLCHAIN_PROOF_REPORT_V0_1.json')
    checks=[val_json(repo),val_toml(repo),val_py(repo),val_md(repo),val_ps(repo,tc),val_rust(repo,tc),val_node(repo,tc),val_css(repo,tc)]
    debt=[{'language':c.get('language'),'lane_id':c.get('lane_id'),'files_checked':c.get('files_checked'),'baseline_type':c.get('baseline_type'),'error_count_visible':len(c.get('errors',[])),'errors':c.get('errors',[])} for c in checks if not c.get('ok')]
    report={'tool_id':TOOL_ID,'repo_root':str(repo),'mode':'LANE_EXPANDED_BASELINE_WITH_JSON_STRICT_CLASSIFICATION','checks':checks,'all_baseline_checks_clean':not debt,'validation_debt':debt,'verdict':'PASS_BASELINE_CLEAN_FOR_IMPLEMENTED_LANE_CHECKS' if not debt else 'PASS_BASELINE_MEASURED_WITH_VALIDATION_DEBT','not_claimed':['100% code cleanliness','all strict build lanes passed','JSON semantic truth'],'warnings':['JSON evidence uses strict classification: canonical parse debt blocks; fixtures/quarantine remain visible but nonblocking for canonical readiness.']}
    out=repo/a.out; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
