
from __future__ import annotations
import argparse, json, py_compile, subprocess, sys
from pathlib import Path

PATCH_ID = 'MECHANICUS-RESIDENCY-TRUST-GATE-0001'
VALIDATOR_ID = 'mechanicus_residency_trust_gate_validator.v0_1'
REQUIRED = [
 'ORGANS/MECHANICUS/MANIFEST.json',
 'ORGANS/MECHANICUS/LAWS/MECHANICUS_RESIDENCY_TRUST_GATE_LAW_V0_1.json',
 'ORGANS/MECHANICUS/MATRICES/MECHANICUS_RESIDENCY_TRUST_REGISTRY_V0_1.json',
 'ORGANS/MECHANICUS/MATRICES/MECHANICUS_RESIDENCY_TRUST_GATE_MATRIX_V0_1.json',
 'ORGANS/MECHANICUS/MATRICES/MECHANICUS_CURRENT_TRUTH_INDEX_V0_1.json',
 'ORGANS/MECHANICUS/TOOLS/build_mechanicus_residency_trust_gate.py',
 'ORGANS/MECHANICUS/VALIDATORS/validate_mechanicus_residency_trust_gate.py',
 'ORGANS/CUSTODES/MATRICES/CUSTODES_MECHANICUS_RESIDENCY_TRUST_GATE_PROSECUTOR_MATRIX_V0_1.json',
 'ORGANS/THRONE/MATRICES/THRONE_MECHANICUS_RESIDENCY_TRUST_GATE_CROWN_MATRIX_V0_1.json',
]
JSONS = [p for p in REQUIRED if p.endswith('.json')]
PYS = [p for p in REQUIRED if p.endswith('.py')]
GENERATED = [
 'ORGANS/MECHANICUS/RECEIPTS/mechanicus_residency_trust_gate_receipt.json',
 'ORGANS/MECHANICUS/REPORTS/MECHANICUS_RESIDENCY_TRUST_GATE_SUMMARY_V0_1.json',
 'ORGANS/MECHANICUS/REPORTS/MECHANICUS_RESIDENCY_TRUST_GATE_REPORT_V0_1.json',
 'ORGANS/MECHANICUS/REPORTS/MECHANICUS_RESIDENCY_TRUST_GATE_REPORT_V0_1.md',
]

def control_hits(path: Path):
    data = path.read_bytes()
    hits=[]
    for i,b in enumerate(data):
        if b < 32 and b not in (9,10,13):
            hits.append({'offset':i,'byte':b})
            if len(hits)>20: break
    return hits

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root', default='.')
    ns = ap.parse_args()
    root = Path(ns.repo_root).resolve()
    checks=[]; errors=[]; warnings=[]
    def check(name, status, details=None):
        checks.append({'name':name,'status':'PASS' if status else 'FAIL','details':details or {}})
        if not status:
            errors.append({'check':name, 'details':details or {}})
    for rel in REQUIRED:
        p=root/rel
        check('exists::'+rel, p.exists(), {'path':rel})
        if p.exists():
            hits=control_hits(p)
            check('no_control_chars::'+rel, not hits, {'hits':hits})
    for rel in JSONS:
        p=root/rel
        if p.exists():
            try:
                json.loads(p.read_text(encoding='utf-8'))
                check('json_parse::'+rel, True)
            except Exception as e:
                check('json_parse::'+rel, False, {'error':str(e)})
    for rel in PYS:
        p=root/rel
        if p.exists():
            try:
                py_compile.compile(str(p), doraise=True)
                check('py_compile::'+rel, True)
            except Exception as e:
                check('py_compile::'+rel, False, {'error':str(e)})
    if not errors:
        proc = subprocess.run([sys.executable, str(root/'ORGANS/MECHANICUS/TOOLS/build_mechanicus_residency_trust_gate.py'), '--repo-root', str(root)], text=True, capture_output=True)
        try:
            built=json.loads(proc.stdout)
        except Exception:
            built={'verdict':'BUILDER_OUTPUT_PARSE_FAIL','stdout':proc.stdout,'stderr':proc.stderr}
        check('builder_runs', proc.returncode == 0 and built.get('verdict') == 'PASS_MECHANICUS_RESIDENCY_TRUST_GATE_READY', built)
    for rel in GENERATED:
        p=root/rel
        check('generated::'+rel, p.exists(), {'path':rel})
    if (root/'ORGANS/MECHANICUS/REPORTS/MECHANICUS_RESIDENCY_TRUST_GATE_SUMMARY_V0_1.json').exists():
        summary=json.loads((root/'ORGANS/MECHANICUS/REPORTS/MECHANICUS_RESIDENCY_TRUST_GATE_SUMMARY_V0_1.json').read_text(encoding='utf-8'))
        check('summary_verdict_pass', summary.get('verdict')=='PASS_MECHANICUS_RESIDENCY_TRUST_GATE_READY', {'verdict':summary.get('verdict')})
        check('g6_status_pass_baseline', summary.get('residency_trust_gate_status')=='PASS_BASELINE', {'value':summary.get('residency_trust_gate_status')})
        check('six_pass_baseline_gates', summary.get('pass_baseline_gate_count')==6, {'count':summary.get('pass_baseline_gate_count')})
        check('six_gate_baseline_closure_claim', summary.get('six_gate_baseline_closure_claim') is True, {'value':summary.get('six_gate_baseline_closure_claim')})
        check('no_organ_assembly_claim', summary.get('organ_assembly_claim') is False, {'value':summary.get('organ_assembly_claim')})
        check('no_custodes_prosecution_claim', summary.get('custodes_prosecution_claim') is False, {'value':summary.get('custodes_prosecution_claim')})
        check('no_throne_crown_claim', summary.get('throne_crown_claim') is False, {'value':summary.get('throne_crown_claim')})
        check('local_model_deferred', summary.get('local_model_membrane_status')=='DEFERRED_AFTER_CORE_V1', {'value':summary.get('local_model_membrane_status')})
    verdict = 'PASS_MECHANICUS_RESIDENCY_TRUST_GATE_READY' if not errors else 'FAIL_MECHANICUS_RESIDENCY_TRUST_GATE'
    result={
        'task_id':PATCH_ID,
        'validator_id':VALIDATOR_ID,
        'verdict':verdict,
        'receipt':'ORGANS/MECHANICUS/RECEIPTS/mechanicus_residency_trust_gate_receipt.json',
        'summary':'ORGANS/MECHANICUS/REPORTS/MECHANICUS_RESIDENCY_TRUST_GATE_SUMMARY_V0_1.json',
        'report_json':'ORGANS/MECHANICUS/REPORTS/MECHANICUS_RESIDENCY_TRUST_GATE_REPORT_V0_1.json',
        'report_md':'ORGANS/MECHANICUS/REPORTS/MECHANICUS_RESIDENCY_TRUST_GATE_REPORT_V0_1.md',
        'errors':errors,
        'warnings':warnings,
        'checks':checks,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith('PASS') else 1
if __name__ == '__main__':
    raise SystemExit(main())
