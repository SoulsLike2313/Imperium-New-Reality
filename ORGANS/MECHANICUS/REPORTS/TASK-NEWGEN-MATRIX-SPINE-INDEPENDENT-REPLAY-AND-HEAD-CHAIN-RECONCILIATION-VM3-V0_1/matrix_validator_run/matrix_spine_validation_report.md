# Matrix Spine Validation Report — TASK-NEWGEN-MATRIX-SPINE-RECEIPT-HEAD-CONSISTENCY-AND-INDEPENDENT-REPLAY-GATE-VM3-V0_1

Timestamp (UTC): 2026-05-30T16:48:40Z

## Summary
- Matrix files scanned: 29
- Matrix parse failures: 0
- FAIL: 0
- WARN: 0
- INFO: 0
- Negative fixtures checked: 24
- Verdict: PASS

## Negative Fixture Evidence
- matrix owner missing: expected `MATRIX_OWNER_MISSING` -> detected
- matrix status outside vocabulary: expected `MATRIX_STATUS_INVALID` -> detected
- matrix support_organs missing: expected `MATRIX_SUPPORT_ORGANS_INVALID` -> detected
- matrix id missing from matrix spine index: expected `MATRIX_ID_NOT_IN_INDEX` -> detected
- malformed json fixture: expected `NEGATIVE_FIXTURE_PARSE_FAIL` -> detected
- stale receipt detection: expected `STALE_RECEIPT_DETECTED` -> detected
- missing implementation head in closure receipt: expected `CAP_EMPTY_IMPLEMENTATION_HEAD` -> detected
- empty closure bundle head in closure receipt: expected `CAP_EMPTY_CLOSURE_BUNDLE_HEAD` -> detected
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
- missing remote head in closure receipt: expected `CAP_EMPTY_REMOTE_HEAD` -> detected
- self-score high without independent replay: expected `CAP_NO_INDEPENDENT_REPLAY` -> detected
- clean pass with CAP_NO_INDEPENDENT_REPLAY: expected `CAP_NO_INDEPENDENT_REPLAY` -> detected
- missing claim ledger in final closure verifier: expected `CAP_CLAIM_LEDGER_MISSING` -> detected
- excluded runtime output without hash: expected `CAP_RUNTIME_EXCLUDED_OUTPUT_WITHOUT_HASH` -> detected
- final receipt with implementation and closure mixed: expected `CAP_HEADS_MIXED_OR_AMBIGUOUS` -> detected

## Findings
- No findings.

## Replay
- `bash IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.sh`
- `pwsh IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.ps1`

