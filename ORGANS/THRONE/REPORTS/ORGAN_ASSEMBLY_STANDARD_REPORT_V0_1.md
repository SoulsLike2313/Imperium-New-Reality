# ORGAN ASSEMBLY STANDARD REPORT V0.1

task_id: `THRONE-ORGAN-ASSEMBLY-STANDARD-0001`  
validator_id: `throne_organ_assembly_standard_validator.v0_1`  
verdict: `PASS_ORGAN_ASSEMBLY_STANDARD_DEFINED`  
generated_at_utc: `2026-07-01T13:13:52Z`  
repo_head: `d8fecad03f7e5ed9093b1c9a5e35d2b535193d7c`

## Meaning

This patch defines what it means to raise an organ into service.

It does not assemble organs.

## Required assembly gates

1. `tui_launcher_presence`
2. `organ_tools_docs_functions`
3. `personal_flow_validators`
4. `personal_integrity_validators`
5. `custodes_organ_validators`
6. `throne_organ_validators`
7. `red_team_layer`
8. `blue_team_layer`

## Stage law

```text
profile_baseline != duty_defined != assembly_target_defined != rule_validated != action_proven != trust_proven != throne_confirmed != organ_assembled
```

## Scores

- organ_assembly_target_defined_score: `100.0`
- organ_assembled_score: `0.0`
- operational_score_delta_allowed: `False`
- trust_score_delta_allowed: `False`
- no_core_mutation_score_delta_allowed: `False`

## Organs

- `ASTRONOMICON` — `PASS`; defined_gates `8`; proven_gates `0`; errors `0`
- `ADMINISTRATUM` — `PASS`; defined_gates `8`; proven_gates `0`; errors `0`
- `DOCTRINARIUM` — `PASS`; defined_gates `8`; proven_gates `0`; errors `0`
- `MECHANICUS` — `PASS`; defined_gates `8`; proven_gates `0`; errors `0`
- `INQUISITION` — `PASS`; defined_gates `8`; proven_gates `0`; errors `0`
- `CUSTODES` — `PASS`; defined_gates `8`; proven_gates `0`; errors `0`
- `STRATEGIUM` — `PASS`; defined_gates `8`; proven_gates `0`; errors `0`
- `SCHOLA_IMPERIALIS` — `PASS`; defined_gates `8`; proven_gates `0`; errors `0`
- `OFFICIO_AGENTIS` — `PASS`; defined_gates `8`; proven_gates `0`; errors `0`
- `THRONE` — `PASS`; defined_gates `8`; proven_gates `0`; errors `0`

## Checks

- `PASS` — organ_assembly_target.schema.json_exists
- `PASS` — THRONE_ORGAN_ASSEMBLY_STANDARD_MATRIX_V0_1.json_exists
- `PASS` — CUSTODES_ORGAN_ASSEMBLY_AUDIT_MATRIX_V0_1.json_exists
- `PASS` — ORGAN_RED_BLUE_TEAM_STANDARD_MATRIX_V0_1.json_exists
- `PASS` — ORGAN_ASSEMBLY_STANDARD_V0_1.md_exists
- `PASS` — organ_assembly_target.schema.json_parses
- `PASS` — THRONE_ORGAN_ASSEMBLY_STANDARD_MATRIX_V0_1.json_parses
- `PASS` — CUSTODES_ORGAN_ASSEMBLY_AUDIT_MATRIX_V0_1.json_parses
- `PASS` — ORGAN_RED_BLUE_TEAM_STANDARD_MATRIX_V0_1.json_parses
- `PASS` — organ_duty_contracts_exist_before_assembly_standard
- `PASS` — all_organ_assembly_targets_defined
- `PASS` — assembly_target_does_not_claim_assembly
- `PASS` — assembly_matrix_separates_target_from_assembly
- `PASS` — operational_score_not_raised_by_this_patch
- `PASS` — trust_score_not_raised_by_this_patch
- `PASS` — no_core_mutation_score_not_raised_by_this_patch
- `PASS` — red_blue_layer_required_but_not_claimed

## Warnings

- none

## Errors

- none

## Outputs

- `ORGANS/THRONE/RECEIPTS/organ_assembly_standard_receipt.json`
- `ORGANS/THRONE/REPORTS/ORGAN_ASSEMBLY_STANDARD_SUMMARY_V0_1.json`
- `ORGANS/THRONE/REPORTS/ORGAN_ASSEMBLY_STANDARD_SUMMARY_V0_1.csv`
