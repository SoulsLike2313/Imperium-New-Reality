# Matrix Spine Validation Report — TASK-NEWGEN-MATRIX-SPINE-CLOSURE-PROVENANCE-CORRIDOR-NAMING-AND-REVIEW-PIPELINE-HARDENING-VM3-V0_1

Timestamp (UTC): 2026-05-30T14:58:50Z

## Summary
- Matrix files scanned: 29
- Matrix parse failures: 0
- FAIL: 0
- WARN: 0
- INFO: 0
- Negative fixtures checked: 18
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
- unclassified runtime output: expected `CAP_RUNTIME_OUTPUT_UNCLASSIFIED` -> detected
- owner-facing language contract missing: expected `OWNER_LANGUAGE_CONTRACT_MISSING` -> detected
- red-team verdict schema required field missing: expected `RED_TEAM_SCHEMA_REQUIRED_MISSING` -> detected
- final closure verifier missing final_verifier_head: expected `CAP_NO_FINAL_CLOSURE_VERIFIER` -> detected
- next pipeline handoff missing target commit: expected `CAP_NO_NEXT_PIPELINE_HANDOFF` -> detected
- untyped runtime corridor claim: expected `CAP_UNTYPED_RUNTIME_CLAIM` -> detected
- synthetic proof claimed as real runtime corridor: expected `CAP_SYNTHETIC_CLAIMED_AS_REAL` -> detected
- warp corridor claimed without unlock: expected `CAP_WARP_CLAIMED_WITHOUT_UNLOCK` -> detected

## Findings
- No findings.

## Replay
- `bash IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.sh`
- `pwsh IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.ps1`

