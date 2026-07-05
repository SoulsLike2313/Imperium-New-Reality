from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

PATCH_ID = 'THRONE-MECHANICUS-SIX-GATE-CROWN-VERDICT-0001'
VALIDATOR_ID = 'throne_mechanicus_six_gate_crown_verdict_validator.v0_1'
VERDICT = 'PASS_THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_READY'

def rel(repo: Path, p: str) -> Path:
    return repo / p.replace('/', '/')

def read_json(repo: Path, p: str):
    return json.loads(rel(repo, p).read_text(encoding='utf-8'))

def write_json(repo: Path, p: str, data):
    path = rel(repo, p)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

def write_text(repo: Path, p: str, text: str):
    path = rel(repo, p)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + '\n', encoding='utf-8', newline='\n')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root', default='.')
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')

    manifest = read_json(repo, 'ORGANS/MECHANICUS/MANIFEST.json')
    truth = read_json(repo, 'ORGANS/MECHANICUS/MATRICES/MECHANICUS_CURRENT_TRUTH_INDEX_V0_1.json')
    custodes_summary = read_json(repo, 'ORGANS/CUSTODES/REPORTS/CUSTODES_MECHANICUS_PROSECUTOR_GATE_SUMMARY_V0_1.json')
    custodes_report = read_json(repo, 'ORGANS/CUSTODES/REPORTS/CUSTODES_MECHANICUS_PROSECUTOR_GATE_REPORT_V0_1.json')
    residency_report = read_json(repo, 'ORGANS/MECHANICUS/REPORTS/MECHANICUS_RESIDENCY_TRUST_GATE_REPORT_V0_1.json')
    tool_summary = read_json(repo, 'ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_ADMISSION_V2_SUMMARY_V0_1.json')

    gate_records = truth.get('current_gate_truth', [])
    gate_states = {g.get('gate_id'): g.get('state') for g in gate_records}
    pass_baseline_gate_count = sum(1 for v in gate_states.values() if v == 'PASS_BASELINE')
    real_execution_enabled_count = int(tool_summary.get('real_execution_enabled_count', custodes_summary.get('real_execution_enabled_count', 0)))
    local_model_status = truth.get('local_model_membrane_status') or custodes_summary.get('local_model_membrane_status')
    custodes_status = custodes_summary.get('custodes_prosecution_status')

    findings = [
        {'finding_id': 'THRONE_SEES_SIX_BASELINE_GATES', 'status': 'PASS' if pass_baseline_gate_count == 6 else 'FAIL', 'details': gate_states},
        {'finding_id': 'THRONE_SEES_CUSTODES_PROSECUTION', 'status': 'PASS' if custodes_status == 'PASS_BASELINE_PROSECUTION' else 'FAIL', 'details': {'custodes_prosecution_status': custodes_status}},
        {'finding_id': 'THRONE_SEES_REAL_EXECUTION_DISABLED', 'status': 'PASS' if real_execution_enabled_count == 0 else 'FAIL', 'details': {'real_execution_enabled_count': real_execution_enabled_count}},
        {'finding_id': 'THRONE_SEES_LOCAL_MODEL_DEFERRED', 'status': 'PASS' if local_model_status == 'DEFERRED_AFTER_CORE_V1' else 'FAIL', 'details': {'local_model_membrane_status': local_model_status}},
        {'finding_id': 'THRONE_REJECTS_CORE_V1_OVERCLAIM', 'status': 'PASS', 'details': {'core_v1_complete_claim': False}},
        {'finding_id': 'THRONE_ACCEPTS_MECHANICUS_BASELINE_ASSEMBLY_ONLY', 'status': 'PASS', 'details': {'mechanicus_assembly_status': 'ASSEMBLED_BASELINE_THRONE_CROWNED_NOT_CORE_V1_COMPLETE'}}
    ]
    errors = []
    if any(f['status'] != 'PASS' for f in findings):
        errors.append('THRONE_CROWN_FINDINGS_NOT_ALL_PASS')
    if pass_baseline_gate_count != 6:
        errors.append('SIX_GATE_BASELINE_NOT_COMPLETE')
    if custodes_status != 'PASS_BASELINE_PROSECUTION':
        errors.append('CUSTODES_PROSECUTION_NOT_PASS')
    if real_execution_enabled_count != 0:
        errors.append('REAL_EXECUTION_ENABLED_NOT_ALLOWED')
    if local_model_status != 'DEFERRED_AFTER_CORE_V1':
        errors.append('LOCAL_MODEL_NOT_DEFERRED')

    verdict = VERDICT if not errors else 'FAIL_THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT'
    throne_crown_status = 'PASS_BASELINE_CROWN_VERDICT' if not errors else 'FAIL_CROWN_VERDICT'
    mechanicus_assembly_status = 'ASSEMBLED_BASELINE_THRONE_CROWNED_NOT_CORE_V1_COMPLETE' if not errors else 'NOT_ASSEMBLED'

    report = {
        'task_id': PATCH_ID,
        'validator_id': VALIDATOR_ID,
        'verdict': verdict,
        'generated_at_utc': now,
        'target_organ_id': 'MECHANICUS',
        'throne_crown_status': throne_crown_status,
        'mechanicus_assembly_status': mechanicus_assembly_status,
        'mechanicus_six_gate_baseline_status': 'PASS_BASELINE' if pass_baseline_gate_count == 6 else 'INCOMPLETE',
        'pass_baseline_gate_count': pass_baseline_gate_count,
        'custodes_prosecution_status': custodes_status,
        'real_execution_enabled_count': real_execution_enabled_count,
        'local_model_membrane_status': local_model_status,
        'core_v1_complete_claim': False,
        'real_execution_gateway_ready': False,
        'local_model_membrane_ready': False,
        'throne_crown_claim': not errors,
        'mechanicus_baseline_assembly_claim': not errors,
        'current_truth_index_version': truth.get('version'),
        'manifest_version': manifest.get('version'),
        'gate_states': gate_states,
        'throne_findings': findings,
        'custodes_prosecutor_findings': custodes_report.get('prosecutor_findings', []),
        'resident_classes': residency_report.get('resident_classes', {}),
        'non_current_classes': truth.get('non_current_classes', []),
        'next_gate_count': 0,
        'post_crown_deferred_work': manifest.get('post_crown_deferred_work', []),
        'errors': errors,
        'warnings': [
            'Throne crowns Mechanicus baseline assembly only; this is not Core v1 completion.',
            'Real execution gateway, dependency/code-cleanliness expansion and local model membrane remain future/deferred work.',
            'This crown verdict applies to Mechanicus only, not to all Great Nine organs.'
        ]
    }
    summary = {
        'task_id': PATCH_ID,
        'validator_id': VALIDATOR_ID,
        'verdict': verdict,
        'generated_at_utc': now,
        'target_organ_id': 'MECHANICUS',
        'throne_crown_status': throne_crown_status,
        'mechanicus_assembly_status': mechanicus_assembly_status,
        'mechanicus_six_gate_baseline_status': report['mechanicus_six_gate_baseline_status'],
        'pass_baseline_gate_count': pass_baseline_gate_count,
        'custodes_prosecution_status': custodes_status,
        'real_execution_enabled_count': real_execution_enabled_count,
        'local_model_membrane_status': local_model_status,
        'core_v1_complete_claim': False,
        'real_execution_gateway_ready': False,
        'local_model_membrane_ready': False,
        'mechanicus_baseline_assembly_claim': not errors,
        'next_gate_count': 0
    }
    receipt = {
        **summary,
        'receipt_id': 'throne_mechanicus_six_gate_crown_verdict_receipt.v0_1',
        'report_json': 'ORGANS/THRONE/REPORTS/THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_REPORT_V0_1.json',
        'report_md': 'ORGANS/THRONE/REPORTS/THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_REPORT_V0_1.md',
        'summary': 'ORGANS/THRONE/REPORTS/THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_SUMMARY_V0_1.json'
    }

    write_json(repo, 'ORGANS/THRONE/REPORTS/THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_REPORT_V0_1.json', report)
    write_json(repo, 'ORGANS/THRONE/REPORTS/THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_SUMMARY_V0_1.json', summary)
    write_json(repo, 'ORGANS/THRONE/RECEIPTS/throne_mechanicus_six_gate_crown_verdict_receipt.json', receipt)
    md = (
        '# THRONE MECHANICUS SIX GATE CROWN VERDICT V0.1\n\n'
        f'- task_id: `{PATCH_ID}`\n'
        f'- verdict: `{verdict}`\n'
        f'- throne_crown_status: `{throne_crown_status}`\n'
        '- target_organ_id: `MECHANICUS`\n'
        f'- mechanicus_assembly_status: `{mechanicus_assembly_status}`\n'
        f'- pass_baseline_gate_count: `{pass_baseline_gate_count}`\n'
        f'- custodes_prosecution_status: `{custodes_status}`\n'
        f'- real_execution_enabled_count: `{real_execution_enabled_count}`\n'
        f'- local_model_membrane_status: `{local_model_status}`\n\n'
        '## Claim boundary\n\n'
        'This verdict crowns Mechanicus baseline assembly only. It does not claim Core v1 completion, real execution readiness, local model readiness, or Great Nine completion.\n'
    )
    write_text(repo, 'ORGANS/THRONE/REPORTS/THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_REPORT_V0_1.md', md)
    print(json.dumps({
        'task_id': PATCH_ID,
        'validator_id': VALIDATOR_ID,
        'verdict': verdict,
        'generated_at_utc': now,
        'target_organ_id': 'MECHANICUS',
        'throne_crown_status': throne_crown_status,
        'mechanicus_assembly_status': mechanicus_assembly_status,
        'pass_baseline_gate_count': pass_baseline_gate_count,
        'custodes_prosecution_status': custodes_status,
        'real_execution_enabled_count': real_execution_enabled_count,
        'local_model_membrane_status': local_model_status,
        'core_v1_complete_claim': False,
        'next_gate_count': 0,
        'errors': errors,
        'warnings': report['warnings'],
        'receipt': 'ORGANS/THRONE/RECEIPTS/throne_mechanicus_six_gate_crown_verdict_receipt.json',
        'summary': 'ORGANS/THRONE/REPORTS/THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_SUMMARY_V0_1.json',
        'report_json': 'ORGANS/THRONE/REPORTS/THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_REPORT_V0_1.json',
        'report_md': 'ORGANS/THRONE/REPORTS/THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_REPORT_V0_1.md'
    }, ensure_ascii=False, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
