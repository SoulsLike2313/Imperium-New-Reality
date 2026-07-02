# ORGAN AGENT ADVISORY SCORING VALIDATION REPORT V0.1

task_id: `ORGAN-AGENT-ADVISORY-SCORING-FOUNDATION-0001`  
validator_id: `organ_agent_advisory_scoring_validator.v0_1`  
verdict: `PASS_ORGAN_AGENT_ADVISORY_SCORING_READY`  
generated_at_utc: `2026-07-02T11:14:33Z`  
repo_head: `663c402afe07620745df8ad55953c27c6031de0b`

## Meaning

Organs can now speak as advisory agents.

They may point to profile-specific attention zones using mathematical scoring.

They must not command concrete actions, execute, claim trust, or claim Throne verdict.

## Checks

- `PASS` — ORGAN_AGENT_ADVISORY_SCORING_MATRIX_V0_1.json_exists
- `PASS` — ORGAN_AGENT_ADVISORY_SCORING_FOUNDATION_V0_1.md_exists
- `PASS` — organ_agent_advisory.py_exists
- `PASS` — imperium_cli.py_exists
- `PASS` — LAUNCHER_COMMANDS_V0_3.json_exists
- `PASS` — advisory_matrix_parses
- `PASS` — success_score_weights_sum_to_one
- `PASS` — all_organs_have_advisory_profiles
- `PASS` — organ_agent_advisory_tool_runs
- `PASS` — organ_agent_advisory_summary_parses
- `PASS` — advisory_count_matches_organs
- `PASS` — advisory_scores_are_numeric_0_100
- `PASS` — advisory_text_has_no_direct_action_commands
- `PASS` — advisory_items_have_profile_domains
- `PASS` — launcher_advise_runs
- `PASS` — launcher_advise_organ_astronomicon_runs
- `PASS` — launcher_advisory_commands_declared

## Warnings

- none

## Errors

- none
