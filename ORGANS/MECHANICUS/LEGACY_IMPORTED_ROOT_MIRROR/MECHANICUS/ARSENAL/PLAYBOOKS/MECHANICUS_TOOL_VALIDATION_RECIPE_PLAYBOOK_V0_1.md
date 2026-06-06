# MECHANICUS TOOL VALIDATION RECIPE PLAYBOOK V0.1

## Purpose
Define reusable install/detect/validate/stress/receipt recipe format for future tool validation waves.

## Recipe Artifact
- `IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/RECIPES/tool_validation_recipes_v0_1.json`
- Schema: `IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/SCHEMAS/tool_validation_recipe_schema_v0_1.json`

## Required Recipe Stages
1. `detect`: prove availability or context existence.
2. `install`: candidate command + policy note (`not executed` unless Owner-gated task).
3. `validate`: functional bounded check and expected receipt.
4. `stress`: repeated bounded runs and stability criteria.
5. `receipt`: required evidence file naming and storage corridor.
6. `rollback_or_cleanup_notes`: recovery expectations for future install waves.

## Build Procedure
1. Ensure matrix JSON exists:
   - `IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/<TASK_ID>/owner_approval_matrix_v0_1.json`
2. Build recipes:
   - `python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_tool_validation_recipe_builder_v0_1.py`
3. Parse-check JSON:
   - `python -m json.tool IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/RECIPES/tool_validation_recipes_v0_1.json`
4. Run matrix checker to verify recipe coverage.

## Operational Notes
- Recipe creation itself does not authorize installation.
- Each future install wave must create fresh receipts and update owner decision state.
- If capability is in reserved LOCAL_LLM or CLOUD_LLM lanes, keep recipe as deferred planning only.
