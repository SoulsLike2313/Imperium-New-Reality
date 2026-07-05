#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from datetime import datetime, timezone

PATCH_ID = "MECHANICUS-CURRENT-TRUTH-RECEIPTS-GATE-0001"
VALIDATOR_ID = "mechanicus_current_truth_receipts_gate_validator.v0_1"
GATE_ID = "G5_CURRENT_TRUTH_RECEIPTS"

INDEX = "ORGANS/MECHANICUS/MATRICES/MECHANICUS_CURRENT_TRUTH_INDEX_V0_1.json"
MATRIX = "ORGANS/MECHANICUS/MATRICES/MECHANICUS_CURRENT_TRUTH_RECEIPTS_GATE_MATRIX_V0_1.json"
MANIFEST = "ORGANS/MECHANICUS/MANIFEST.json"
RECEIPT = "ORGANS/MECHANICUS/RECEIPTS/mechanicus_current_truth_receipts_gate_receipt.json"
SUMMARY = "ORGANS/MECHANICUS/REPORTS/MECHANICUS_CURRENT_TRUTH_RECEIPTS_GATE_SUMMARY_V0_1.json"
REPORT_JSON = "ORGANS/MECHANICUS/REPORTS/MECHANICUS_CURRENT_TRUTH_RECEIPTS_GATE_REPORT_V0_1.json"
REPORT_MD = "ORGANS/MECHANICUS/REPORTS/MECHANICUS_CURRENT_TRUTH_RECEIPTS_GATE_REPORT_V0_1.md"

PASS_STATES = {"PASS_BASELINE"}
FORBIDDEN_CLAIMS = {"MECHANICUS_ASSEMBLED", "SIX_GATES_100_PERCENT_CLOSED", "CUSTODES_AUDIT_DONE", "THRONE_CROWN_DONE"}

def relpath(repo: Path, rel: str) -> Path:
    return repo / rel

def read_json(repo: Path, rel: str):
    with relpath(repo, rel).open('r', encoding='utf-8') as f:
        return json.load(f)

def write_json(repo: Path, rel: str, data):
    p = relpath(repo, rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def has_control_chars(path: Path) -> list[dict]:
    if not path.exists() or path.is_dir():
        return []
    hits = []
    data = path.read_bytes()
    for i, b in enumerate(data):
        if b in (9, 10, 13):
            continue
        if b < 32:
            hits.append({'offset': i, 'byte': b})
            if len(hits) >= 10:
                break
    return hits

def parse_artifact(repo: Path, rel: str, errors: list, checks: list):
    p = relpath(repo, rel)
    exists = p.exists()
    checks.append({'name': f'exists::{rel}', 'status': 'PASS' if exists else 'FAIL', 'details': {'path': rel}})
    if not exists:
        errors.append({'error': 'MISSING_INDEXED_ARTIFACT', 'path': rel})
        return None
    hits = has_control_chars(p)
    checks.append({'name': f'no_control_chars::{rel}', 'status': 'PASS' if not hits else 'FAIL', 'details': {'hits': hits}})
    if hits:
        errors.append({'error': 'CONTROL_CHARS_IN_INDEXED_ARTIFACT', 'path': rel, 'hits': hits})
    if rel.lower().endswith('.json'):
        try:
            data = read_json(repo, rel)
            checks.append({'name': f'json_parse::{rel}', 'status': 'PASS', 'details': {}})
            return data
        except Exception as e:
            checks.append({'name': f'json_parse::{rel}', 'status': 'FAIL', 'details': {'error': str(e)}})
            errors.append({'error': 'JSON_PARSE_ERROR', 'path': rel, 'message': str(e)})
            return None
    return None

def build(repo: Path) -> dict:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    errors = []
    warnings = [
        'This patch closes Current Truth / Receipts baseline only; it does not assemble Mechanicus.',
        'Residency/trust, Custodes prosecution and Throne crown gates remain future work.',
        'Historical and negative-example artifacts remain non-current unless promoted by index.'
    ]
    checks = []

    index = parse_artifact(repo, INDEX, errors, checks)
    matrix = parse_artifact(repo, MATRIX, errors, checks)
    manifest = parse_artifact(repo, MANIFEST, errors, checks)
    if not index:
        index = {'current_gate_truth': [], 'current_supporting_truth': []}
    if not matrix:
        matrix = {'six_gate_progress_after_pass': []}

    current_gate_truth = index.get('current_gate_truth', []) or []
    supporting_truth = index.get('current_supporting_truth', []) or []
    indexed_records = []
    receipt_records = []
    parse_records = []

    pass_baseline_gate_count = 0
    not_proven_gate_count = 0
    missing_receipt_count = 0
    missing_report_count = 0
    malformed_current_truth_count = 0
    indexed_json_parse_count = 0

    for item in current_gate_truth:
        gate_id = item.get('gate_id')
        state = item.get('state')
        if state in PASS_STATES:
            pass_baseline_gate_count += 1
        if state == 'NOT_PROVEN':
            not_proven_gate_count += 1
        record = {'gate_id': gate_id, 'state': state, 'closure_claim': item.get('closure_claim'), 'source_patch_id': item.get('source_patch_id')}
        for field in ('summary_path','report_path','receipt_path'):
            rel = item.get(field)
            record[field] = rel
            if state in PASS_STATES and not rel:
                malformed_current_truth_count += 1
                errors.append({'error': 'PASS_GATE_MISSING_INDEX_FIELD', 'gate_id': gate_id, 'field': field})
                continue
            if rel:
                # The current patch lists its own outputs in the index as future generated outputs.
                # They must be generated by this builder, not pre-exist before the builder runs.
                is_self_output = item.get('source_patch_id') == PATCH_ID and rel in {SUMMARY, REPORT_JSON, RECEIPT}
                if is_self_output:
                    checks.append({'name': f'self_output_declared::{rel}', 'status': 'PASS', 'details': {'path': rel}})
                    continue
                data = parse_artifact(repo, rel, errors, checks)
                if rel.lower().endswith('.json') and data is not None:
                    indexed_json_parse_count += 1
                    parse_records.append({'path': rel, 'parse': True})
                if field == 'receipt_path' and not relpath(repo, rel).exists():
                    missing_receipt_count += 1
                if field in ('summary_path','report_path') and not relpath(repo, rel).exists():
                    missing_report_count += 1
        indexed_records.append(record)

    for item in supporting_truth:
        record = {'truth_id': item.get('truth_id'), 'state': item.get('state')}
        for field in ('summary_path','report_path','receipt_path'):
            rel = item.get(field)
            record[field] = rel
            if rel:
                data = parse_artifact(repo, rel, errors, checks)
                if rel.lower().endswith('.json') and data is not None:
                    indexed_json_parse_count += 1
        receipt_records.append(record)

    gate_ids = {i.get('gate_id') for i in current_gate_truth}
    if len(gate_ids) != 6:
        errors.append({'error': 'CURRENT_GATE_TRUTH_COUNT_NOT_SIX', 'count': len(gate_ids)})
    g6 = next((i for i in current_gate_truth if i.get('gate_id') == 'G6_RESIDENCY_TRUST'), None)
    if not g6 or g6.get('state') != 'NOT_PROVEN':
        errors.append({'error': 'G6_MUST_REMAIN_NOT_PROVEN', 'value': g6})

    if index.get('organ_assembly_claim') is not False:
        errors.append({'error': 'ORGAN_ASSEMBLY_OVERCLAIM_IN_INDEX', 'value': index.get('organ_assembly_claim')})
    if index.get('six_gate_closure_claim') is not False:
        errors.append({'error': 'SIX_GATE_OVERCLAIM_IN_INDEX', 'value': index.get('six_gate_closure_claim')})
    if manifest and manifest.get('organ_assembly_claim') is not False:
        errors.append({'error': 'ORGAN_ASSEMBLY_OVERCLAIM_IN_MANIFEST', 'value': manifest.get('organ_assembly_claim')})
    if manifest and manifest.get('six_gate_closure_claim') is not False:
        errors.append({'error': 'SIX_GATE_OVERCLAIM_IN_MANIFEST', 'value': manifest.get('six_gate_closure_claim')})

    local_model_status = index.get('local_model_membrane_status')
    if local_model_status != 'DEFERRED_AFTER_CORE_V1':
        errors.append({'error': 'LOCAL_MODEL_MEMBRANE_NOT_DEFERRED', 'value': local_model_status})

    six_gate_progress = matrix.get('six_gate_progress_after_pass') or []
    if not six_gate_progress:
        six_gate_progress = [
            {'gate_id': 'G1_IDENTITY_MANIFEST', 'state': 'PASS_BASELINE', 'closure_claim': 'BASELINE_ONLY_NOT_FULL_ORGAN_CLOSURE'},
            {'gate_id': 'G2_FUNCTIONS_REGISTRY', 'state': 'PASS_BASELINE', 'closure_claim': 'BASELINE_ONLY_NOT_FULL_ORGAN_CLOSURE'},
            {'gate_id': 'G3_CAPABILITY_EVIDENCE', 'state': 'PASS_BASELINE', 'closure_claim': 'BASELINE_ONLY_NOT_FULL_ORGAN_CLOSURE'},
            {'gate_id': 'G4_PERSONAL_VALIDATORS', 'state': 'PASS_BASELINE', 'closure_claim': 'BASELINE_ONLY_NOT_FULL_ORGAN_CLOSURE'},
            {'gate_id': 'G5_CURRENT_TRUTH_RECEIPTS', 'state': 'PASS_BASELINE', 'closure_claim': 'BASELINE_ONLY_NOT_FULL_ORGAN_CLOSURE'},
            {'gate_id': 'G6_RESIDENCY_TRUST', 'state': 'NOT_PROVEN', 'closure_claim': 'NOT_FULLY_CLOSED'},
        ]

    checks.extend([
        {'name': 'current_gate_truth_has_six_gates', 'status': 'PASS' if len(gate_ids) == 6 else 'FAIL', 'details': {'count': len(gate_ids)}},
        {'name': 'five_gates_pass_baseline', 'status': 'PASS' if pass_baseline_gate_count == 5 else 'FAIL', 'details': {'count': pass_baseline_gate_count}},
        {'name': 'g6_not_proven', 'status': 'PASS' if (g6 and g6.get('state') == 'NOT_PROVEN') else 'FAIL', 'details': {'g6': g6}},
        {'name': 'missing_required_reports_zero', 'status': 'PASS' if missing_report_count == 0 else 'FAIL', 'details': {'count': missing_report_count}},
        {'name': 'missing_required_receipts_zero', 'status': 'PASS' if missing_receipt_count == 0 else 'FAIL', 'details': {'count': missing_receipt_count}},
        {'name': 'malformed_current_truth_zero', 'status': 'PASS' if malformed_current_truth_count == 0 else 'FAIL', 'details': {'count': malformed_current_truth_count}},
        {'name': 'local_model_deferred', 'status': 'PASS' if local_model_status == 'DEFERRED_AFTER_CORE_V1' else 'FAIL', 'details': {'value': local_model_status}},
        {'name': 'no_organ_assembly_claim', 'status': 'PASS' if index.get('organ_assembly_claim') is False else 'FAIL', 'details': {'value': index.get('organ_assembly_claim')}},
        {'name': 'no_six_gate_closure_claim', 'status': 'PASS' if index.get('six_gate_closure_claim') is False else 'FAIL', 'details': {'value': index.get('six_gate_closure_claim')}},
    ])

    if pass_baseline_gate_count != 5:
        errors.append({'error': 'EXPECTED_FIVE_PASS_BASELINE_GATES', 'count': pass_baseline_gate_count})
    if missing_report_count:
        errors.append({'error': 'MISSING_REQUIRED_CURRENT_REPORTS', 'count': missing_report_count})
    if missing_receipt_count:
        errors.append({'error': 'MISSING_REQUIRED_CURRENT_RECEIPTS', 'count': missing_receipt_count})
    if malformed_current_truth_count:
        errors.append({'error': 'MALFORMED_CURRENT_TRUTH_INDEX', 'count': malformed_current_truth_count})

    verdict = 'PASS_MECHANICUS_CURRENT_TRUTH_RECEIPTS_GATE_READY' if not errors else 'FAIL_MECHANICUS_CURRENT_TRUTH_RECEIPTS_GATE'

    report = {
        'task_id': PATCH_ID,
        'validator_id': VALIDATOR_ID,
        'verdict': verdict,
        'generated_at_utc': generated_at,
        'gate_id': GATE_ID,
        'current_truth_receipts_gate_status': 'PASS_BASELINE' if verdict.startswith('PASS') else 'FAIL',
        'current_gate_truth_count': len(current_gate_truth),
        'pass_baseline_gate_count': pass_baseline_gate_count,
        'not_proven_gate_count': not_proven_gate_count,
        'indexed_current_record_count': len(indexed_records),
        'supporting_truth_record_count': len(receipt_records),
        'indexed_json_parse_count': indexed_json_parse_count,
        'missing_required_report_count': missing_report_count,
        'missing_required_receipt_count': missing_receipt_count,
        'malformed_current_truth_count': malformed_current_truth_count,
        'local_model_membrane_status': local_model_status,
        'organ_assembly_claim': False,
        'six_gate_closure_claim': False,
        'indexed_gate_records': indexed_records,
        'supporting_truth_records': receipt_records,
        'six_gate_progress': six_gate_progress,
        'non_current_classes': index.get('non_current_classes', []),
        'receipt': RECEIPT,
        'summary': SUMMARY,
        'report_json': REPORT_JSON,
        'report_md': REPORT_MD,
        'errors': errors,
        'warnings': warnings,
        'checks': checks
    }
    summary = {
        'task_id': PATCH_ID,
        'validator_id': VALIDATOR_ID,
        'verdict': verdict,
        'generated_at_utc': generated_at,
        'gate_id': GATE_ID,
        'current_truth_receipts_gate_status': report['current_truth_receipts_gate_status'],
        'current_gate_truth_count': len(current_gate_truth),
        'pass_baseline_gate_count': pass_baseline_gate_count,
        'not_proven_gate_count': not_proven_gate_count,
        'indexed_current_record_count': len(indexed_records),
        'supporting_truth_record_count': len(receipt_records),
        'missing_required_report_count': missing_report_count,
        'missing_required_receipt_count': missing_receipt_count,
        'malformed_current_truth_count': malformed_current_truth_count,
        'local_model_membrane_status': local_model_status,
        'next_gate_count': 3,
        'organ_assembly_claim': False,
        'six_gate_closure_claim': False,
        'errors': errors,
        'warnings': warnings
    }
    receipt = dict(summary)
    receipt.update({'receipt': RECEIPT, 'summary': SUMMARY, 'report_json': REPORT_JSON, 'report_md': REPORT_MD})

    write_json(repo, REPORT_JSON, report)
    write_json(repo, SUMMARY, summary)
    write_json(repo, RECEIPT, receipt)
    md = [
        '# MECHANICUS Current Truth / Receipts Gate Report v0.1',
        '',
        f'- task_id: `{PATCH_ID}`',
        f'- verdict: `{verdict}`',
        f'- gate: `{GATE_ID}`',
        f'- current_truth_receipts_gate_status: `{report["current_truth_receipts_gate_status"]}`',
        f'- pass_baseline_gate_count: `{pass_baseline_gate_count}`',
        f'- not_proven_gate_count: `{not_proven_gate_count}`',
        f'- missing_required_report_count: `{missing_report_count}`',
        f'- missing_required_receipt_count: `{missing_receipt_count}`',
        f'- local_model_membrane_status: `{local_model_status}`',
        '',
        '## Six Gate Progress',
        '',
        '| Gate | State | Closure claim |',
        '|---|---:|---|',
    ]
    for g in six_gate_progress:
        md.append(f'| {g.get("gate_id")} | {g.get("state")} | {g.get("closure_claim")} |')
    md.extend(['', '## Warnings'])
    for w in warnings:
        md.append(f'- {w}')
    if errors:
        md.extend(['', '## Errors'])
        for e in errors:
            md.append(f'- `{e}`')
    relpath(repo, REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    relpath(repo, REPORT_MD).write_text('\n'.join(md) + '\n', encoding='utf-8')
    return receipt

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root', default='.')
    ns = ap.parse_args()
    repo = Path(ns.repo_root).resolve()
    receipt = build(repo)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if str(receipt.get('verdict','')).startswith('PASS_') else 2

if __name__ == '__main__':
    raise SystemExit(main())
