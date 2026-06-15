# MECHANICUS OWNER APPROVED TOOL NORMALIZATION PLAYBOOK V0.1

## Purpose
Resolve Owner-approved tool names into canonical Mechanicus capability IDs before any install-wave execution.

## Required Inputs
- `IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/arsenal_registry_v0_1.json`
- `IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/owner_approved_tool_aliases_v0_1.json`
- Previous matrix/wave artifacts from latest Owner-approval report bundle.

## Mandatory Rule
Do not start install wave planning if any Owner-approved ID is missing in canonical cards or alias mapping.

## Normalization Procedure
1. Run truth check and capture preflight git state.
2. List Owner-approved IDs for the wave.
3. For each ID:
   - find exact canonical card match in registry;
   - if missing, check related capability IDs (legacy or generic cards);
   - choose one action: `already_present`, `alias_created`, `canonical_card_created`, `matrix_row_patched`;
   - document reason in RU and include related cards.
4. Create/update canonical cards only when exact ID is absent.
5. Create/update alias map to preserve explicit link history.
6. Build normalization map and recommended wave artifact with detect/install/validate/stress fields.
7. Run checker:
   - `python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_owner_approved_tool_normalization_v0_1.py`
8. Confirm no installs were performed and write closure receipts.

## Decision Guidance
- Prefer identity mapping when Owner-approved ID already exists as canonical card.
- Prefer canonical card creation when Owner-approved ID is explicit CLI/tool contract and only generic related cards exist.
- Keep related legacy cards as references in alias metadata; do not silently rewrite history.

## Forbidden Actions
- No package manager install commands in normalization-only task.
- No CANON promotion in normalization-only task.
- No hidden aliasing: every non-trivial mapping must be explicit in alias JSON.

## Expected Outputs
- `owner_approved_tools_normalization_map_v0_1.json`
- `OWNER_APPROVED_TOOLS_NORMALIZATION_REPORT.md`
- `recommended_install_wave_001_owner_approved_v0_1.json`
- `normalization_check_report.json`

