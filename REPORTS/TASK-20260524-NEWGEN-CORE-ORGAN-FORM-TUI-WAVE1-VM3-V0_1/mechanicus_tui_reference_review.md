# Mechanicus TUI Reference Review (Wave1)

## Scope

Task: `TASK-20260524-NEWGEN-CORE-ORGAN-FORM-TUI-WAVE1-VM3-V0_1`

Reviewed existing Mechanicus prototype assets before creating Wave1 form/TUI layer.

## Inspected References

1. `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/MECHANICUS_AGENT/SHELL/mechanicus_textual_tui_v0_5.py`
2. `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/MECHANICUS_AGENT/TOOLS/mechanicus_agent_runner.py`
3. `IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/base_half_cli.py`
4. `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/MECHANICUS_AGENT/TOOL_REGISTRY/TOOLS/rich.json`
5. `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_CAPABILITY_REGISTRY_V0_1.generated.json`

## Reusable Pattern Extracted

- Keep organ-specific shells thin and route shared rendering/data logic through common runtime helpers.
- Preserve explicit tool-capability registry entries (especially Rich renderer evidence).
- Keep domain query commands machine-readable and receipt-friendly.
- Separate operator-visual mode from plain/machine mode to avoid fake-green visual claims.

## Preservation Decision

- Existing Mechanicus prototype files were **not** deleted or rewritten.
- Wave1 outputs were added in parallel under:
  - `IMPERIUM_NEW_GENERATION/MECHANICUS/IDENTITY/`
  - `IMPERIUM_NEW_GENERATION/MECHANICUS/CONTRACTS/`
  - `IMPERIUM_NEW_GENERATION/MECHANICUS/GATES/`
  - `IMPERIUM_NEW_GENERATION/MECHANICUS/STATE/`
  - `IMPERIUM_NEW_GENERATION/MECHANICUS/TEMPLATES/`
  - `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/`
  - `IMPERIUM_NEW_GENERATION/MECHANICUS/TUI/`
  - `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS_REGISTRY/`

## Wave1 Outcome

Wave1 uses Mechanicus as reference and raises structure order for cross-organ reuse without breaking existing prototype lineage.
