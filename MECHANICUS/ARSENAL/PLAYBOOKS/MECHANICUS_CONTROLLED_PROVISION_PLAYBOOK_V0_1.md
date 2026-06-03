# MECHANICUS CONTROLLED PROVISION PLAYBOOK V0.1

## Purpose

Repeatable owner-approved tool provisioning in bounded PC-local Mechanicus scope:

- detect first;
- install only approved packages when missing;
- validate and write receipts;
- update capability cards from evidence;
- sync registry and emit compact reports.

## Guardrails

1. Run truth checks first (`git status`, `git rev-parse HEAD`, branch, remote ref).
2. Require dossier + scope approval + `GATE_ACK` before edits.
3. Install only approved packages with `python -m pip install --user ...`.
4. No forbidden lanes: pyright, React/Vite creation, Playwright browser install, LLM/cloud activation, secrets/API keys.
5. Never enable pre-commit hooks automatically.
6. Update cards/registry only if receipts prove validation.
7. Run fake-CANON detector and cleanliness reports before final verdict.

## Standard Execution

1. `python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_controlled_provision_runner_v0_1.py`
2. Validate JSON artifacts in current task report folder.
3. Verify `capability_status_change_report.json` and `registry_sync_report.json`.
4. Check `fake_canon_detector_report.json` and `inquisition_cleanliness_report.json`.
5. Ensure final report and closure receipt are present.

## Evidence Bundle

Required minimum:

- `tool_detection_report.json`
- `controlled_provision_results.json`
- `install_receipts_index.json`
- `validation_receipts_index.json`
- `capability_status_change_report.json`
- `registry_sync_report.json`
- `capability_scope_code_quality_report.json`
- `fake_canon_detector_report.json`
- `inquisition_cleanliness_report.json`
- `administratum_evidence_map.json`
- `ghost_evolve_provision_training_proof.json`
- `closure_receipt.json`
- `FINAL_REPORT.md`

## Replay Notes

- Runner is safe for repeated runs: already-present approved tools are not reinstalled.
- Receipts are always regenerated for current task timestamp.
- Registry rebuild reflects current card statuses each run.
- If any approved tool remains missing, verdict may be `PASS_WITH_WARNINGS` with explicit reason.
