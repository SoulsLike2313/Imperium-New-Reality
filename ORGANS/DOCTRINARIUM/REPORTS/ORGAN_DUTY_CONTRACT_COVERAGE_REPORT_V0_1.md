# ORGAN DUTY CONTRACT COVERAGE REPORT V0.1

task_id: `DOCTRINARIUM-ORGAN-DUTY-CONTRACT-SCHEMA-0001`  
validator_id: `organ_duty_contract_coverage_validator.v0_1`  
verdict: `PASS_DUTY_CONTRACTS_DEFINED`  
generated_at_utc: `2026-06-30T15:19:09Z`  
repo_head: `947c63ae7ce07706c0668d7308e0f01c8514b9cf`

## Meaning

This patch defines what each organ must be responsible for before operational proof is possible.

It does **not** claim the organs are operationally proven.

## Stage law

```text
profile_baseline != duty_defined != rule_validated != action_proven != trust_proven != throne_confirmed
```

## Scores

- organ_count: `10`
- pass_count: `10`
- duty_defined_score: `100.0`
- operational_score_delta_allowed: `False`
- trust_score_delta_allowed: `False`
- no_core_mutation_score_delta_allowed: `False`

## Organs

- `ASTRONOMICON` — `PASS`; errors: 0
- `ADMINISTRATUM` — `PASS`; errors: 0
- `DOCTRINARIUM` — `PASS`; errors: 0
- `MECHANICUS` — `PASS`; errors: 0
- `INQUISITION` — `PASS`; errors: 0
- `CUSTODES` — `PASS`; errors: 0
- `STRATEGIUM` — `PASS`; errors: 0
- `SCHOLA_IMPERIALIS` — `PASS`; errors: 0
- `OFFICIO_AGENTIS` — `PASS`; errors: 0
- `THRONE` — `PASS`; errors: 0

## Checks

- `PASS` — organ_duty_contract.schema.json_exists
- `PASS` — ORGAN_DUTY_CONTRACT_REQUIRED_FIELDS_MATRIX_V0_1.json_exists
- `PASS` — THRONE_ORGAN_TRUTH_STAGE_MATRIX_V0_1.json_exists
- `PASS` — all_organ_contracts_exist_and_parse
- `PASS` — duty_defined_does_not_claim_action_or_trust
- `PASS` — throne_truth_stage_matrix_has_fake_green_law
- `PASS` — operational_score_not_raised_by_this_patch
- `PASS` — trust_score_not_raised_by_this_patch
- `PASS` — no_core_mutation_score_not_raised_by_this_patch

## Warnings

- none

## Errors

- none

## Outputs

- `ORGANS/DOCTRINARIUM/RECEIPTS/organ_duty_contract_coverage_receipt.json`
- `ORGANS/DOCTRINARIUM/REPORTS/ORGAN_DUTY_CONTRACT_SUMMARY_V0_1.json`
- `ORGANS/DOCTRINARIUM/REPORTS/ORGAN_DUTY_CONTRACT_SUMMARY_V0_1.csv`
