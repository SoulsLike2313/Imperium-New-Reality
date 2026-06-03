# Next Pipeline Handoff Update Report

NEXT_PIPELINE_HANDOFF now carries taxonomy and combined adjudication links as first-class routing fields.

## Updated contract files

- IMPERIUM_NEW_GENERATION/MATRIX_SPINE/SCHEMAS/next_pipeline_handoff_schema.json
- IMPERIUM_NEW_GENERATION/MATRIX_SPINE/TEMPLATES/NEXT_PIPELINE_HANDOFF_TEMPLATE.json
- IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/CONTRACTS/NEXT_PIPELINE_HANDOFF_AND_CLOSURE_PROVENANCE_CONTRACT_V0_1.md

## New fields in handoff payload

- head_taxonomy_manifest_path
- combined_review_adjudication_receipt_path
- review_target_head
- accepted_continuity_head
- artifact_bundle_head
