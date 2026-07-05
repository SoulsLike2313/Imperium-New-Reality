#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, py_compile, shutil, subprocess, sys
from pathlib import Path

PATCH_ID = "MECHANICUS-CURRENT-TRUTH-RECEIPTS-GATE-0001"
VALIDATOR_ID = "mechanicus_current_truth_receipts_gate_validator.v0_1"
FILES = [
  "ORGANS/MECHANICUS/MANIFEST.json",
  "ORGANS/MECHANICUS/LAWS/MECHANICUS_CURRENT_TRUTH_RECEIPTS_GATE_LAW_V0_1.json",
  "ORGANS/MECHANICUS/MATRICES/MECHANICUS_CURRENT_TRUTH_INDEX_V0_1.json",
  "ORGANS/MECHANICUS/MATRICES/MECHANICUS_CURRENT_TRUTH_RECEIPTS_GATE_MATRIX_V0_1.json",
  "ORGANS/MECHANICUS/TOOLS/build_mechanicus_current_truth_receipts_gate.py",
  "ORGANS/MECHANICUS/VALIDATORS/validate_mechanicus_current_truth_receipts_gate.py",
  "ORGANS/CUSTODES/MATRICES/CUSTODES_MECHANICUS_CURRENT_TRUTH_RECEIPTS_GATE_PROSECUTOR_MATRIX_V0_1.json",
  "ORGANS/THRONE/MATRICES/THRONE_MECHANICUS_CURRENT_TRUTH_RECEIPTS_GATE_CROWN_MATRIX_V0_1.json",
]
GENERATED = [
  "ORGANS/MECHANICUS/RECEIPTS/mechanicus_current_truth_receipts_gate_receipt.json",
  "ORGANS/MECHANICUS/REPORTS/MECHANICUS_CURRENT_TRUTH_RECEIPTS_GATE_SUMMARY_V0_1.json",
  "ORGANS/MECHANICUS/REPORTS/MECHANICUS_CURRENT_TRUTH_RECEIPTS_GATE_REPORT_V0_1.json",
  "ORGANS/MECHANICUS/REPORTS/MECHANICUS_CURRENT_TRUTH_RECEIPTS_GATE_REPORT_V0_1.md",
]

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

def read_json(path: Path):
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root', default='.')
    ns = ap.parse_args()
    repo = Path(ns.repo_root).resolve()
    errors = []
    warnings = []
    checks = []

    for rel in FILES:
        p = repo / rel
        exists = p.exists()
        checks.append({'name': f'exists::{rel}', 'status': 'PASS' if exists else 'FAIL', 'details': {'path': rel}})
        if not exists:
            errors.append({'error': 'MISSING_REQUIRED_FILE', 'path': rel})
            continue
        hits = has_control_chars(p)
        checks.append({'name': f'no_control_chars::{rel}', 'status': 'PASS' if not hits else 'FAIL', 'details': {'hits': hits}})
        if hits:
            errors.append({'error': 'CONTROL_CHARS', 'path': rel, 'hits': hits})
        if rel.endswith('.json'):
            try:
                read_json(p)
                checks.append({'name': f'json_parse::{rel}', 'status': 'PASS', 'details': {}})
            except Exception as e:
                checks.append({'name': f'json_parse::{rel}', 'status': 'FAIL', 'details': {'error': str(e)}})
                errors.append({'error': 'JSON_PARSE_ERROR', 'path': rel, 'message': str(e)})
        if rel.endswith('.py'):
            try:
                py_compile.compile(str(p), doraise=True)
                checks.append({'name': f'py_compile::{rel}', 'status': 'PASS', 'details': {}})
            except Exception as e:
                checks.append({'name': f'py_compile::{rel}', 'status': 'FAIL', 'details': {'error': str(e)}})
                errors.append({'error': 'PY_COMPILE_ERROR', 'path': rel, 'message': str(e)})

    builder = repo / 'ORGANS/MECHANICUS/TOOLS/build_mechanicus_current_truth_receipts_gate.py'
    if not errors:
        proc = subprocess.run([sys.executable, str(builder), '--repo-root', str(repo)], text=True, capture_output=True)
        if proc.returncode != 0:
            errors.append({'error': 'BUILDER_FAILED', 'returncode': proc.returncode, 'stdout': proc.stdout[-4000:], 'stderr': proc.stderr[-4000:]})
            checks.append({'name': 'builder_runs', 'status': 'FAIL', 'details': {'returncode': proc.returncode}})
        else:
            try:
                receipt = json.loads(proc.stdout)
            except Exception as e:
                errors.append({'error': 'BUILDER_OUTPUT_NOT_JSON', 'message': str(e), 'stdout': proc.stdout[-4000:]})
                receipt = {}
            checks.append({'name': 'builder_runs', 'status': 'PASS', 'details': receipt})

    report = {}
    summary = {}
    receipt = {}
    for rel in GENERATED:
        p = repo / rel
        exists = p.exists()
        checks.append({'name': f'generated::{rel}', 'status': 'PASS' if exists else 'FAIL', 'details': {'path': rel}})
        if not exists:
            errors.append({'error': 'MISSING_GENERATED_FILE', 'path': rel})
    try:
        report = read_json(repo / 'ORGANS/MECHANICUS/REPORTS/MECHANICUS_CURRENT_TRUTH_RECEIPTS_GATE_REPORT_V0_1.json')
        summary = read_json(repo / 'ORGANS/MECHANICUS/REPORTS/MECHANICUS_CURRENT_TRUTH_RECEIPTS_GATE_SUMMARY_V0_1.json')
        receipt = read_json(repo / 'ORGANS/MECHANICUS/RECEIPTS/mechanicus_current_truth_receipts_gate_receipt.json')
    except Exception as e:
        errors.append({'error': 'GENERATED_JSON_READ_FAILED', 'message': str(e)})

    expected_checks = [
        ('summary_verdict_pass', summary.get('verdict') == 'PASS_MECHANICUS_CURRENT_TRUTH_RECEIPTS_GATE_READY', {'verdict': summary.get('verdict')}),
        ('g5_status_pass_baseline', summary.get('current_truth_receipts_gate_status') == 'PASS_BASELINE', {'value': summary.get('current_truth_receipts_gate_status')}),
        ('five_pass_baseline_gates', summary.get('pass_baseline_gate_count') == 5, {'count': summary.get('pass_baseline_gate_count')}),
        ('g6_not_proven_visible', summary.get('not_proven_gate_count') == 1, {'count': summary.get('not_proven_gate_count')}),
        ('missing_required_reports_zero', summary.get('missing_required_report_count') == 0, {'count': summary.get('missing_required_report_count')}),
        ('missing_required_receipts_zero', summary.get('missing_required_receipt_count') == 0, {'count': summary.get('missing_required_receipt_count')}),
        ('local_model_deferred', summary.get('local_model_membrane_status') == 'DEFERRED_AFTER_CORE_V1', {'value': summary.get('local_model_membrane_status')}),
        ('no_organ_assembly_claim', summary.get('organ_assembly_claim') is False, {'value': summary.get('organ_assembly_claim')}),
        ('no_six_gate_closure_claim', summary.get('six_gate_closure_claim') is False, {'value': summary.get('six_gate_closure_claim')}),
    ]
    for name, ok, details in expected_checks:
        checks.append({'name': name, 'status': 'PASS' if ok else 'FAIL', 'details': details})
        if not ok:
            errors.append({'error': name.upper(), 'details': details})

    final = {
        'task_id': PATCH_ID,
        'validator_id': VALIDATOR_ID,
        'verdict': 'PASS_MECHANICUS_CURRENT_TRUTH_RECEIPTS_GATE_READY' if not errors else 'FAIL_MECHANICUS_CURRENT_TRUTH_RECEIPTS_GATE',
        'receipt': 'ORGANS/MECHANICUS/RECEIPTS/mechanicus_current_truth_receipts_gate_receipt.json',
        'summary': 'ORGANS/MECHANICUS/REPORTS/MECHANICUS_CURRENT_TRUTH_RECEIPTS_GATE_SUMMARY_V0_1.json',
        'report_json': 'ORGANS/MECHANICUS/REPORTS/MECHANICUS_CURRENT_TRUTH_RECEIPTS_GATE_REPORT_V0_1.json',
        'report_md': 'ORGANS/MECHANICUS/REPORTS/MECHANICUS_CURRENT_TRUTH_RECEIPTS_GATE_REPORT_V0_1.md',
        'errors': errors,
        'warnings': warnings,
        'checks': checks,
    }
    print(json.dumps(final, ensure_ascii=False, indent=2))
    return 0 if not errors else 2

if __name__ == '__main__':
    raise SystemExit(main())
