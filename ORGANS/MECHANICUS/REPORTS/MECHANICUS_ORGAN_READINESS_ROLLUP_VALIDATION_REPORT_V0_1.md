# MECHANICUS ORGAN READINESS ROLLUP VALIDATION REPORT V0.1

task_id: `MECHANICUS-ORGAN-READINESS-ROLLUP-0001`  
validator_id: `mechanicus_organ_readiness_rollup_validator.v0_1`  
verdict: `PASS_MECHANICUS_ORGAN_READINESS_ROLLUP_READY`  
generated_at_utc: `2026-07-05T22:11:45Z`

## Meaning

This validator proves the readiness rollup exists, is script-generated, contains required sections, and does not falsely claim Mechanicus assembly closure.

It does not prove Mechanicus is assembled.

## Checks

- `PASS` — rollup_law_exists_and_declares_required_boundaries
- `PASS` — rollup_matrix_exists_and_declares_required_boundaries
- `PASS` — custodes_prosecutor_matrix_exists_and_declares_required_boundaries
- `PASS` — throne_crown_gate_matrix_exists_and_declares_required_boundaries
- `PASS` — rollup_builder_exists
- `PASS` — rollup_builder_runs_and_writes_outputs
- `PASS` — rollup_json_parse
- `PASS` — rollup_contains_required_sections
- `PASS` — rollup_verdict_is_not_assembled
- `PASS` — rollup_blocks_mechanicus_assembled_claim
- `PASS` — assembly_gate_map_present_and_non_closing
- `PASS` — baseline_capabilities_visible
- `PASS` — no_fake_green_guard_complete
- `PASS` — local_model_membrane_marked_deferred_not_dependency

## Warnings

- Mechanicus assembly blockers visible: 13

## Errors

- none

## Runtime outputs

- `ORGANS/MECHANICUS/REPORTS/MECHANICUS_ORGAN_READINESS_ROLLUP_V0_1.json`
- `ORGANS/MECHANICUS/REPORTS/MECHANICUS_ORGAN_READINESS_ROLLUP_V0_1.md`
- `ORGANS/MECHANICUS/REPORTS/MECHANICUS_ORGAN_READINESS_ROLLUP_SUMMARY_V0_1.json`
- `ORGANS/MECHANICUS/RECEIPTS/mechanicus_organ_readiness_rollup_receipt.json`
