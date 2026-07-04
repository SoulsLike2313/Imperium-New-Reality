# IMPERIUM APP UI REFERENCE TARGET CONTRACT AND FIDELITY GATE REPORT V0.1

task_id: `IMPERIUM-APP-UI-REFERENCE-TARGET-CONTRACT-AND-FIDELITY-GATE-0001`  
validator_id: `mechanicus_ui_reference_target_contract_and_fidelity_gate_validator.v0_1`  
verdict: `PASS_IMPERIUM_APP_UI_REFERENCE_TARGET_CONTRACT_AND_FIDELITY_GATE_READY`  
generated_at_utc: `2026-07-04T13:53:07Z`

## Meaning

This patch does not change the UI. It locks the target and the evaluation law for future UI work.

The UI is not complete until Owner accepts the reference form. Build, FPS, HTTP 200, and npm/cargo proof are lower gates only.

## New law

```text
Build proof is not target proof.
FPS proof is not reference fidelity proof.
UX proof is not backend execution proof.
External outsource candidates are evidence, not canonical implementation.
```

## Checks

- `PASS` — reference_target_contract_exists_and_declares_no_fake_visual_green
- `PASS` — contract_forbids_final_ui_claims_without_owner_acceptance
- `PASS` — fidelity_gate_matrix_exists_weights_sum_to_100_and_covers_target_dimensions
- `PASS` — fidelity_matrix_blocks_build_fps_to_reference_pollution
- `PASS` — custodes_ui_reference_prosecutor_matrix_exists
- `PASS` — throne_ui_reference_crown_gate_matrix_exists

## Warnings

- none

## Errors

- none
