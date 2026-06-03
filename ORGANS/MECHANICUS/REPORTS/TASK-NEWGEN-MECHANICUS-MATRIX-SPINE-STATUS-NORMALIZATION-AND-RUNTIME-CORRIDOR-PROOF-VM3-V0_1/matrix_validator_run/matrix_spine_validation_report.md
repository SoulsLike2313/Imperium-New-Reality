# Matrix Spine Validation Report — TASK-NEWGEN-MECHANICUS-MATRIX-SPINE-STATUS-NORMALIZATION-AND-RUNTIME-CORRIDOR-PROOF-VM3-V0_1

Timestamp (UTC): 2026-05-29T23:59:43Z

## Summary
- Matrix files scanned: 29
- Matrix parse failures: 0
- FAIL: 0
- WARN: 0
- INFO: 0
- Negative fixtures checked: 13
- Verdict: PASS

## Negative Fixture Evidence
- matrix owner missing: expected `MATRIX_OWNER_MISSING` -> detected
- matrix status outside vocabulary: expected `MATRIX_STATUS_INVALID` -> detected
- matrix support_organs missing: expected `MATRIX_SUPPORT_ORGANS_INVALID` -> detected
- matrix id missing from matrix spine index: expected `MATRIX_ID_NOT_IN_INDEX` -> detected
- malformed json fixture: expected `NEGATIVE_FIXTURE_PARSE_FAIL` -> detected
- stale receipt detection: expected `STALE_RECEIPT_DETECTED` -> detected
- missing implementation head in closure receipt: expected `CLOSURE_RECEIPT_IMPLEMENTATION_HEAD_MISSING` -> detected
- missing closure head in closure receipt: expected `CLOSURE_RECEIPT_CLOSURE_HEAD_MISSING` -> detected
- fake pass with no red-team receipt: expected `CLOSURE_RECEIPT_RED_TEAM_MISSING` -> detected
- script-first capability without replay command: expected `CAPABILITY_SPLIT_SCRIPT_FIRST_REPLAY_MISSING` -> detected
- unclassified runtime output kind: expected `RUNTIME_OUTPUT_UNCLASSIFIED` -> detected
- owner-facing language contract missing: expected `OWNER_LANGUAGE_CONTRACT_MISSING` -> detected
- red-team verdict schema required field missing: expected `RED_TEAM_SCHEMA_REQUIRED_MISSING` -> detected

## Findings
- No findings.

## Replay
- `bash IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.sh`
- `pwsh IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.ps1`

