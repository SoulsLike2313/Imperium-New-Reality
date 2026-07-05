#!/usr/bin/env python3
from __future__ import annotations
import argparse
import importlib.util
import json
import shutil
from pathlib import Path

TASK_ID = "MECHANICUS-PERSONAL-VALIDATORS-GATE-0001"
VALIDATOR_ID = "mechanicus_personal_validators_gate_validator.v0_1"
PASS_VERDICT = "PASS_MECHANICUS_PERSONAL_VALIDATORS_GATE_READY"

REQUIRED_STATIC = [
    "ORGANS/MECHANICUS/MANIFEST.json",
    "ORGANS/MECHANICUS/MATRICES/MECHANICUS_PERSONAL_VALIDATORS_REGISTRY_V0_1.json",
    "ORGANS/MECHANICUS/LAWS/MECHANICUS_PERSONAL_VALIDATORS_GATE_LAW_V0_1.json",
    "ORGANS/MECHANICUS/MATRICES/MECHANICUS_PERSONAL_VALIDATORS_GATE_MATRIX_V0_1.json",
    "ORGANS/MECHANICUS/TOOLS/build_mechanicus_personal_validators_gate.py",
    "ORGANS/MECHANICUS/VALIDATORS/validate_mechanicus_personal_validators_gate.py",
    "ORGANS/CUSTODES/MATRICES/CUSTODES_MECHANICUS_PERSONAL_VALIDATORS_GATE_PROSECUTOR_MATRIX_V0_1.json",
    "ORGANS/THRONE/MATRICES/THRONE_MECHANICUS_PERSONAL_VALIDATORS_GATE_CROWN_MATRIX_V0_1.json",
]

GENERATED = [
    "ORGANS/MECHANICUS/RECEIPTS/mechanicus_personal_validators_gate_receipt.json",
    "ORGANS/MECHANICUS/REPORTS/MECHANICUS_PERSONAL_VALIDATORS_GATE_SUMMARY_V0_1.json",
    "ORGANS/MECHANICUS/REPORTS/MECHANICUS_PERSONAL_VALIDATORS_GATE_REPORT_V0_1.json",
    "ORGANS/MECHANICUS/REPORTS/MECHANICUS_PERSONAL_VALIDATORS_GATE_REPORT_V0_1.md",
]

CONTROL_CHARS = {chr(i) for i in range(32)} - {"\n", "\r", "\t"}


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


def copy_files_to_land(files_to_land: Path, repo_root: Path):
    if not files_to_land.exists():
        raise FileNotFoundError(f"FILES_TO_LAND not found: {files_to_land}")
    for child in files_to_land.iterdir():
        dst = repo_root / child.name
        if child.is_dir():
            shutil.copytree(child, dst, dirs_exist_ok=True)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(child, dst)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_builder(repo_root: Path):
    builder_path = repo_root / "ORGANS/MECHANICUS/TOOLS/build_mechanicus_personal_validators_gate.py"
    spec = importlib.util.spec_from_file_location("build_mechanicus_personal_validators_gate", builder_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder: {builder_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root', default='.')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--files-to-land', default=None)
    args = ap.parse_args()
    repo_root = Path(args.repo_root).resolve()

    if args.apply:
        if not args.files_to_land:
            raise SystemExit('--apply requires --files-to-land')
        copy_files_to_land(Path(args.files_to_land).resolve(), repo_root)

    checks = []
    errors = []
    warnings = []

    def check(name, status, details=None, error=None):
        checks.append({'name': name, 'status': 'PASS' if status else 'FAIL', 'details': details or {}})
        if not status and error:
            errors.append(error)

    for rel in REQUIRED_STATIC:
        path = repo_root / rel
        check(f'exists::{rel}', path.exists(), {'path': rel}, f'missing required static file: {rel}')
        if path.exists() and path.suffix.lower() in {'.py', '.json', '.md', '.ps1'}:
            hits = has_control_chars(path)
            check(f'no_control_chars::{rel}', not hits, {'hits': hits}, f'control characters found in {rel}: {hits[:3]}')
            if path.suffix.lower() == '.json':
                try:
                    load_json(path)
                    check(f'json_parse::{rel}', True, {})
                except Exception as exc:
                    check(f'json_parse::{rel}', False, {'error': str(exc)}, f'JSON parse failed for {rel}: {exc}')

    if not errors:
        builder = load_builder(repo_root)
        result = builder.build(repo_root, write_outputs=True)
        receipt = result['receipt']
        report = result['report']
        checks.append({'name': 'builder_runs', 'status': 'PASS', 'details': receipt})
        errors.extend(receipt.get('errors') or [])
        warnings.extend(receipt.get('warnings') or [])
        check('receipt_verdict_pass', receipt.get('verdict') == PASS_VERDICT, {'verdict': receipt.get('verdict')}, 'receipt verdict is not PASS_MECHANICUS_PERSONAL_VALIDATORS_GATE_READY')
        check('g4_status_pass_baseline', receipt.get('personal_validators_gate_status') == 'PASS_BASELINE', {'value': receipt.get('personal_validators_gate_status')}, 'G4 personal validators gate did not reach PASS_BASELINE')
        check('all_required_validators_present', receipt.get('required_validator_count') == receipt.get('present_required_validator_count'), {'required': receipt.get('required_validator_count'), 'present': receipt.get('present_required_validator_count')}, 'not all required validators are present')
        check('no_compile_failures', receipt.get('compile_failure_count') == 0, {'count': receipt.get('compile_failure_count')}, 'personal validator compile failures exist')
        check('no_control_char_failures', receipt.get('control_char_failure_count') == 0, {'count': receipt.get('control_char_failure_count')}, 'personal validator control-char failures exist')
        check('claim_discipline_protected', receipt.get('claim_discipline_protected') is True, {'value': receipt.get('claim_discipline_protected')}, 'claim discipline is not protected')
        check('no_organ_assembly_claim', receipt.get('organ_assembly_claim') is False, {'value': receipt.get('organ_assembly_claim')}, 'organ assembly claim must remain false')
        check('no_six_gate_closure_claim', receipt.get('six_gate_closure_claim') is False, {'value': receipt.get('six_gate_closure_claim')}, 'six gate closure claim must remain false')
        if report.get('local_model_membrane_status') != 'DEFERRED_AFTER_CORE_V1':
            errors.append('local model membrane must remain DEFERRED_AFTER_CORE_V1')

    for rel in GENERATED:
        path = repo_root / rel
        check(f'generated::{rel}', path.exists(), {'path': rel}, f'generated output missing: {rel}')

    verdict = PASS_VERDICT if not errors else 'FAIL_MECHANICUS_PERSONAL_VALIDATORS_GATE'
    output = {
        'task_id': TASK_ID,
        'validator_id': VALIDATOR_ID,
        'verdict': verdict,
        'receipt': 'ORGANS/MECHANICUS/RECEIPTS/mechanicus_personal_validators_gate_receipt.json',
        'summary': 'ORGANS/MECHANICUS/REPORTS/MECHANICUS_PERSONAL_VALIDATORS_GATE_SUMMARY_V0_1.json',
        'report_json': 'ORGANS/MECHANICUS/REPORTS/MECHANICUS_PERSONAL_VALIDATORS_GATE_REPORT_V0_1.json',
        'report_md': 'ORGANS/MECHANICUS/REPORTS/MECHANICUS_PERSONAL_VALIDATORS_GATE_REPORT_V0_1.md',
        'errors': errors,
        'warnings': list(dict.fromkeys(warnings)),
        'checks': checks,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    raise SystemExit(0 if not errors else 2)

if __name__ == '__main__':
    main()
