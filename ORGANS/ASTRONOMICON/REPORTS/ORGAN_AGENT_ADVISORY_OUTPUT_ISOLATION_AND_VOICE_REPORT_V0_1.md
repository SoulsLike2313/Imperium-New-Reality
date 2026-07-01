# ORGAN AGENT ADVISORY OUTPUT ISOLATION AND VOICE REPORT V0.1

task_id: `ORGAN-AGENT-ADVISORY-OUTPUT-ISOLATION-AND-VOICE-ENRICHMENT-0001`  
validator_id: `organ_agent_advisory_output_isolation_voice_validator.v0_1`  
verdict: `PASS_ADVISORY_OUTPUT_ISOLATION_AND_VOICE_ENRICHED`  
generated_at_utc: `2026-07-01T20:32:36Z`  
repo_head: `ef85a546f015cf968e58d2a4a75ea1df0145eb70`

## Meaning

The single-organ advisory output bug is fixed.

`imperium advise organ INQUISITION` writes isolated per-organ files and does not overwrite global advisory summary/report.

The organ voice is now richer: visible state, why the zone matters, probability raisers/reducers, evidence considered, and not-claimed boundaries.

## Next

Red + Blue team tools and skills foundation.

## Checks

- `PASS` — ORGAN_AGENT_ADVISORY_OUTPUT_ISOLATION_AND_VOICE_MATRIX_V0_1.json_exists
- `PASS` — ORGAN_AGENT_ADVISORY_OUTPUT_ISOLATION_AND_VOICE_ENRICHMENT_V0_1.md_exists
- `PASS` — organ_agent_advisory.py_exists
- `PASS` — output_isolation_matrix_parses
- `PASS` — global_advisory_generation_runs
- `PASS` — global_summary_parses
- `PASS` — global_summary_has_all_10_organs
- `PASS` — single_organ_advisory_generation_runs
- `PASS` — single_organ_json_written
- `PASS` — single_organ_markdown_written
- `PASS` — single_organ_did_not_overwrite_global_summary
- `PASS` — single_organ_did_not_overwrite_global_report
- `PASS` — single_organ_json_parses
- `PASS` — single_organ_has_one_advisory
- `PASS` — voice_enrichment_fields_present
- `PASS` — voice_has_no_direct_action_commands
- `PASS` — global_advisory_regenerated_after_test

## Warnings

- none

## Errors

- none
