
from __future__ import annotations
import argparse, json, os, subprocess, sys, re, py_compile
from pathlib import Path
PATCH_ID='CUSTODES-MECHANICUS-PROSECUTOR-GATE-0001'
VALIDATOR_ID='custodes_mechanicus_prosecutor_gate_validator.v0_1'
CONTROL_RE=re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
REQUIRED_STATIC=['ORGANS/MECHANICUS/MANIFEST.json','ORGANS/MECHANICUS/MATRICES/MECHANICUS_CURRENT_TRUTH_INDEX_V0_1.json','ORGANS/CUSTODES/LAWS/CUSTODES_MECHANICUS_PROSECUTOR_GATE_LAW_V0_1.json','ORGANS/CUSTODES/MATRICES/CUSTODES_MECHANICUS_PROSECUTOR_GATE_MATRIX_V0_1.json','ORGANS/CUSTODES/TOOLS/build_custodes_mechanicus_prosecutor_gate.py']
GENERATED=['ORGANS/CUSTODES/RECEIPTS/custodes_mechanicus_prosecutor_gate_receipt.json','ORGANS/CUSTODES/REPORTS/CUSTODES_MECHANICUS_PROSECUTOR_GATE_SUMMARY_V0_1.json','ORGANS/CUSTODES/REPORTS/CUSTODES_MECHANICUS_PROSECUTOR_GATE_REPORT_V0_1.json','ORGANS/CUSTODES/REPORTS/CUSTODES_MECHANICUS_PROSECUTOR_GATE_REPORT_V0_1.md']
def rel(repo:Path,p:str)->Path: return repo / p.replace('/',os.sep)
def no_control_chars(path:Path):
    if not path.exists(): return []
    return [{'index':m.start(),'codepoint':ord(m.group(0))} for m in CONTROL_RE.finditer(path.read_text(encoding='utf-8',errors='replace'))]
def read_json(repo:Path,p:str): return json.loads(rel(repo,p).read_text(encoding='utf-8'))
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('--apply',action='store_true'); args=ap.parse_args(); repo=Path(args.repo_root).resolve(); errors=[]; warnings=[]; checks=[]
    if args.apply:
        patch_files=repo/'WARP'/'PATCHES'/PATCH_ID/'FILES_TO_LAND'
        if not patch_files.exists():
            print(json.dumps({'task_id':PATCH_ID,'validator_id':VALIDATOR_ID,'verdict':'FAIL','errors':[f'MISSING_FILES_TO_LAND::{patch_files}']},ensure_ascii=False,indent=2)); return 1
        for src in patch_files.rglob('*'):
            if src.is_file():
                dst=repo/src.relative_to(patch_files); dst.parent.mkdir(parents=True,exist_ok=True); dst.write_bytes(src.read_bytes())
    for p in REQUIRED_STATIC:
        pp=rel(repo,p); exists=pp.exists(); checks.append({'name':f'exists::{p}','status':'PASS' if exists else 'FAIL','details':{'path':p}})
        if not exists: errors.append(f'MISSING_REQUIRED_STATIC::{p}'); continue
        hits=no_control_chars(pp); checks.append({'name':f'no_control_chars::{p}','status':'PASS' if not hits else 'FAIL','details':{'hits':hits}})
        if hits: errors.append(f'CONTROL_CHARS::{p}')
        if p.endswith('.json'):
            try: read_json(repo,p); checks.append({'name':f'json_parse::{p}','status':'PASS','details':{}})
            except Exception as e: errors.append(f'JSON_PARSE_ERROR::{p}::{e}'); checks.append({'name':f'json_parse::{p}','status':'FAIL','details':{'error':str(e)}})
        if p.endswith('.py'):
            try: py_compile.compile(str(pp),doraise=True); checks.append({'name':f'py_compile::{p}','status':'PASS','details':{}})
            except Exception as e: errors.append(f'PY_COMPILE_ERROR::{p}::{e}'); checks.append({'name':f'py_compile::{p}','status':'FAIL','details':{'error':str(e)}})
    if not errors:
        proc=subprocess.run([sys.executable,str(rel(repo,'ORGANS/CUSTODES/TOOLS/build_custodes_mechanicus_prosecutor_gate.py')),'--repo-root',str(repo)],text=True,capture_output=True)
        if proc.returncode!=0:
            errors.append('BUILDER_FAILED')
            try: detail=json.loads(proc.stdout)
            except Exception: detail={'stdout':proc.stdout,'stderr':proc.stderr}
            checks.append({'name':'builder_runs','status':'FAIL','details':detail})
        else: checks.append({'name':'builder_runs','status':'PASS','details':json.loads(proc.stdout)})
    generated_ok=True
    for p in GENERATED:
        exists=rel(repo,p).exists(); checks.append({'name':f'generated::{p}','status':'PASS' if exists else 'FAIL','details':{'path':p}})
        if not exists: generated_ok=False; errors.append(f'MISSING_GENERATED::{p}')
    if generated_ok:
        try:
            summary=read_json(repo,'ORGANS/CUSTODES/REPORTS/CUSTODES_MECHANICUS_PROSECUTOR_GATE_SUMMARY_V0_1.json'); report=read_json(repo,'ORGANS/CUSTODES/REPORTS/CUSTODES_MECHANICUS_PROSECUTOR_GATE_REPORT_V0_1.json')
            checks.append({'name':'summary_verdict_pass','status':'PASS' if summary.get('verdict')=='PASS_CUSTODES_MECHANICUS_PROSECUTOR_GATE_READY' else 'FAIL','details':{'verdict':summary.get('verdict')}})
            checks.append({'name':'custodes_prosecution_status_pass','status':'PASS' if report.get('custodes_prosecution_status')=='PASS_BASELINE_PROSECUTION' else 'FAIL','details':{'value':report.get('custodes_prosecution_status')}})
            checks.append({'name':'no_organ_assembly_claim','status':'PASS' if report.get('organ_assembly_claim') is False else 'FAIL','details':{'value':report.get('organ_assembly_claim')}})
            checks.append({'name':'no_throne_crown_claim','status':'PASS' if report.get('throne_crown_claim') is False else 'FAIL','details':{'value':report.get('throne_crown_claim')}})
            if summary.get('verdict')!='PASS_CUSTODES_MECHANICUS_PROSECUTOR_GATE_READY': errors.append('SUMMARY_VERDICT_NOT_PASS')
            if report.get('custodes_prosecution_status')!='PASS_BASELINE_PROSECUTION': errors.append('CUSTODES_PROSECUTION_STATUS_NOT_PASS')
            if report.get('organ_assembly_claim') is not False: errors.append('ORGAN_ASSEMBLY_OVERCLAIM')
            if report.get('throne_crown_claim') is not False: errors.append('THRONE_CROWN_OVERCLAIM')
        except Exception as e: errors.append(f'GENERATED_JSON_CHECK_ERROR::{e}')
    verdict='PASS_CUSTODES_MECHANICUS_PROSECUTOR_GATE_READY' if not errors else 'FAIL_CUSTODES_MECHANICUS_PROSECUTOR_GATE'
    print(json.dumps({'task_id':PATCH_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'receipt':'ORGANS/CUSTODES/RECEIPTS/custodes_mechanicus_prosecutor_gate_receipt.json','summary':'ORGANS/CUSTODES/REPORTS/CUSTODES_MECHANICUS_PROSECUTOR_GATE_SUMMARY_V0_1.json','report_json':'ORGANS/CUSTODES/REPORTS/CUSTODES_MECHANICUS_PROSECUTOR_GATE_REPORT_V0_1.json','report_md':'ORGANS/CUSTODES/REPORTS/CUSTODES_MECHANICUS_PROSECUTOR_GATE_REPORT_V0_1.md','errors':errors,'warnings':warnings,'checks':checks},ensure_ascii=False,indent=2))
    return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
