# Negative Fixtures Report

Total fixtures declared: 13

## Detection Results
- NF01 matrix owner missing: PASS (expected `MATRIX_OWNER_MISSING`)
- NF02 matrix status outside vocabulary: PASS (expected `MATRIX_STATUS_INVALID`)
- NF03 matrix support_organs missing: PASS (expected `MATRIX_SUPPORT_ORGANS_INVALID`)
- NF04 matrix id missing from matrix spine index: PASS (expected `MATRIX_ID_NOT_IN_INDEX`)
- NF05 malformed json fixture: PASS (expected `NEGATIVE_FIXTURE_PARSE_FAIL`)
- NF06 stale receipt detection: PASS (expected `STALE_RECEIPT_DETECTED`)
- NF07 missing implementation head in closure receipt: PASS (expected `CLOSURE_RECEIPT_IMPLEMENTATION_HEAD_MISSING`)
- NF08 missing closure head in closure receipt: PASS (expected `CLOSURE_RECEIPT_CLOSURE_HEAD_MISSING`)
- NF09 fake pass with no red-team receipt: PASS (expected `CLOSURE_RECEIPT_RED_TEAM_MISSING`)
- NF10 script-first capability without replay command: PASS (expected `CAPABILITY_SPLIT_SCRIPT_FIRST_REPLAY_MISSING`)
- NF11 unclassified runtime output kind: PASS (expected `RUNTIME_OUTPUT_UNCLASSIFIED`)
- NF12 owner-facing language contract missing: PASS (expected `OWNER_LANGUAGE_CONTRACT_MISSING`)
- NF13 red-team verdict schema required field missing: PASS (expected `RED_TEAM_SCHEMA_REQUIRED_MISSING`)

## Gate
- Requirement `CAP_NEGATIVE_FIXTURES_LT_10`: satisfied (13 fixtures).
- Detection replay evidence: matrix validator summary/report in `matrix_validator_run/`.
