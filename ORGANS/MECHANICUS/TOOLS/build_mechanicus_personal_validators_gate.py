#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import py_compile
from datetime import datetime, timezone
from pathlib import Path

TASK_ID = "MECHANICUS-PERSONAL-VALIDATORS-GATE-0001"
VALIDATOR_ID = "mechanicus_personal_validators_gate_validator.v0_1"
PASS_VERDICT = "PASS_MECHANICUS_PERSONAL_VALIDATORS_GATE_READY"

REGISTRY = "ORGANS/MECHANICUS/MATRICES/MECHANICUS_PERSONAL_VALIDATORS_REGISTRY_V0_1.json"
MANIFEST = "ORGANS/MECHANICUS/MANIFEST.json"
MATRIX = "ORGANS/MECHANICUS/MATRICES/MECHANICUS_PERSONAL_VALIDATORS_GATE_MATRIX_V0_1.json"
RECEIPT = "ORGANS/MECHANICUS/RECEIPTS/mechanicus_personal_validators_gate_receipt.json"
SUMMARY = "ORGANS/MECHANICUS/REPORTS/MECHANICUS_PERSONAL_VALIDATORS_GATE_SUMMARY_V0_1.json"
REPORT_JSON = "ORGANS/MECHANICUS/REPORTS/MECHANICUS_PERSONAL_VALIDATORS_GATE_REPORT_V0_1.json"
REPORT_MD = "ORGANS/MECHANICUS/REPORTS/MECHANICUS_PERSONAL_VALIDATORS_GATE_REPORT_V0_1.md"

CONTROL_CHARS = {chr(i) for i in range(32)} - {"\n", "\r", "\t"}


def read_json(root: Path, rel: str):
    return json.loads((root / rel).read_text(encoding="utf-8"))


def write_json(root: Path, rel: str, data):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def has_control_chars(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    hits = []
    for idx, ch in enumerate(text):
        if ch in CONTROL_CHARS:
            line = text.count("\n", 0, idx) + 1
            col = idx - text.rfind("\n", 0, idx)
            hits.append({"line": line, "column": col, "ord": ord(ch)})
            if len(hits) >= 10:
                break
    return hits


def build(repo_root: Path, write_outputs: bool = True):
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    registry = read_json(repo_root, REGISTRY)
    matrix = read_json(repo_root, MATRIX)
    manifest = read_json(repo_root, MANIFEST)

    errors: list[str] = []
    warnings: list[str] = [
        "This patch closes Personal Validators baseline only; it does not assemble Mechanicus.",
        "Current truth/receipts, residency/trust, Custodes and Throne gates remain future work.",
        "Personal validators are baseline self-checks and still require future Custodes prosecution."
    ]

    validator_records = []
    missing = []
    compile_failures = []
    control_char_failures = []
    protects_claim_discipline = False

    for item in registry.get('validators', []):
        rel = item.get('path')
        path = repo_root / rel
        record = {
            'validator_id': item.get('validator_id'),
            'path': rel,
            'status': item.get('status'),
            'protects': item.get('protects') or [],
            'exists': path.exists(),
            'no_control_chars': None,
            'python_compile': None,
            'compile_error': None,
        }
        if 'claim_discipline' in record['protects'] or 'no_assembly_overclaim' in record['protects']:
            protects_claim_discipline = True
        if not path.exists():
            missing.append(rel)
        else:
            hits = has_control_chars(path)
            record['no_control_chars'] = not hits
            record['control_char_hits'] = hits
            if hits:
                control_char_failures.append({'path': rel, 'hits': hits})
            try:
                py_compile.compile(str(path), doraise=True)
                record['python_compile'] = True
            except Exception as exc:
                record['python_compile'] = False
                record['compile_error'] = str(exc)
                compile_failures.append({'path': rel, 'error': str(exc)})
        validator_records.append(record)

    required = [r for r in validator_records if r.get('status') == 'REQUIRED_BASELINE']
    present_required = [r for r in required if r.get('exists')]
    compiled_required = [r for r in required if r.get('python_compile') is True]
    no_control_required = [r for r in required if r.get('no_control_chars') is True]

    if missing:
        errors.append(f"Missing required personal validators: {missing}")
    if compile_failures:
        errors.append(f"Personal validator compile failures: {compile_failures}")
    if control_char_failures:
        errors.append(f"Control characters found in personal validators: {control_char_failures}")
    if not protects_claim_discipline:
        errors.append("No required personal validator protects claim discipline")
    if manifest.get('organ_assembly_claim') is not False or manifest.get('six_gate_closure_claim') is not False:
        errors.append("Manifest must not claim organ assembly or six gate closure")
    if registry.get('local_model_membrane_status') != 'DEFERRED_AFTER_CORE_V1':
        errors.append("Local model membrane must remain DEFERRED_AFTER_CORE_V1")

    personal_validators_gate_status = 'PASS_BASELINE' if not errors else 'FAIL'
    six_gate_progress = matrix.get('six_gate_progress_after_pass', [])

    report = {
        'task_id': TASK_ID,
        'validator_id': VALIDATOR_ID,
        'verdict': PASS_VERDICT if not errors else 'FAIL_MECHANICUS_PERSONAL_VALIDATORS_GATE',
        'generated_at_utc': now,
        'gate_id': 'G4_PERSONAL_VALIDATORS',
        'personal_validators_gate_status': personal_validators_gate_status,
        'required_validator_count': len(required),
        'present_required_validator_count': len(present_required),
        'compiled_required_validator_count': len(compiled_required),
        'no_control_char_required_validator_count': len(no_control_required),
        'missing_required_validator_count': len(missing),
        'compile_failure_count': len(compile_failures),
        'control_char_failure_count': len(control_char_failures),
        'claim_discipline_protected': protects_claim_discipline,
        'validator_records': validator_records,
        'six_gate_progress': six_gate_progress,
        'local_model_membrane_status': registry.get('local_model_membrane_status'),
        'organ_assembly_claim': False,
        'six_gate_closure_claim': False,
        'future_external_audits_required': registry.get('future_external_audits_required', []),
        'errors': errors,
        'warnings': warnings,
    }
    summary = {
        'task_id': TASK_ID,
        'validator_id': VALIDATOR_ID,
        'verdict': report['verdict'],
        'generated_at_utc': now,
        'personal_validators_gate_status': personal_validators_gate_status,
        'required_validator_count': len(required),
        'present_required_validator_count': len(present_required),
        'compiled_required_validator_count': len(compiled_required),
        'no_control_char_required_validator_count': len(no_control_required),
        'missing_required_validator_count': len(missing),
        'compile_failure_count': len(compile_failures),
        'control_char_failure_count': len(control_char_failures),
        'claim_discipline_protected': protects_claim_discipline,
        'local_model_membrane_status': registry.get('local_model_membrane_status'),
        'next_gate_count': 4,
        'organ_assembly_claim': False,
        'six_gate_closure_claim': False,
        'errors_count': len(errors),
        'warnings_count': len(warnings),
    }
    receipt = {
        'task_id': TASK_ID,
        'validator_id': VALIDATOR_ID,
        'verdict': report['verdict'],
        'generated_at_utc': now,
        'gate_id': 'G4_PERSONAL_VALIDATORS',
        'personal_validators_gate_status': personal_validators_gate_status,
        'required_validator_count': len(required),
        'present_required_validator_count': len(present_required),
        'compiled_required_validator_count': len(compiled_required),
        'missing_required_validator_count': len(missing),
        'compile_failure_count': len(compile_failures),
        'control_char_failure_count': len(control_char_failures),
        'claim_discipline_protected': protects_claim_discipline,
        'organ_assembly_claim': False,
        'six_gate_closure_claim': False,
        'receipt': RECEIPT,
        'summary': SUMMARY,
        'report_json': REPORT_JSON,
        'report_md': REPORT_MD,
        'errors': errors,
        'warnings': warnings,
    }
    md = [
        '# MECHANICUS PERSONAL VALIDATORS GATE REPORT V0.1',
        '',
        f'- task_id: `{TASK_ID}`',
        f'- verdict: `{report["verdict"]}`',
        f'- gate: `G4_PERSONAL_VALIDATORS`',
        f'- status: `{personal_validators_gate_status}`',
        f'- required validators: `{len(required)}`',
        f'- present required validators: `{len(present_required)}`',
        f'- compiled required validators: `{len(compiled_required)}`',
        f'- missing required validators: `{len(missing)}`',
        f'- compile failures: `{len(compile_failures)}`',
        f'- control char failures: `{len(control_char_failures)}`',
        f'- claim discipline protected: `{protects_claim_discipline}`',
        f'- local model membrane: `{registry.get("local_model_membrane_status")}`',
        '',
        '## Six Gate Progress',
        ''
    ]
    for g in six_gate_progress:
        md.append(f'- `{g.get("gate_id")}`: `{g.get("state")}` / `{g.get("closure_claim")}`')
    md.extend(['', '## Warnings', ''])
    for w in warnings:
        md.append(f'- {w}')
    if errors:
        md.extend(['', '## Errors', ''])
        for e in errors:
            md.append(f'- {e}')
    else:
        md.extend(['', '## No Fake Green', '', 'This PASS is baseline self-validator coverage only. It is not Custodes audit, Throne crown, full trust, or organ assembly.'])

    if write_outputs:
        write_json(repo_root, REPORT_JSON, report)
        write_json(repo_root, SUMMARY, summary)
        write_json(repo_root, RECEIPT, receipt)
        (repo_root / REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
        (repo_root / REPORT_MD).write_text('\n'.join(md) + '\n', encoding='utf-8')
    return {'receipt': receipt, 'summary': summary, 'report': report}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root', default='.')
    args = ap.parse_args()
    result = build(Path(args.repo_root).resolve(), write_outputs=True)
    print(json.dumps(result['receipt'], ensure_ascii=False, indent=2))
    raise SystemExit(0 if not result['receipt'].get('errors') else 2)

if __name__ == '__main__':
    main()
