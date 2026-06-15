# MECHANICUS TOOL APPROVAL MATRIX PLAYBOOK V0.1

## Purpose
Provide a repeatable workflow for building and checking Owner approval matrix artifacts without installing tools.

## Inputs
- `IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/arsenal_registry_v0_1.json`
- `IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/FIELD_GUIDES/BATCH_001/ARSENAL_AGENT_USAGE_MAP_BATCH_001.json`
- `IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/TOOL_EXPANSION/BATCH_001/tool_detection_results.json`

## Output Bundle
- `OWNER_APPROVAL_MATRIX.md`
- `OWNER_APPROVAL_MATRIX.csv`
- `owner_approval_matrix_v0_1.json`
- `recommended_install_waves_v0_1.json`
- `defer_queue_v0_1.json`
- `reject_or_quarantine_queue_v0_1.json`
- `owner_decision_template_v0_1.csv`
- `owner_decision_template_v0_1.json`
- `matrix_build_receipt.json`

## Run Procedure
1. Confirm git truth and clean scope gates.
2. Run builder:
   - `python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_owner_approval_matrix_builder_v0_1.py`
3. Validate JSON files with `python -m json.tool`.
4. Build validation recipes:
   - `python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_tool_validation_recipe_builder_v0_1.py`
5. Run matrix checker:
   - `python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_mechanicus_owner_approval_matrix_v0_1.py`
6. Collect checker receipt and final report.

## Owner Decision Round
1. Owner updates `owner_decision_template_v0_1.csv` or `owner_decision_template_v0_1.json`.
2. Servitor imports decisions into next matrix revision (keep history in report folder).
3. Install waves are allowed only after explicit Owner gate.

## Rules
- No tool installation in matrix-only tasks.
- No CANON promotion in matrix-only tasks.
- VM3/Ubuntu profiles are untouched unless explicitly admitted.
