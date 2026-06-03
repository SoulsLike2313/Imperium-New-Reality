# Next Pipeline Handoff and Closure Provenance Contract V0.1

Owner organ: `Administratum`
Support organs: `Mechanicus`, `Inquisition`, `Astronomicon`
Status: `CANDIDATE_RUNTIME_READY`

## Required closure provenance fields
- `base_head`
- `implementation_head`
- `proof_head`
- `closure_bundle_head`
- `final_verifier_head`
- `remote_head_after_bundle`
- `worktree_clean_after_bundle`
- `origin_master_sync_after_bundle`
- `base_commit_url`
- `implementation_commit_url`
- `proof_commit_url`
- `closure_bundle_commit_url`
- `remote_commit_url`
- `hard_red_team_verdict_path`
- `independent_replay_status`
- `claim_ledger_path`
- `claim_statuses_seen`

## Required handoff payload
- `NEXT_PIPELINE_HANDOFF.json` with target commit(s), complete head chain, claim ledger path, independent replay status, changed paths, report paths, replay commands, caps/warnings, efficiency delta, and next task candidate.
- `head_taxonomy_manifest_path` must be present and point to one shared taxonomy source for all reviewers.
- `combined_review_adjudication_receipt_path` must be present and point to machine-readable merged review status.
- `review_target_head` must be a single canonical head and must not diverge from taxonomy.
- `accepted_continuity_head` and `artifact_bundle_head` must be first-class fields in handoff payload.

## Mandatory caps
- `CAP_EMPTY_IMPLEMENTATION_HEAD`
- `CAP_EMPTY_CLOSURE_BUNDLE_HEAD`
- `CAP_EMPTY_REMOTE_HEAD`
- `CAP_NO_INDEPENDENT_REPLAY`
- `CAP_CLAIM_LEDGER_MISSING`
- `CAP_RUNTIME_EXCLUDED_OUTPUT_WITHOUT_HASH`
- `CAP_HEADS_MIXED_OR_AMBIGUOUS`
- `CAP_NO_FINAL_CLOSURE_VERIFIER`
- `CAP_NO_NEXT_PIPELINE_HANDOFF`
- `CAP_HEAD_TAXONOMY_MANIFEST_MISSING`
- `CAP_COMBINED_REVIEW_ADJUDICATION_MISSING`
- `CAP_REVIEW_TARGET_NOT_SINGLE`
- `CAP_REVIEW_TARGET_TYPO_OR_HASH_MISMATCH`
- `CAP_DECLARED_TARGET_UNFETCHABLE`
- `CAP_REVIEWERS_USED_DIFFERENT_HEAD_TAXONOMY`
- `CAP_ARTIFACT_BUNDLE_HEAD_MISSING`
- `CAP_WARP_CLAIMED_WITHOUT_UNLOCK`

## Enforcement artifacts
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/TEMPLATES/FINAL_CLOSURE_VERIFIER_RECEIPT_TEMPLATE.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/TEMPLATES/NEXT_PIPELINE_HANDOFF_TEMPLATE.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/TEMPLATES/HEAD_TAXONOMY_MANIFEST_TEMPLATE.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/TEMPLATES/REVIEW_TARGET_MANIFEST_TEMPLATE.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/TEMPLATES/COMBINED_REVIEW_ADJUDICATION_RECEIPT_TEMPLATE.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/TEMPLATES/HEAD_CONSISTENCY_RECEIPT_TEMPLATE.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/TEMPLATES/INDEPENDENT_REPLAY_RECEIPT_TEMPLATE.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/TEMPLATES/RUNTIME_EXCLUDED_OUTPUT_MANIFEST_TEMPLATE.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/SCHEMAS/final_closure_verifier_receipt_schema.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/SCHEMAS/next_pipeline_handoff_schema.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/SCHEMAS/head_taxonomy_manifest_schema.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/SCHEMAS/review_target_manifest_schema.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/SCHEMAS/combined_review_adjudication_receipt_schema.json`
