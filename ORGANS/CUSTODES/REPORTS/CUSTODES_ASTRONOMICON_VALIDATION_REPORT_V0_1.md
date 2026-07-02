# CUSTODES ASTRONOMICON VALIDATION REPORT V0.2

task_id: `CUSTODES-ASTRONOMICON-VALIDATION-INVOKE-CONTRACT-FIX-0001`  
validator_id: `custodes_astronomicon_validation_invoke_contract_fix_validator.v0_1`  
verdict: `PASS_CUSTODES_ASTRONOMICON_VALIDATION_READY`  
generated_at_utc: `2026-07-02T11:14:42Z`  
custodes_validation_score: `100.0`

## Meaning

Custodes now prosecutes Astronomicon validators through explicit/adaptive invocation contracts.

This fixes false indictment caused by calling a validator with the wrong CLI shape.

## Checks

- `PASS` — custodes_audit_astronomicon.py_exists
- `PASS` — CUSTODES_VALIDATOR_INVOKE_CONTRACTS_V0_1.json_exists
- `PASS` — invoke_contract_matrix_parses
- `PASS` — invoke_contracts_include_lifecycle_foundation_validator
- `PASS` — custodes_audit_tool_runs
- `PASS` — custodes_audit_summary_parses
- `PASS` — custodes_audit_verdict_pass
- `PASS` — all_astronomicon_validators_pass_under_custodes
- `PASS` — custodes_indictments_absent
- `PASS` — throne_confirmation_score_remains_zero

## Errors

- none

## Not claimed

- Throne verdict
- organ assembled
