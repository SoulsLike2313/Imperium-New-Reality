# ASTRONOMICON RED + BLUE HARDENING AND SCAN ISOLATION REPORT V0.1

task_id: `ASTRONOMICON-RED-BLUE-HARDENING-AND-SCAN-ISOLATION-0001`  
validator_id: `astronomicon_red_blue_hardening_scan_isolation_validator.v0_1`  
verdict: `PASS_ASTRONOMICON_RED_BLUE_HARDENED_AND_SCAN_ISOLATED`  
generated_at_utc: `2026-07-02T10:51:07Z`  
repo_head: `589cfb80c608587a460479af7173d944fdf22229`

## Meaning

Astronomicon Red/Blue is locally hardened by profile-specific red cases and blue guards.

The Red/Blue scan output isolation bug is also closed: single-organ scan writes isolated output and does not overwrite global 10-organ scan summary.

## Scores

- red_local_hardening_score: `100.0`
- blue_local_hardening_score: `100.0`
- red_team_proven_score: `0.0`
- blue_team_proven_score: `0.0`
- custodes_validation_score: `0.0`
- throne_confirmation_score: `0.0`

## Next

`CUSTODES-ASTRONOMICON-VALIDATION-0001`

## Checks

- `PASS` — red_blue_team_skills_scan.py_exists
- `PASS` — astronomicon_red_blue_hardening.py_exists
- `PASS` — ASTRONOMICON_RED_BLUE_HARDENING_MATRIX_V0_1.json_exists
- `PASS` — ASTRONOMICON_RED_BLUE_HARDENING_CASES_V0_1.json_exists
- `PASS` — astronomicon_red_blue_matrix_parses
- `PASS` — astronomicon_red_blue_cases_parse
- `PASS` — global_redblue_scan_runs
- `PASS` — global_redblue_summary_has_10_organs
- `PASS` — single_organ_redblue_scan_runs
- `PASS` — single_organ_scan_does_not_overwrite_global_summary
- `PASS` — single_organ_scan_writes_isolated_astronomicon_summary
- `PASS` — astronomicon_red_blue_hardening_tool_runs
- `PASS` — astronomicon_red_blue_hardening_summary_parses
- `PASS` — astronomicon_red_blue_local_scores_pass_threshold
- `PASS` — proof_scores_remain_zero
- `PASS` — global_redblue_scan_restored_after_test

## Warnings

- none

## Errors

- none
