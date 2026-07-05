# MECHANICUS JSON EVIDENCE STRICT LANE REPORT V0.1

tool_id: `mechanicus_json_evidence_strict_lane_scanner.v0_1`  
verdict: `PASS_JSON_EVIDENCE_CANONICAL_STRICT_CLEAN_WITH_CLASSIFIED_DEBT`  
lane_state: `LANE_READY_BASELINE`  
generated_at_utc: `2026-07-05T15:04:44Z`

## Counts

- files_checked: `3642`
- parse_error_count: `3`
- canonical_parse_debt_count: `0`
- expected_negative_fixture_count: `2`
- quarantine_parse_debt_count: `1`

## Canonical parse debt

- none

## Expected negative fixtures

- `ORGANS/ADMINISTRATUM/BUNDLE_GATE/FIXTURES/v0_2_malformed_required_json/CLAIM_LEDGER.json` — Expecting property name enclosed in double quotes: line 2 column 1 (char 2)
- `SUPPORT/COMMON_IMPERIUM_SUPPORT/ROOT_IMPORTED_COMMON_SUPPORT/MATRIX_SPINE/FIXTURES/invalid_malformed_json_matrix.json` — Expecting property name enclosed in double quotes: line 5 column 1 (char 111)

## Quarantine parse debt

- `SUPPORT/QUARANTINE/ROOT_REPORTS_PENDING_HARNESS_INTAKE/REPORTS/TASK-20260521-NEWGEN-ASTRONOMICON-TASK-FORMATION-PC-V0_1/STEP_PROOF_RECORDS.jsonl` — Extra data: line 1 column 741 (char 740)

## Boundary

```text
This proves canonical JSON/JSONL parse cleanliness only.
It does not prove schema correctness, semantic truth, or receipt honesty.
```
