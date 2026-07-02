# THRONE ASTRONOMICON ANTI SELF-DECEPTION VALIDATION REPORT V0.1

task_id: `THRONE-ASTRONOMICON-STRICT-GATES-ANTI-SELF-DECEPTION-FIX-0001`  
validator_id: `throne_astronomicon_anti_self_deception_validator.v0_1`  
verdict: `PASS_THRONE_ASTRONOMICON_ANTI_SELF_DECEPTION_READY`  
generated_at_utc: `2026-07-02T11:26:09Z`

## Meaning

The Throne strict gate now distinguishes local Crown order from forbidden Throne self-validation.

A local Crown order can be issued for Astronomicon while `throne_self_validation_score` remains `0`.

## Checks

- `PASS` — throne_astronomicon_strict_gate.py_exists
- `PASS` — THRONE_ASTRONOMICON_STRICT_GATES_ANTI_SELF_DECEPTION_MATRIX_V0_2.json_exists
- `PASS` — anti_self_deception_matrix_parses
- `PASS` — matrix_separates_crown_order_from_self_validation
- `PASS` — throne_strict_gate_tool_runs
- `PASS` — throne_summary_parses
- `PASS` — crown_order_passes_but_self_validation_zero
- `PASS` — truth_state_is_not_self_proven
- `PASS` — astronomicon_assembled_remains_zero
- `PASS` — not_claimed_includes_throne_self_validation
- `PASS` — all_evidence_crown_gates_still_pass

## Warnings

- none

## Errors

- none

## Not claimed

- Throne self-validation
- global organ assembled
- Core v1 ready
- Great Nine complete
