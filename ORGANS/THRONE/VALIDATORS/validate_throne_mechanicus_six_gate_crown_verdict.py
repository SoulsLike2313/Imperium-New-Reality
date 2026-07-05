from __future__ import annotations
import argparse, json, os, subprocess, sys, re, py_compile
from pathlib import Path

PATCH_ID = 'THRONE-MECHANICUS-SIX-GATE-CROWN-VERDICT-0001'
VALIDATOR_ID = 'throne_mechanicus_six_gate_crown_verdict_validator.v0_1'
CONTROL_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
REQUIRED_STATIC = [
    'ORGANS/MECHANICUS/MANIFEST.json',
    'ORGANS/MECHANICUS/MATRICES/MECHANICUS_CURRENT_TRUTH_INDEX_V0_1.json',
    'ORGANS/CUSTODES/REPORTS/CUSTODES_MECHANICUS_PROSECUTOR_GATE_SUMMARY_V0_1.json',
    'ORGANS/CUSTODES/REPORTS/CUSTODES_MECHANICUS_PROSECUTOR_GATE_REPORT_V0_1.json',
    'ORGANS/CUSTODES/RECEIPTS/custodes_mechanicus_prosecutor_gate_receipt.json',
    'ORGANS/MECHANICUS/REPORTS/MECHANICUS_RESIDENCY_TRUST_GATE_REPORT_V0_1.json',
    'ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_ADMISSION_V2_SUMMARY_V0_1.json',
    'ORGANS/THRONE/LAWS/THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_LAW_V0_1.json',
    'ORGANS/THRONE/MATRICES/THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_MATRIX_V0_1.json',
    'ORGANS/THRONE/TOOLS/build_throne_mechanicus_six_gate_crown_verdict.py',
    'ORGANS/THRONE/VALIDATORS/validate_throne_mechanicus_six_gate_crown_verdict.py'
]
GENERATED = [
    'ORGANS/THRONE/RECEIPTS/throne_mechanicus_six_gate_crown_verdict_receipt.json',
    'ORGANS/THRONE/REPORTS/THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_SUMMARY_V0_1.json',
    'ORGANS/THRONE/REPORTS/THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_REPORT_V0_1.json',
    'ORGANS/THRONE/REPORTS/THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_REPORT_V0_1.md'
]

def rel(repo: Path, p: str) -> Path:
    return repo / p.replace('/', os.sep)

def no_control_chars(path: Path):
    if not path.exists():
        return []
    return [{'index': m.start(), 'codepoint': ord(m.group(0))} for m in CONTROL_RE.finditer(path.read_text(encoding='utf-8', errors='replace'))]

def read_json(repo: Path, p: str):
    return json.loads(rel(repo, p).read_text(encoding='utf-8'))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root', default='.')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()
    errors = []
    warnings = []
    checks = []
    if args.apply:
        patch_files = repo / 'WARP' / 'PATCHES' / PATCH_ID / 'FILES_TO_LAND'
        if not patch_files.exists():
            print(json.dumps({'task_id': PATCH_ID, 'validator_id': VALIDATOR_ID, 'verdict': 'FAIL', 'errors': [f'MISSING_FILES_TO_LAND::{patch_files}']}, ensure_ascii=False, indent=2))
            return 1
        for src in patch_files.rglob('*'):
            if src.is_file():
                dst = repo / src.relative_to(patch_files)
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(src.read_bytes())
    for p in REQUIRED_STATIC:
        pp = rel(repo, p)
        exists = pp.exists()
        checks.append({'name': f'exists::{p}', 'status': 'PASS' if exists else 'FAIL', 'details': {'path': p}})
        if not exists:
            errors.append(f'MISSING_REQUIRED_STATIC::{p}')
            continue
        hits = no_control_chars(pp)
        checks.append({'name': f'no_control_chars::{p}', 'status': 'PASS' if not hits else 'FAIL', 'details': {'hits': hits}})
        if hits:
            errors.append(f'CONTROL_CHARS::{p}')
        if p.endswith('.json'):
            try:
                read_json(repo, p)
                checks.append({'name': f'json_parse::{p}', 'status': 'PASS', 'details': {}})
            except Exception as e:
                errors.append(f'JSON_PARSE_ERROR::{p}::{e}')
                checks.append({'name': f'json_parse::{p}', 'status': 'FAIL', 'details': {'error': str(e)}})
        if p.endswith('.py'):
            try:
                py_compile.compile(str(pp), doraise=True)
                checks.append({'name': f'py_compile::{p}', 'status': 'PASS', 'details': {}})
            except Exception as e:
                errors.append(f'PY_COMPILE_ERROR::{p}::{e}')
                checks.append({'name': f'py_compile::{p}', 'status': 'FAIL', 'details': {'error': str(e)}})
    if not errors:
        proc = subprocess.run([sys.executable, str(rel(repo, 'ORGANS/THRONE/TOOLS/build_throne_mechanicus_six_gate_crown_verdict.py')), '--repo-root', str(repo)], text=True, capture_output=True)
        if proc.returncode != 0:
            errors.append('BUILDER_FAILED')
            try:
                detail = json.loads(proc.stdout)
            except Exception:
                detail = {'stdout': proc.stdout, 'stderr': proc.stderr}
            checks.append({'name': 'builder_runs', 'status': 'FAIL', 'details': detail})
        else:
            checks.append({'name': 'builder_runs', 'status': 'PASS', 'details': json.loads(proc.stdout)})
    generated_ok = True
    for p in GENERATED:
        exists = rel(repo, p).exists()
        checks.append({'name': f'generated::{p}', 'status': 'PASS' if exists else 'FAIL', 'details': {'path': p}})
        if not exists:
            generated_ok = False
            errors.append(f'MISSING_GENERATED::{p}')
    if generated_ok:
        try:
            summary = read_json(repo, 'ORGANS/THRONE/REPORTS/THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_SUMMARY_V0_1.json')
            report = read_json(repo, 'ORGANS/THRONE/REPORTS/THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_REPORT_V0_1.json')
            manifest = read_json(repo, 'ORGANS/MECHANICUS/MANIFEST.json')
            truth = read_json(repo, 'ORGANS/MECHANICUS/MATRICES/MECHANICUS_CURRENT_TRUTH_INDEX_V0_1.json')
            checks.append({'name': 'summary_verdict_pass', 'status': 'PASS' if summary.get('verdict') == 'PASS_THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_READY' else 'FAIL', 'details': {'verdict': summary.get('verdict')}})
            checks.append({'name': 'throne_crown_status_pass', 'status': 'PASS' if report.get('throne_crown_status') == 'PASS_BASELINE_CROWN_VERDICT' else 'FAIL', 'details': {'value': report.get('throne_crown_status')}})
            checks.append({'name': 'mechanicus_baseline_assembled', 'status': 'PASS' if report.get('mechanicus_assembly_status') == 'ASSEMBLED_BASELINE_THRONE_CROWNED_NOT_CORE_V1_COMPLETE' else 'FAIL', 'details': {'value': report.get('mechanicus_assembly_status')}})
            checks.append({'name': 'six_gates_pass_baseline', 'status': 'PASS' if report.get('pass_baseline_gate_count') == 6 else 'FAIL', 'details': {'count': report.get('pass_baseline_gate_count')}})
            checks.append({'name': 'custodes_prosecution_pass', 'status': 'PASS' if report.get('custodes_prosecution_status') == 'PASS_BASELINE_PROSECUTION' else 'FAIL', 'details': {'value': report.get('custodes_prosecution_status')}})
            checks.append({'name': 'real_execution_enabled_zero', 'status': 'PASS' if report.get('real_execution_enabled_count') == 0 else 'FAIL', 'details': {'value': report.get('real_execution_enabled_count')}})
            checks.append({'name': 'local_model_deferred', 'status': 'PASS' if report.get('local_model_membrane_status') == 'DEFERRED_AFTER_CORE_V1' else 'FAIL', 'details': {'value': report.get('local_model_membrane_status')}})
            checks.append({'name': 'core_v1_not_claimed', 'status': 'PASS' if report.get('core_v1_complete_claim') is False else 'FAIL', 'details': {'value': report.get('core_v1_complete_claim')}})
            checks.append({'name': 'manifest_throne_crowned', 'status': 'PASS' if manifest.get('throne_crown_status') == 'PASS_BASELINE_CROWN_VERDICT' else 'FAIL', 'details': {'value': manifest.get('throne_crown_status')}})
            checks.append({'name': 'current_truth_throne_crowned', 'status': 'PASS' if truth.get('throne_crown_status') == 'PASS_BASELINE_CROWN_VERDICT' else 'FAIL', 'details': {'value': truth.get('throne_crown_status')}})
            if summary.get('verdict') != 'PASS_THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_READY': errors.append('SUMMARY_VERDICT_NOT_PASS')
            if report.get('throne_crown_status') != 'PASS_BASELINE_CROWN_VERDICT': errors.append('THRONE_CROWN_STATUS_NOT_PASS')
            if report.get('mechanicus_assembly_status') != 'ASSEMBLED_BASELINE_THRONE_CROWNED_NOT_CORE_V1_COMPLETE': errors.append('MECHANICUS_ASSEMBLY_STATUS_NOT_BASELINE')
            if report.get('pass_baseline_gate_count') != 6: errors.append('SIX_GATES_NOT_PASS_BASELINE')
            if report.get('custodes_prosecution_status') != 'PASS_BASELINE_PROSECUTION': errors.append('CUSTODES_PROSECUTION_NOT_PASS')
            if report.get('real_execution_enabled_count') != 0: errors.append('REAL_EXECUTION_ENABLED_NOT_ALLOWED')
            if report.get('local_model_membrane_status') != 'DEFERRED_AFTER_CORE_V1': errors.append('LOCAL_MODEL_NOT_DEFERRED')
            if report.get('core_v1_complete_claim') is not False: errors.append('CORE_V1_OVERCLAIM')
        except Exception as e:
            errors.append(f'GENERATED_JSON_CHECK_ERROR::{e}')
    verdict = 'PASS_THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_READY' if not errors else 'FAIL_THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT'
    print(json.dumps({
        'task_id': PATCH_ID,
        'validator_id': VALIDATOR_ID,
        'verdict': verdict,
        'receipt': 'ORGANS/THRONE/RECEIPTS/throne_mechanicus_six_gate_crown_verdict_receipt.json',
        'summary': 'ORGANS/THRONE/REPORTS/THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_SUMMARY_V0_1.json',
        'report_json': 'ORGANS/THRONE/REPORTS/THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_REPORT_V0_1.json',
        'report_md': 'ORGANS/THRONE/REPORTS/THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_REPORT_V0_1.md',
        'errors': errors,
        'warnings': warnings,
        'checks': checks
    }, ensure_ascii=False, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
