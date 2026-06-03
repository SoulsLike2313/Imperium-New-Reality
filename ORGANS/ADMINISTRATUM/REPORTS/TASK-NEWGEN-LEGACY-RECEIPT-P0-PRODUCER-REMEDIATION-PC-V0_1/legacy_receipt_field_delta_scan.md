# Legacy Receipt Field Delta Scan

Task: `TASK-NEWGEN-LEGACY-RECEIPT-P0-PRODUCER-REMEDIATION-PC-V0_1`

## Scope
- Delta mode only over 4 required P0 producers.
- No full 479-candidate inventory regeneration committed.

## Delta Summary
- p0_count_before: 4
- p0_count_after: 0
- before_summary: `{'MANUAL_REVIEW': 9, 'LIKELY_SELF_HEAD_RISK': 4}`
- after_summary: `{'SAFE_NEW_SEMANTICS': 6}`

## Per-path
| Path | Before | After | P0 resolved |
|---|---|---|---|
| `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_capability_scope_exporter_v0_2.py` | LEGACY_AMBIGUOUS_HEADS (P0) | MIGRATED_TO_EXTERNAL_FINALIZATION (P3) | yes |
| `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_quality_gate_runner_v0_1.py` | LEGACY_AMBIGUOUS_HEADS (P0) | MIGRATED_TO_EXTERNAL_FINALIZATION (P3) | yes |
| `IMPERIUM_NEW_GENERATION/SANCTUM_NG/IMPORTANT_SIX_TUI_DASHBOARD/ACTIONS/important_six_dashboard_actions_v0_1.py` | LEGACY_AMBIGUOUS_HEADS (P0) | MIGRATED_TO_EXTERNAL_FINALIZATION (P3) | yes |
| `IMPERIUM_NEW_GENERATION/TOOLS/TOOL_ADMISSION/newgen_tool_admission_builder_v0_1.py` | LEGACY_SELF_HEAD_RISK (P0) | MIGRATED_TO_EXTERNAL_FINALIZATION (P3) | yes |
