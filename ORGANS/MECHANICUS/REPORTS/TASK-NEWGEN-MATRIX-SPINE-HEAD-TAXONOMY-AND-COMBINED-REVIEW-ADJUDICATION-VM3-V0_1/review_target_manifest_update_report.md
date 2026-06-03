# Review Target Manifest Update Report

The review target manifest is extended to include explicit taxonomy binding and reviewer consistency fields.

## Updated contract surfaces

- IMPERIUM_NEW_GENERATION/MATRIX_SPINE/SCHEMAS/review_target_manifest_schema.json
- IMPERIUM_NEW_GENERATION/MATRIX_SPINE/TEMPLATES/REVIEW_TARGET_MANIFEST_TEMPLATE.json
- IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/REPORTS/TASK-NEWGEN-MATRIX-SPINE-HEAD-TAXONOMY-AND-COMBINED-REVIEW-ADJUDICATION-VM3-V0_1/REVIEW_TARGET_MANIFEST.json

## Added enforcement semantics

- head_taxonomy_manifest_path is required.
- reviewer_head_taxonomy_paths.inquisitor and reviewer_head_taxonomy_paths.speculum must converge.
- review_target_head must be a single full hash.
- independent replay commands are machine-readable in the manifest.
