#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, json, subprocess, sys
from pathlib import Path
from typing import Any, Dict, List
TASK_ID = "MECHANICUS-LANGUAGE-SURFACE-V2-TOOLCHAIN-PROBE-ULTRASAFE-HOTFIX-0002"
VALIDATOR_ID = "mechanicus_language_surface_v2_toolchain_probe_ultrasafe_hotfix_validator.v0_2"
PROBE = Path("ORGANS/MECHANICUS/TOOLS/prove_toolchains.py")
PREVIOUS_VALIDATOR = Path("ORGANS/MECHANICUS/VALIDATORS/validate_mechanicus_language_surface_v2_toolchain_validator_dispatch.py")
PREVIOUS_RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_language_surface_v2_toolchain_validator_dispatch_receipt.json")
TOOLCHAIN_REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOLCHAIN_PROOF_REPORT_V0_1.json")
RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_language_surface_v2_toolchain_probe_ultrasafe_hotfix_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_PROBE_ULTRASAFE_HOTFIX_SUMMARY_V0_2.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_PROBE_ULTRASAFE_HOTFIX_REPORT_V0_2.md")
def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def load_json(path: Path):
    try: return json.loads(path.read_text(encoding='utf-8-sig')), None
    except Exception as e: return None, str(e)
def write_json(path: Path, data: Any): path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def add(checks: List[Dict[str, Any]], name: str, ok: bool, details=None): checks.append({'name': name, 'status': 'PASS' if ok else 'FAIL', 'details': details or {}})
def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument('--repo-root', default='.'); ap.add_argument('--apply', action='store_true'); args = ap.parse_args(); repo = Path(args.repo_root).resolve()
    checks=[]; errors=[]; warnings=[]; report_data={}
    text = (repo/PROBE).read_text(encoding='utf-8', errors='replace') if (repo/PROBE).is_file() else ''
    add(checks, 'ultrasafe_toolchain_probe_installed', 'mechanicus_toolchain_probe.v0_3_ultrasafe_nonblocking' in text, {'path': PROBE.as_posix()})
    if checks[-1]['status'] != 'PASS': errors.append('ultrasafe toolchain probe not installed')
    if not errors:
        p = subprocess.run([sys.executable, str(repo/PROBE), '--repo-root', str(repo), '--out', TOOLCHAIN_REPORT.as_posix()], cwd=str(repo), capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=90)
        exists = (repo/TOOLCHAIN_REPORT).is_file()
        add(checks, 'ultrasafe_probe_runs_and_writes_report', p.returncode == 0 and exists, {'exit_code':p.returncode,'stdout_tail':p.stdout[-2500:],'stderr_tail':p.stderr[-2500:]})
        if p.returncode != 0 or not exists: errors.append('ultrasafe probe did not run/write report')
        else:
            report_data, err = load_json(repo/TOOLCHAIN_REPORT)
            rt = json.dumps(report_data, ensure_ascii=False) if isinstance(report_data, dict) else ''
            ok = err is None and 'ULTRASAFE_NONBLOCKING_LOCAL_TOOLCHAIN_CAPABILITY_PROBE' in rt and 'not_claimed' in report_data
            add(checks, 'ultrasafe_probe_report_has_debt_boundary', ok, {'error':err,'verdict':report_data.get('verdict') if isinstance(report_data,dict) else None})
            if not ok: errors.append('ultrasafe probe report lacks debt boundary')
    add(checks, 'previous_language_surface_v2_validator_exists', (repo/PREVIOUS_VALIDATOR).is_file(), {'path': PREVIOUS_VALIDATOR.as_posix()})
    if checks[-1]['status'] != 'PASS': errors.append('previous validator missing')
    if not errors:
        p = subprocess.run([sys.executable, str(repo/PREVIOUS_VALIDATOR), '--repo-root', str(repo), '--apply'], cwd=str(repo), capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=420)
        ok = p.returncode == 0 and 'PASS_MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_VALIDATOR_DISPATCH_READY' in p.stdout
        add(checks, 'previous_language_surface_v2_validator_passes_after_ultrasafe_hotfix', ok, {'exit_code':p.returncode,'stdout_tail':p.stdout[-8000:],'stderr_tail':p.stderr[-4000:]})
        if not ok: errors.append('previous validator still does not pass after ultrasafe probe hotfix')
    prev, rerr = load_json(repo/PREVIOUS_RECEIPT) if (repo/PREVIOUS_RECEIPT).is_file() else ({}, 'missing')
    prev_ok = rerr is None and isinstance(prev, dict) and prev.get('verdict') == 'PASS_MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_VALIDATOR_DISPATCH_READY'
    add(checks, 'previous_language_surface_v2_receipt_is_pass_after_ultrasafe_hotfix', prev_ok, {'error':rerr,'verdict':prev.get('verdict') if isinstance(prev,dict) else None})
    if not prev_ok and not errors: errors.append('previous receipt is not PASS after ultrasafe hotfix')
    if isinstance(report_data, dict):
        if report_data.get('observed_required_failed'): warnings.append('Observed host-required tools failed in probe and are recorded as capability debt.')
        if report_data.get('optional_missing_or_failed'): warnings.append('Optional toolchains missing or failed and are recorded as capability debt.')
        if report_data.get('build_targets_detected_but_not_run'): warnings.append('Build targets were detected but not run by ultrasafe probe; strict build lanes remain separate.')
    if prev_ok:
        for w in prev.get('warnings', []) or []:
            if w not in warnings: warnings.append(w)
    verdict = 'PASS_MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_PROBE_ULTRASAFE_HOTFIX_READY' if not errors else 'FAIL_MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_PROBE_ULTRASAFE_HOTFIX'
    generated=utc(); summary={'summary_id':'mechanicus.language_surface_v2_toolchain_probe_ultrasafe_hotfix_summary.v0_2','task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'generated_at_utc':generated,'checks':checks,'errors':errors,'warnings':warnings}
    receipt={'receipt_id':'receipt.mechanicus.language_surface_v2_toolchain_probe_ultrasafe_hotfix.v0_2','task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'generated_at_utc':generated,'checks':checks,'errors':errors,'warnings':warnings,'probe':PROBE.as_posix(),'toolchain_report':TOOLCHAIN_REPORT.as_posix(),'previous_validator':PREVIOUS_VALIDATOR.as_posix(),'previous_receipt':PREVIOUS_RECEIPT.as_posix()}
    write_json(repo/SUMMARY, summary); write_json(repo/RECEIPT, receipt)
    (repo/REPORT).write_text(f"# MECHANICUS LANGUAGE SURFACE V2 TOOLCHAIN PROBE ULTRASAFE HOTFIX REPORT V0.2\n\ntask_id: `{TASK_ID}`  \nvalidator_id: `{VALIDATOR_ID}`  \nverdict: `{verdict}`  \ngenerated_at_utc: `{generated}`\n\n## Meaning\n\nThis hotfix installs an ultrasafe nonblocking toolchain probe. Missing/failing tools are capability debt, not fake pass and not early foundation blocker.\n\n## Checks\n\n" + '\n'.join(f"- `{c['status']}` — {c['name']}" for c in checks) + "\n\n## Warnings\n\n" + ('\n'.join(f"- {w}" for w in warnings) if warnings else '- none') + "\n\n## Errors\n\n" + ('\n'.join(f"- {e}" for e in errors) if errors else '- none') + "\n", encoding='utf-8')
    print(json.dumps({'task_id':TASK_ID,'validator_id':VALIDATOR_ID,'verdict':verdict,'receipt':RECEIPT.as_posix(),'summary':SUMMARY.as_posix(),'errors':errors,'warnings':warnings}, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith('PASS') else 1
if __name__ == '__main__': raise SystemExit(main())
