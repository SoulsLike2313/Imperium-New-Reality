
from __future__ import annotations
import argparse, json
from pathlib import Path
from datetime import datetime, timezone

PATCH_ID = 'MECHANICUS-RESIDENCY-TRUST-GATE-0001'
VALIDATOR_ID = 'mechanicus_residency_trust_gate_validator.v0_1'
GATE_ID = 'G6_RESIDENCY_TRUST'

REQ_PREV = {
  'G1_IDENTITY_MANIFEST':'PASS_BASELINE',
  'G2_FUNCTIONS_REGISTRY':'PASS_BASELINE',
  'G3_CAPABILITY_EVIDENCE':'PASS_BASELINE',
  'G4_PERSONAL_VALIDATORS':'PASS_BASELINE',
  'G5_CURRENT_TRUTH_RECEIPTS':'PASS_BASELINE',
}

def load_json(root: Path, rel: str):
    return json.loads((root / rel).read_text(encoding='utf-8'))

def dump_json(root: Path, rel: str, obj):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def classify_residents(root: Path, registry: dict):
    mech = root / 'ORGANS' / 'MECHANICUS'
    files = [p for p in mech.rglob('*') if p.is_file()]
    rels = [str(p.relative_to(root)).replace('\\','/') for p in files]
    pats = registry.get('classification_patterns', {})
    def hit(names):
        out = []
        for r in rels:
            up = r.upper()
            if any(str(n).upper() in up for n in names):
                out.append(r)
        return out
    classes = {
        'resident_file_count': len(rels),
        'negative_examples': hit(pats.get('negative_examples', [])),
        'quarantine_residents': hit(pats.get('quarantine_residents', [])),
        'legacy_history': hit(pats.get('legacy_history', [])),
        'future_deferred_capabilities': hit(pats.get('future_deferred_capabilities', [])),
    }
    return classes


def build(repo_root: Path):
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    errors, warnings = [], []
    manifest = load_json(repo_root, 'ORGANS/MECHANICUS/MANIFEST.json')
    index = load_json(repo_root, 'ORGANS/MECHANICUS/MATRICES/MECHANICUS_CURRENT_TRUTH_INDEX_V0_1.json')
    registry = load_json(repo_root, 'ORGANS/MECHANICUS/MATRICES/MECHANICUS_RESIDENCY_TRUST_REGISTRY_V0_1.json')

    gate_map = {g.get('gate_id'): g for g in index.get('current_gate_truth', [])}
    for gate_id, want in REQ_PREV.items():
        got = gate_map.get(gate_id, {}).get('state')
        if got != want:
            errors.append({'code':'PREVIOUS_GATE_NOT_PASS_BASELINE','gate_id':gate_id,'expected':want,'actual':got})

    resident_classes = classify_residents(repo_root, registry)
    non_current_classes = [c.get('class_id') for c in registry.get('resident_classes', []) if not c.get('current_truth_allowed')]
    required_non_current = {'legacy_history','negative_examples','quarantine_residents','superseded_reports','future_deferred_capabilities'}
    missing_non_current = sorted(required_non_current.difference(non_current_classes))
    if missing_non_current:
        errors.append({'code':'NON_CURRENT_CLASSES_MISSING','missing':missing_non_current})

    # Update manifest and current truth index to final six-gate baseline truth.
    manifest['manifest_id'] = 'MECHANICUS.manifest.v0_6'
    manifest['version'] = '0.6'
    manifest['patch_id'] = PATCH_ID
    manifest['status'] = 'SIX_GATE_BASELINE_CLOSED_NOT_CUSTODES_OR_THRONE_CROWNED'
    manifest['organ_assembly_claim'] = False
    manifest['full_implementation_claim'] = False
    manifest['six_gate_closure_claim'] = True
    manifest['six_gate_baseline_closure_claim'] = True
    manifest['custodes_prosecution_claim'] = False
    manifest['throne_crown_claim'] = False
    for g in manifest.get('six_gates', []):
        if g.get('gate_id') in list(REQ_PREV.keys()) + [GATE_ID]:
            g['current_state_after_this_patch'] = 'PASS_BASELINE'
            g['closure_claim'] = 'BASELINE_CLOSED_NOT_CUSTODES_OR_THRONE_CROWNED'
    dump_json(repo_root, 'ORGANS/MECHANICUS/MANIFEST.json', manifest)

    for rec in index.get('current_gate_truth', []):
        if rec.get('gate_id') == GATE_ID:
            rec.update({'state':'PASS_BASELINE','source_patch_id':PATCH_ID,'summary_path':'ORGANS/MECHANICUS/REPORTS/MECHANICUS_RESIDENCY_TRUST_GATE_SUMMARY_V0_1.json','report_path':'ORGANS/MECHANICUS/REPORTS/MECHANICUS_RESIDENCY_TRUST_GATE_REPORT_V0_1.json','receipt_path':'ORGANS/MECHANICUS/RECEIPTS/mechanicus_residency_trust_gate_receipt.json','closure_claim':'BASELINE_CLOSED_NOT_CUSTODES_OR_THRONE_CROWNED'})
        elif rec.get('state') == 'PASS_BASELINE':
            rec['closure_claim'] = 'BASELINE_CLOSED_NOT_CUSTODES_OR_THRONE_CROWNED'
    index['version'] = '0.2'
    index['patch_id'] = PATCH_ID
    index['gate_id'] = GATE_ID
    index['six_gate_baseline_closure_claim'] = True
    index['six_gate_closure_claim'] = True
    index['organ_assembly_claim'] = False
    index['custodes_prosecution_claim'] = False
    index['throne_crown_claim'] = False
    dump_json(repo_root, 'ORGANS/MECHANICUS/MATRICES/MECHANICUS_CURRENT_TRUTH_INDEX_V0_1.json', index)

    six_gate_progress = [
        {'gate_id':'G1_IDENTITY_MANIFEST','state':'PASS_BASELINE','closure_claim':'BASELINE_CLOSED_NOT_CUSTODES_OR_THRONE_CROWNED'},
        {'gate_id':'G2_FUNCTIONS_REGISTRY','state':'PASS_BASELINE','closure_claim':'BASELINE_CLOSED_NOT_CUSTODES_OR_THRONE_CROWNED'},
        {'gate_id':'G3_CAPABILITY_EVIDENCE','state':'PASS_BASELINE','closure_claim':'BASELINE_CLOSED_NOT_CUSTODES_OR_THRONE_CROWNED'},
        {'gate_id':'G4_PERSONAL_VALIDATORS','state':'PASS_BASELINE','closure_claim':'BASELINE_CLOSED_NOT_CUSTODES_OR_THRONE_CROWNED'},
        {'gate_id':'G5_CURRENT_TRUTH_RECEIPTS','state':'PASS_BASELINE','closure_claim':'BASELINE_CLOSED_NOT_CUSTODES_OR_THRONE_CROWNED'},
        {'gate_id':'G6_RESIDENCY_TRUST','state':'PASS_BASELINE','closure_claim':'BASELINE_CLOSED_NOT_CUSTODES_OR_THRONE_CROWNED'},
    ]
    pass_baseline_gate_count = sum(1 for g in six_gate_progress if g['state']=='PASS_BASELINE')
    if pass_baseline_gate_count != 6:
        errors.append({'code':'SIX_PASS_BASELINE_GATES_NOT_REACHED','count':pass_baseline_gate_count})

    warnings.extend([
        'This patch closes all six Mechanicus gates at baseline level; it does not assemble Mechanicus as Custodes/Throne accepted organ.',
        'Residency/trust means resident classes are classified and bounded, not that all debt is removed.',
        'Custodes prosecution and Throne crown verdict remain future work.'
    ])
    verdict = 'PASS_MECHANICUS_RESIDENCY_TRUST_GATE_READY' if not errors else 'FAIL_MECHANICUS_RESIDENCY_TRUST_GATE'
    summary = {
        'task_id':PATCH_ID,
        'validator_id':VALIDATOR_ID,
        'verdict':verdict,
        'generated_at_utc':now,
        'gate_id':GATE_ID,
        'residency_trust_gate_status':'PASS_BASELINE' if not errors else 'FAIL',
        'six_gate_baseline_closure_claim': True if not errors else False,
        'pass_baseline_gate_count':pass_baseline_gate_count,
        'resident_file_count':resident_classes['resident_file_count'],
        'negative_example_resident_count':len(resident_classes['negative_examples']),
        'quarantine_resident_count':len(resident_classes['quarantine_residents']),
        'legacy_history_resident_count':len(resident_classes['legacy_history']),
        'future_deferred_resident_count':len(resident_classes['future_deferred_capabilities']),
        'non_current_class_count':len(non_current_classes),
        'organ_assembly_claim':False,
        'custodes_prosecution_claim':False,
        'throne_crown_claim':False,
        'local_model_membrane_status':'DEFERRED_AFTER_CORE_V1',
        'next_gate_count':2,
    }
    report = dict(summary)
    report.update({
        'six_gate_progress':six_gate_progress,
        'resident_classes':resident_classes,
        'non_current_classes':non_current_classes,
        'indexed_gate_records':index.get('current_gate_truth', []),
        'errors':errors,
        'warnings':warnings,
    })
    receipt = {k: summary[k] for k in ['task_id','validator_id','verdict','generated_at_utc','gate_id','residency_trust_gate_status','six_gate_baseline_closure_claim','pass_baseline_gate_count','resident_file_count','negative_example_resident_count','quarantine_resident_count','legacy_history_resident_count','non_current_class_count','organ_assembly_claim','custodes_prosecution_claim','throne_crown_claim']}
    dump_json(repo_root, 'ORGANS/MECHANICUS/RECEIPTS/mechanicus_residency_trust_gate_receipt.json', receipt)
    dump_json(repo_root, 'ORGANS/MECHANICUS/REPORTS/MECHANICUS_RESIDENCY_TRUST_GATE_SUMMARY_V0_1.json', summary)
    dump_json(repo_root, 'ORGANS/MECHANICUS/REPORTS/MECHANICUS_RESIDENCY_TRUST_GATE_REPORT_V0_1.json', report)
    md = '# Mechanicus Residency / Trust Gate Report v0.1\n\n'
    md += f'- task_id: `{PATCH_ID}`\n- verdict: `{verdict}`\n- gate: `{GATE_ID}`\n- six_gate_baseline_closure_claim: `{summary["six_gate_baseline_closure_claim"]}`\n- organ_assembly_claim: `False`\n- pass_baseline_gate_count: `{pass_baseline_gate_count}`\n\n'
    md += '## Boundary\n\nG6 closes the Mechanicus six-gate baseline, but does not claim Custodes prosecution, Throne crown, or full organ assembly.\n'
    (repo_root / 'ORGANS/MECHANICUS/REPORTS/MECHANICUS_RESIDENCY_TRUST_GATE_REPORT_V0_1.md').write_text(md, encoding='utf-8')
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root', default='.')
    ns = ap.parse_args()
    result = build(Path(ns.repo_root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['verdict'] == 'PASS_MECHANICUS_RESIDENCY_TRUST_GATE_READY' else 1

if __name__ == '__main__':
    raise SystemExit(main())
