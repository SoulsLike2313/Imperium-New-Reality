# OUTPUT_REQUIREMENTS.md

## Required report directory

REPORTS/TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_3/

## Required owner-facing file

- FINAL_OWNER_SUMMARY_RU.md

The final owner-facing file must be Russian.

## Required core outputs

At minimum produce or update equivalent files:

- POST_WORK_BUNDLE_V0_3_CONTRACT.md
- POST_WORK_STANDARD_CLOSURE_ROUTE_V0_3.md
- administratum_standard_task_closure_v0_3.py or equivalent runnable command
- post_work_bundle_manifest.schema.json
- post_work_bundle_index_card.schema.json
- post_work_organ_receipt.schema.json
- post_work_repair_request.schema.json
- ORGAN_RECEIPT_TEMPLATE.json
- REPAIR_REQUEST_TEMPLATE.json
- REQUIRED_9_ORGANS_V0_3.json
- POST_WORK_BUNDLE_INDEX_CARD.json
- POST_WORK_BUNDLE_MANIFEST.json
- POST_WORK_RECEIPT_INDEX.json
- POST_WORK_FILE_DELTA_INDEX.json
- POST_WORK_ORGAN_RING_RECEIPT.json
- ADMINISTRATUM_POST_WORK_BUNDLE_CHECKER_REPORT.json
- ADMINISTRATUM_POST_WORK_BUNDLE_RECEIPT.json
- INQUISITION_CONTRADICTION_SCAN_RECEIPT.json
- CUSTODES_ORGAN_MATRIX_AUDIT_RECEIPT.json
- SCHOLA_ENHANCED_GHOST_EVOLVE_RECEIPT.json
- REPAIR_LOOP_RECEIPT.json
- REMOTE_CLOSURE_RECEIPT.json
- POST_PUSH_NO_WRITE_PROOF.json
- GIT_CLOSURE_RECEIPT.json
- NEXT_TASK_ROUTE.json

## Required fixtures

Produce positive and negative fixtures sufficient to prove V0.3:

- fixture_valid_bundle_pass
- fixture_missing_organ_receipt_block
- fixture_malformed_receipt_block
- fixture_inquisition_block_repair_required
- fixture_missing_remote_proof_block
- fixture_heavy_artifact_policy_case

## Required commands in final report

Final report must include exact commands that can be copied:

- run schema/checker suite
- run standard closure command
- inspect bundle index
- verify git status
- verify local HEAD equals origin/master

## GitHub index policy

GitHub may contain:

- contracts
- schemas
- templates
- validators/checkers
- small fixtures
- small receipts
- indexes
- summaries
- hash manifests

GitHub must not contain unadmitted heavy/private/local payload.

## Required final response

Servitor final response to Owner must include:

1. Step name.
2. Full path to primary report or bundle index.
3. Verdict.
4. Commit hash.
5. Remote proof line.
6. Clean worktree line.
7. Short Russian comments.
8. Warnings and limitations.
9. Next task route.

## Forbidden final claims

Do not claim:

- full semantic truth
- full production readiness
- full Custodes/Throne authority
- WARP readiness
- all future tasks fully automated unless proven by runnable closure route and fixtures
