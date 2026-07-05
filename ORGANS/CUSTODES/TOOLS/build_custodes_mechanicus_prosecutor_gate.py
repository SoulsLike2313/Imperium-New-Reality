
from __future__ import annotations
import argparse, json, os, re, py_compile
from pathlib import Path
from datetime import datetime, timezone
PATCH_ID='CUSTODES-MECHANICUS-PROSECUTOR-GATE-0001'
VALIDATOR_ID='custodes_mechanicus_prosecutor_gate_validator.v0_1'
REQUIRED_JSON=['ORGANS/MECHANICUS/MANIFEST.json','ORGANS/MECHANICUS/MATRICES/MECHANICUS_CURRENT_TRUTH_INDEX_V0_1.json','ORGANS/MECHANICUS/MATRICES/MECHANICUS_PERSONAL_VALIDATORS_REGISTRY_V0_1.json','ORGANS/MECHANICUS/REPORTS/MECHANICUS_RESIDENCY_TRUST_GATE_REPORT_V0_1.json','ORGANS/MECHANICUS/REPORTS/MECHANICUS_RESIDENCY_TRUST_GATE_SUMMARY_V0_1.json','ORGANS/MECHANICUS/RECEIPTS/mechanicus_residency_trust_gate_receipt.json','ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_ADMISSION_V2_SUMMARY_V0_1.json','ORGANS/CUSTODES/LAWS/CUSTODES_MECHANICUS_PROSECUTOR_GATE_LAW_V0_1.json','ORGANS/CUSTODES/MATRICES/CUSTODES_MECHANICUS_PROSECUTOR_GATE_MATRIX_V0_1.json']
REQUIRED_PY=['ORGANS/CUSTODES/TOOLS/build_custodes_mechanicus_prosecutor_gate.py','ORGANS/CUSTODES/VALIDATORS/validate_custodes_mechanicus_prosecutor_gate.py']
CONTROL_RE=re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
def rel(repo: Path, p: str) -> Path: return repo / p.replace('/', os.sep)
def has_control_chars(path: Path):
    return [{'index':m.start(),'codepoint':ord(m.group(0))} for m in CONTROL_RE.finditer(path.read_text(encoding='utf-8',errors='replace'))]
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); args=ap.parse_args(); repo=Path(args.repo_root).resolve()
    errors=[]; warnings=[]; checks=[]; loaded={}
    for p in REQUIRED_JSON:
        pp=rel(repo,p)
        if not pp.exists(): errors.append(f'MISSING_REQUIRED_JSON::{p}'); checks.append({'name':f'exists::{p}','status':'FAIL','details':{'path':p}}); continue
        checks.append({'name':f'exists::{p}','status':'PASS','details':{'path':p}})
        hits=has_control_chars(pp); checks.append({'name':f'no_control_chars::{p}','status':'PASS' if not hits else 'FAIL','details':{'hits':hits}})
        if hits: errors.append(f'CONTROL_CHARS::{p}')
        try: loaded[p]=json.loads(pp.read_text(encoding='utf-8')); checks.append({'name':f'json_parse::{p}','status':'PASS','details':{}})
        except Exception as e: errors.append(f'JSON_PARSE_ERROR::{p}::{e}'); checks.append({'name':f'json_parse::{p}','status':'FAIL','details':{'error':str(e)}})
    for p in REQUIRED_PY:
        pp=rel(repo,p)
        if not pp.exists(): errors.append(f'MISSING_REQUIRED_PY::{p}'); checks.append({'name':f'exists::{p}','status':'FAIL','details':{'path':p}}); continue
        checks.append({'name':f'exists::{p}','status':'PASS','details':{'path':p}})
        hits=has_control_chars(pp); checks.append({'name':f'no_control_chars::{p}','status':'PASS' if not hits else 'FAIL','details':{'hits':hits}})
        if hits: errors.append(f'CONTROL_CHARS::{p}')
        try: py_compile.compile(str(pp),doraise=True); checks.append({'name':f'py_compile::{p}','status':'PASS','details':{}})
        except Exception as e: errors.append(f'PY_COMPILE_ERROR::{p}::{e}'); checks.append({'name':f'py_compile::{p}','status':'FAIL','details':{'error':str(e)}})
    manifest=loaded.get('ORGANS/MECHANICUS/MANIFEST.json',{})
    current_truth=loaded.get('ORGANS/MECHANICUS/MATRICES/MECHANICUS_CURRENT_TRUTH_INDEX_V0_1.json',{})
    residency_report=loaded.get('ORGANS/MECHANICUS/REPORTS/MECHANICUS_RESIDENCY_TRUST_GATE_REPORT_V0_1.json',{})
    residency_summary=loaded.get('ORGANS/MECHANICUS/REPORTS/MECHANICUS_RESIDENCY_TRUST_GATE_SUMMARY_V0_1.json',{})
    tool_summary=loaded.get('ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_ADMISSION_V2_SUMMARY_V0_1.json',{})
    personal_registry=loaded.get('ORGANS/MECHANICUS/MATRICES/MECHANICUS_PERSONAL_VALIDATORS_REGISTRY_V0_1.json',{})
    indexed_records=current_truth.get('current_gate_truth') or residency_report.get('indexed_gate_records') or []
    gate_states={r.get('gate_id'):r.get('state') for r in indexed_records if isinstance(r,dict)}
    required_gate_ids=['G1_IDENTITY_MANIFEST','G2_FUNCTIONS_REGISTRY','G3_CAPABILITY_EVIDENCE','G4_PERSONAL_VALIDATORS','G5_CURRENT_TRUTH_RECEIPTS','G6_RESIDENCY_TRUST']
    bad={gid:gate_states.get(gid) for gid in required_gate_ids if gate_states.get(gid)!='PASS_BASELINE'}
    if bad: errors.append('SIX_GATE_BASELINE_NOT_PROVEN::'+json.dumps(bad,ensure_ascii=False))
    checks.append({'name':'six_gates_pass_baseline','status':'PASS' if not bad else 'FAIL','details':{'gate_states':gate_states}})
    six_gate_baseline=bool(current_truth.get('six_gate_baseline_closure_claim') or residency_summary.get('six_gate_baseline_closure_claim') or residency_report.get('six_gate_baseline_closure_claim'))
    if not six_gate_baseline: errors.append('SIX_GATE_BASELINE_CLOSURE_CLAIM_NOT_TRUE')
    checks.append({'name':'six_gate_baseline_closure_true','status':'PASS' if six_gate_baseline else 'FAIL','details':{'value':six_gate_baseline}})
    organ_assembly_claim=bool(manifest.get('organ_assembly_claim') or current_truth.get('organ_assembly_claim') or residency_report.get('organ_assembly_claim'))
    throne_crown_claim=bool(manifest.get('throne_crown_claim') or current_truth.get('throne_crown_claim') or residency_report.get('throne_crown_claim'))
    if organ_assembly_claim: errors.append('FORBIDDEN_OVERCLAIM::organ_assembly_claim_true')
    if throne_crown_claim: errors.append('FORBIDDEN_OVERCLAIM::throne_crown_claim_true')
    checks.append({'name':'no_organ_assembly_claim','status':'PASS' if not organ_assembly_claim else 'FAIL','details':{'value':organ_assembly_claim}})
    checks.append({'name':'no_throne_crown_claim','status':'PASS' if not throne_crown_claim else 'FAIL','details':{'value':throne_crown_claim}})
    lmm=current_truth.get('local_model_membrane_status') or residency_summary.get('local_model_membrane_status') or residency_report.get('local_model_membrane_status')
    if lmm!='DEFERRED_AFTER_CORE_V1': errors.append(f'LOCAL_MODEL_NOT_DEFERRED::{lmm}')
    checks.append({'name':'local_model_deferred','status':'PASS' if lmm=='DEFERRED_AFTER_CORE_V1' else 'FAIL','details':{'value':lmm}})
    real_exec=int(tool_summary.get('real_execution_enabled_count',-1) if isinstance(tool_summary,dict) else -1)
    if real_exec!=0: errors.append(f'REAL_EXECUTION_ENABLED_NOT_ZERO::{real_exec}')
    checks.append({'name':'real_execution_enabled_zero','status':'PASS' if real_exec==0 else 'FAIL','details':{'value':real_exec}})
    non_current=residency_report.get('non_current_classes') or []
    required_nc={'legacy_history','negative_examples','quarantine_residents','superseded_reports','future_deferred_capabilities'}
    missing_nc=sorted(required_nc-set(non_current))
    if missing_nc: errors.append('NON_CURRENT_CLASSES_MISSING::'+','.join(missing_nc))
    checks.append({'name':'non_current_classes_declared','status':'PASS' if not missing_nc else 'FAIL','details':{'missing':missing_nc,'classes':non_current}})
    validators=personal_registry.get('validators') or personal_registry.get('required_validators') or []
    validator_records=[]
    for entry in validators:
        if isinstance(entry,str): vid,path=entry,entry
        elif isinstance(entry,dict): vid=entry.get('validator_id') or entry.get('id') or entry.get('path'); path=entry.get('path') or entry.get('validator_path') or entry.get('file')
        else: continue
        if not path: continue
        pp=rel(repo,path); exists=pp.exists(); no_chars=False; py_ok=False
        if exists:
            no_chars=not has_control_chars(pp)
            try: py_compile.compile(str(pp),doraise=True); py_ok=True
            except Exception: py_ok=False
        validator_records.append({'validator_id':vid,'path':path,'exists':exists,'no_control_chars':no_chars,'python_compile':py_ok})
    bad_validators=[r for r in validator_records if not r['exists'] or not r['no_control_chars'] or not r['python_compile']]
    if bad_validators: errors.append('PERSONAL_VALIDATOR_PROOF_FAILED')
    checks.append({'name':'personal_validators_present_and_compile','status':'PASS' if not bad_validators else 'FAIL','details':{'count':len(validator_records),'failures':bad_validators}})
    now=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
    custodes_status='PASS_BASELINE_PROSECUTION' if not errors else 'FAIL_CUSTODES_PROSECUTION'
    verdict='PASS_CUSTODES_MECHANICUS_PROSECUTOR_GATE_READY' if not errors else 'FAIL_CUSTODES_MECHANICUS_PROSECUTOR_GATE'
    findings=[
        {'finding_id':'MECH_IDENTITY_AND_FUNCTIONS_BOUND','status':'PASS' if gate_states.get('G1_IDENTITY_MANIFEST')=='PASS_BASELINE' and gate_states.get('G2_FUNCTIONS_REGISTRY')=='PASS_BASELINE' else 'FAIL'},
        {'finding_id':'MECH_CAPABILITIES_EVIDENCE_BOUND','status':'PASS' if gate_states.get('G3_CAPABILITY_EVIDENCE')=='PASS_BASELINE' else 'FAIL'},
        {'finding_id':'MECH_PERSONAL_VALIDATORS_BASELINE_PRESENT','status':'PASS' if not bad_validators else 'FAIL'},
        {'finding_id':'MECH_CURRENT_TRUTH_INDEX_PRESENT','status':'PASS' if bool(indexed_records) else 'FAIL'},
        {'finding_id':'MECH_RESIDENCY_NON_CURRENT_CLASSES_BOUNDED','status':'PASS' if not missing_nc else 'FAIL'},
        {'finding_id':'MECH_NO_REAL_EXECUTION_ENABLED','status':'PASS' if real_exec==0 else 'FAIL'},
        {'finding_id':'MECH_NO_THRONE_OR_ASSEMBLY_OVERCLAIM','status':'PASS' if not organ_assembly_claim and not throne_crown_claim else 'FAIL'},]
    report={'task_id':PATCH_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'generated_at_utc':now,'target_organ_id':'MECHANICUS','custodes_prosecution_status':custodes_status,'mechanicus_six_gate_baseline_status':'PASS_BASELINE' if not bad else 'NOT_PROVEN','six_gate_baseline_closure_claim':six_gate_baseline,'pass_baseline_gate_count':sum(1 for gid in required_gate_ids if gate_states.get(gid)=='PASS_BASELINE'),'real_execution_enabled_count':real_exec,'local_model_membrane_status':lmm,'organ_assembly_claim':False,'throne_crown_claim':False,'next_gate_count':1,'next_gate_work':['THRONE-MECHANICUS-SIX-GATE-CROWN-VERDICT-0001'],'gate_states':gate_states,'validator_records':validator_records,'non_current_classes':non_current,'prosecutor_findings':findings,'errors':errors,'warnings':['Custodes prosecution accepts Mechanicus six-gate baseline only; it does not crown Mechanicus.','Throne crown verdict remains future work.','Local model membrane and real execution gateway remain deferred/not ready.'] if not errors else warnings}
    summary={'task_id':PATCH_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'generated_at_utc':now,'target_organ_id':'MECHANICUS','custodes_prosecution_status':custodes_status,'mechanicus_six_gate_baseline_status':report['mechanicus_six_gate_baseline_status'],'pass_baseline_gate_count':report['pass_baseline_gate_count'],'real_execution_enabled_count':real_exec,'personal_validator_record_count':len(validator_records),'local_model_membrane_status':lmm,'organ_assembly_claim':False,'throne_crown_claim':False,'next_gate_count':1}
    receipt=dict(summary); receipt.update({'receipt':'ORGANS/CUSTODES/RECEIPTS/custodes_mechanicus_prosecutor_gate_receipt.json','summary':'ORGANS/CUSTODES/REPORTS/CUSTODES_MECHANICUS_PROSECUTOR_GATE_SUMMARY_V0_1.json','report_json':'ORGANS/CUSTODES/REPORTS/CUSTODES_MECHANICUS_PROSECUTOR_GATE_REPORT_V0_1.json','report_md':'ORGANS/CUSTODES/REPORTS/CUSTODES_MECHANICUS_PROSECUTOR_GATE_REPORT_V0_1.md','errors':errors,'warnings':report['warnings']})
    for p,data in {'ORGANS/CUSTODES/RECEIPTS/custodes_mechanicus_prosecutor_gate_receipt.json':receipt,'ORGANS/CUSTODES/REPORTS/CUSTODES_MECHANICUS_PROSECUTOR_GATE_SUMMARY_V0_1.json':summary,'ORGANS/CUSTODES/REPORTS/CUSTODES_MECHANICUS_PROSECUTOR_GATE_REPORT_V0_1.json':report}.items():
        pp=rel(repo,p); pp.parent.mkdir(parents=True,exist_ok=True); pp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    md=f"""# CUSTODES MECHANICUS PROSECUTOR GATE V0.1\n\n- task_id: `{PATCH_ID}`\n- verdict: `{verdict}`\n- target_organ_id: `MECHANICUS`\n- custodes_prosecution_status: `{custodes_status}`\n- pass_baseline_gate_count: `{report['pass_baseline_gate_count']}`\n- real_execution_enabled_count: `{real_exec}`\n- local_model_membrane_status: `{lmm}`\n- organ_assembly_claim: `false`\n- throne_crown_claim: `false`\n\n## Findings\n\n"""
    for f in findings: md += f"- {f['finding_id']}: {f['status']}\n"
    md += "\n## Warnings\n\n" + "\n".join(f"- {w}" for w in report['warnings']) + "\n"
    rel(repo,'ORGANS/CUSTODES/REPORTS/CUSTODES_MECHANICUS_PROSECUTOR_GATE_REPORT_V0_1.md').write_text(md,encoding='utf-8')
    result=dict(receipt); result['checks']=checks+[{'name':'custodes_prosecution_status_pass','status':'PASS' if custodes_status=='PASS_BASELINE_PROSECUTION' else 'FAIL','details':{'value':custodes_status}},{'name':'next_gate_throne_pending','status':'PASS','details':{'next_gate':'THRONE-MECHANICUS-SIX-GATE-CROWN-VERDICT-0001'}}]
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
