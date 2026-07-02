# THRONE TARGET GAP REPORT V0.5 — ORGAN IMPLEMENTATION SPLIT

task_id: `THRONE-TARGET-GAP-VALIDATOR-0001`  
upgrade_id: `THRONE-TARGET-GAP-ORGAN-IMPLEMENTATION-SPLIT-0001`  
validator_id: `throne_target_gap_validator.v0_5_organ_implementation_split`  
verdict: `PASS_MEASURED`  
mode: `MEASURE_ONLY`  
validation_model: `TARGET_V1_VS_CURRENT_REALITY_WITH_ORGAN_IMPLEMENTATION_SPLIT`  
generated_at_utc: `2026-07-02T12:06:34Z`

## Global scores

- core_readiness_score: `53.2`
- throne_readiness_score: `97.0`
- great_nine_readiness_score: `55.22`
- lowest_organ_readiness_score: `47.75`

## Great Nine split

- great_nine_profile_baseline_score: `100.0`
- great_nine_structural_score: `100.0`
- great_nine_operational_score: `32.67`
- great_nine_trust_score: `15.56`

## Core v1 strict split

- core_v1_target_definition_score: `100.0`
- core_v1_operational_evidence_score: `44.75`
- core_v1_workflow_readiness_score: `75.0`
- core_v1_trust_readiness_score: `35.0`
- core_v1_human_visibility_score: `40.0`
- core_v1_no_core_mutation_evidence_score: `0.0`

## Interpretation

A passported organ is not a fully implemented organ.

Profile validators and profile receipts count toward organ baseline, not operational implementation.

## Organ readiness, lowest first

- `DOCTRINARIUM`: readiness `47.75` (profile `100.0`, structural `100.0`, operational `15.0`, trust `10.0`)
- `CUSTODES`: readiness `47.75` (profile `100.0`, structural `100.0`, operational `15.0`, trust `10.0`)
- `STRATEGIUM`: readiness `47.75` (profile `100.0`, structural `100.0`, operational `15.0`, trust `10.0`)
- `SCHOLA_IMPERIALIS`: readiness `47.75` (profile `100.0`, structural `100.0`, operational `15.0`, trust `10.0`)
- `OFFICIO_AGENTIS`: readiness `57.55` (profile `100.0`, structural `100.0`, operational `43.0`, trust `10.0`)
- `MECHANICUS`: readiness `59.25` (profile `100.0`, structural `100.0`, operational `30.0`, trust `35.0`)
- `ADMINISTRATUM`: readiness `59.65` (profile `100.0`, structural `100.0`, operational `49.0`, trust `10.0`)
- `ASTRONOMICON`: readiness `64.55` (profile `100.0`, structural `100.0`, operational `63.0`, trust `10.0`)
- `INQUISITION`: readiness `65.0` (profile `100.0`, structural `100.0`, operational `49.0`, trust `35.0`) capped: [{'reason': 'operational<50', 'cap': 65.0}]

## Next attention areas

4. **Great Nine operational proofs** — Great Nine profiles exist, but organ-specific operational receipts are weak. → `GREAT-NINE-OPERATIONAL-PROOF-0001`
5. **Great Nine trust proofs** — Organs need Custodes/Inquisition/Throne trust receipts beyond self-profile receipts. → `GREAT-NINE-TRUST-PROOF-0001`
6. **No-core-mutation proof** — Need before/after census and allowed-return receipts. → `THRONE-NO-CORE-MUTATION-PROOF-0001`
7. **Human visibility implementation** — TUI/dashboard target exists, but implementation artifacts are not enough. → `THRONE-HUMAN-VISIBILITY-PROOF-0001`
20. **CUSTODES operational implementation** — CUSTODES operational score is 15.0%. → `CUSTODES-OPERATIONAL-PROOF-0001`
21. **CUSTODES trust proof** — CUSTODES trust score is 10.0%. → `CUSTODES-TRUST-PROOF-0001`

## Checks

- `PASS` — required_inputs_exist
- `PASS` — input_json_parse
- `PASS` — census_has_residents
- `PASS` — target_definition_measured
- `PASS` — organ_implementation_split_matrix_present
- `PASS` — profile_baseline_separate_from_operational
- `PASS` — great_nine_no_false_near_complete
- `PASS` — near_v1_core_guard_active

## Warnings

- none

## Errors

- none

## Outputs

- `ORGANS/THRONE/RECEIPTS/throne_target_gap_receipt.json`
- `ORGANS/THRONE/REPORTS/THRONE_ORGAN_IMPLEMENTATION_BREAKDOWN_V0_1.json`
- `ORGANS/THRONE/REPORTS/THRONE_ORGAN_IMPLEMENTATION_BREAKDOWN_V0_1.csv`
- `ORGANS/THRONE/REPORTS/THRONE_CORE_V1_OPERATIONAL_BREAKDOWN_V0_1.json`
- `ORGANS/THRONE/REPORTS/THRONE_CORE_V1_OPERATIONAL_BREAKDOWN_V0_1.csv`
- `ORGANS/THRONE/REPORTS/THRONE_CORE_V1_READINESS_BREAKDOWN_V0_1.json`
- `ORGANS/THRONE/REPORTS/THRONE_CORE_V1_READINESS_BREAKDOWN_V0_1.csv`
- `ORGANS/THRONE/REPORTS/THRONE_ORGAN_READINESS_TABLE_V0_1.csv`
- `ORGANS/THRONE/REPORTS/THRONE_NEXT_ATTENTION_AREAS_V0_1.json`
