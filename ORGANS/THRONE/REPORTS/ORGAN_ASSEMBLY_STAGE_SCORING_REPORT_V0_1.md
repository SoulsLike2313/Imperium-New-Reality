# ORGAN ASSEMBLY STAGE SCORING REPORT V0.1

task_id: `THRONE-ORGAN-ASSEMBLY-STAGE-SCORING-INTEGRATION-0001`  
validator_id: `throne_organ_assembly_stage_scoring_validator.v0_1`  
verdict: `PASS_STAGE_SCORING_INTEGRATED`  
generated_at_utc: `2026-07-01T20:21:00Z`  
repo_head: `ef85a546f015cf968e58d2a4a75ea1df0145eb70`

## Meaning

This patch teaches the Throne to measure organ maturity by separate truth stages.

It does not assemble organs and does not raise operational/trust/no-core-mutation readiness.

## Stage law

```text
profile_baseline != duty_defined != assembly_target_defined != rule_validated != action_proven != trust_proven != throne_confirmed != organ_assembled
```

## Global stage scores

- profile_baseline_score: `100.0`
- duty_defined_score: `100.0`
- assembly_target_defined_score: `100.0`
- rule_validated_score: `0.0`
- action_proven_score: `0.0`
- trust_proven_score: `0.0`
- throne_confirmed_score: `0.0`
- organ_assembled_score: `0.0`
- tui_launcher_presence_score: `0.0`
- organ_tools_docs_functions_score: `0.0`
- personal_flow_validators_score: `0.0`
- personal_integrity_validators_score: `0.0`
- custodes_organ_validators_score: `0.0`
- throne_organ_validators_score: `0.0`
- red_team_layer_score: `0.0`
- blue_team_layer_score: `0.0`
- red_team_score: `0.0`
- blue_team_score: `0.0`
- organ_truth_maturity_score: `40.0`

## Interpretation

`duty_defined_score` and `assembly_target_defined_score` may be high because the laws and targets exist.

`organ_assembled_score`, `red_team_score`, and `blue_team_score` must remain low/zero until actual validators, receipts, and Crown confirmations exist.

## Organs

- `ASTRONOMICON` — maturity `40.0`, assembled `0.0`, red `0.0`, blue `0.0`, errors `0`
- `ADMINISTRATUM` — maturity `40.0`, assembled `0.0`, red `0.0`, blue `0.0`, errors `0`
- `DOCTRINARIUM` — maturity `40.0`, assembled `0.0`, red `0.0`, blue `0.0`, errors `0`
- `MECHANICUS` — maturity `40.0`, assembled `0.0`, red `0.0`, blue `0.0`, errors `0`
- `INQUISITION` — maturity `40.0`, assembled `0.0`, red `0.0`, blue `0.0`, errors `0`
- `CUSTODES` — maturity `40.0`, assembled `0.0`, red `0.0`, blue `0.0`, errors `0`
- `STRATEGIUM` — maturity `40.0`, assembled `0.0`, red `0.0`, blue `0.0`, errors `0`
- `SCHOLA_IMPERIALIS` — maturity `40.0`, assembled `0.0`, red `0.0`, blue `0.0`, errors `0`
- `OFFICIO_AGENTIS` — maturity `40.0`, assembled `0.0`, red `0.0`, blue `0.0`, errors `0`
- `THRONE` — maturity `40.0`, assembled `0.0`, red `0.0`, blue `0.0`, errors `0`

## Checks

- `PASS` — THRONE_ORGAN_ASSEMBLY_STAGE_SCORING_MATRIX_V0_1.json_exists
- `PASS` — THRONE_ORGAN_ASSEMBLY_STANDARD_MATRIX_V0_1.json_exists
- `PASS` — ORGAN_DUTY_CONTRACT_REQUIRED_FIELDS_MATRIX_V0_1.json_exists
- `PASS` — throne_organ_assembly_stage_scoring_receipt.schema.json_exists
- `PASS` — ORGAN_ASSEMBLY_STAGE_SCORING_V0_1.md_exists
- `PASS` — THRONE_ORGAN_ASSEMBLY_STAGE_SCORING_MATRIX_V0_1.json_parses
- `PASS` — THRONE_ORGAN_ASSEMBLY_STANDARD_MATRIX_V0_1.json_parses
- `PASS` — ORGAN_DUTY_CONTRACT_REQUIRED_FIELDS_MATRIX_V0_1.json_parses
- `PASS` — throne_organ_assembly_stage_scoring_receipt.schema.json_parses
- `PASS` — stage_scoring_hard_rules_present
- `PASS` — all_organs_have_duty_and_assembly_stage_inputs
- `PASS` — no_organ_assembled_claim_from_target_definition
- `PASS` — red_blue_not_claimed_before_proof
- `PASS` — operational_score_not_raised_by_this_patch
- `PASS` — trust_score_not_raised_by_this_patch
- `PASS` — no_core_mutation_score_not_raised_by_this_patch
- `PASS` — organ_assembled_score_delta_not_allowed

## Warnings

- none

## Errors

- none

## Outputs

- `ORGANS/THRONE/RECEIPTS/organ_assembly_stage_scoring_receipt.json`
- `ORGANS/THRONE/REPORTS/ORGAN_ASSEMBLY_STAGE_SCORING_SUMMARY_V0_1.json`
- `ORGANS/THRONE/REPORTS/ORGAN_ASSEMBLY_STAGE_SCORING_SUMMARY_V0_1.csv`
