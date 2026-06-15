# TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_2

## Mission

Build Post-Work Bundle Admission Ring V0.2.

V0.1 proved the principle: a task can leave a post-work bundle index, file delta index, receipt index, 9-organ ring receipt, and Administratum structural checker output. V0.2 must convert this from a structural prototype into an enforced closure path.

The Servitor remains a precise executor. The organs must become the system that receives the report, validates evidence, requests repairs, assembles the bundle, rejects incomplete work, and records the historical delta.

## Required role entry

Before any mutation, Servitor must enter through OFFICIO_AGENTIS.

Required evidence:
- OFFICIO role entry receipt exists.
- Servitor acknowledges role, active root, task id, and owner-facing language rule.
- After OFFICIO role entry, owner-facing live and final output must be Russian.
- Machine artifacts remain ENGLISH UTF8 NO_BOM.

## Enhanced Ghost Evolve

Mode: ULTIMATE_ORGAN_TEACHING.

Servitor must not only implement files. Servitor must teach the organs. Every important rule discovered during the task must be converted into at least one durable artifact:
- contract,
- schema,
- template,
- checker,
- receipt,
- repair request grammar,
- next task route,
- Mechanicus tool card.

Learning only in final summary is not enough.

## Scope

Primary zone:
- ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/

Support zones:
- ORGANS/_POST_WORK_RING/
- ORGANS/CUSTODES/ORGAN_MATRIX_AUDIT/
- ORGANS/INQUISITION/
- ORGANS/SCHOLA_IMPERIALIS/
- ORGANS/MECHANICUS/
- ORGANS/OFFICIO_AGENTIS/
- ORGANS/ASTRONOMICON/
- REPORTS/TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_2/

## Deliverables

Create or update these artifacts:

1. Schema enforcement
- ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/SCHEMAS/post_work_bundle_manifest.schema.json
- ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/SCHEMAS/post_work_bundle_index_card.schema.json
- ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/SCHEMAS/post_work_receipt_index.schema.json
- ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/SCHEMAS/post_work_file_delta_index.schema.json
- ORGANS/_POST_WORK_RING/SCHEMAS/post_work_organ_receipt.schema.json
- ORGANS/_POST_WORK_RING/SCHEMAS/post_work_repair_request.schema.json

2. Checker V0.2
- ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/administratum_post_work_bundle_checker_v0_2.py

The checker must validate:
- bundle manifest schema,
- bundle index card schema,
- receipt index schema,
- file delta index schema,
- 9-organ ring receipt schema,
- all required 9 organ ids,
- no BLOCK verdict in required organ receipts for final acceptance,
- Inquisition receipt exists,
- Custodes narrow audit receipt exists,
- Officio language/role receipt exists,
- Schola enhanced ghost evolve receipt exists,
- Mechanicus tool delta receipt exists,
- remote proof fields exist,
- no fake final PASS when validation is incomplete.

3. Closure updater V0.2
- ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/administratum_post_work_closure_updater_v0_2.py

It must support self-reference boundary:
- pre_commit_head,
- expected_commit_message,
- post_push_head,
- origin_master_head,
- local_equals_origin,
- no_write_after_remote_proof,
- self_reference_boundary note when final commit hash cannot be embedded before commit.

4. Repair loop grammar
- ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/POST_WORK_REPAIR_LOOP_CONTRACT_V0_2.md
- ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/TEMPLATES/POST_WORK_REPAIR_REQUEST_TEMPLATE.json

Required behavior:
- If any required organ returns BLOCK, Administratum must not accept final bundle.
- Administratum must emit repair request.
- Servitor must repair only requested defects.
- Checker must be runnable on a fixture showing repair loop BLOCK then PASS.

5. Fixtures
Create fixtures proving:
- complete valid bundle PASS_WITH_WARNINGS or PASS depending on caps,
- missing organ receipt BLOCK,
- malformed receipt BLOCK,
- required organ BLOCK creates repair request,
- remote closure missing BLOCK,
- local heavy artifact referenced without index BLOCK.

6. Reports for this task
- REPORTS/TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_2/FINAL_OWNER_SUMMARY_RU.md
- REPORTS/TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_2/OFFICIO_ROLE_ENTRY_RECEIPT.json
- REPORTS/TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_2/SCHOLA_ENHANCED_GHOST_EVOLVE_RECEIPT.json
- REPORTS/TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_2/MECHANICUS_TOOL_DELTA_RECEIPT.json
- REPORTS/TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_2/INQUISITION_CONTRADICTION_SCAN_RECEIPT.json
- REPORTS/TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_2/CUSTODES_ORGAN_MATRIX_AUDIT_RECEIPT.json
- REPORTS/TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_2/ADMINISTRATUM_POST_WORK_BUNDLE_CHECKER_REPORT.json
- REPORTS/TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_2/POST_WORK_BUNDLE_INDEX_CARD.json
- REPORTS/TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_2/POST_WORK_RECEIPT_INDEX.json
- REPORTS/TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_2/POST_WORK_FILE_DELTA_INDEX.json
- REPORTS/TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_2/GIT_CLOSURE_RECEIPT.json
- REPORTS/TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_2/REMOTE_CLOSURE_RECEIPT.json
- REPORTS/TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_2/NEXT_TASK_ROUTE.json

## Required commands

At minimum run:
- JSON parse validation for all created JSON.
- The new V0.2 checker on positive and negative fixtures.
- Git status before commit.
- Commit with a clear message.
- Normal non-force push.
- Remote proof local HEAD equals origin/master after push.

## Final response

Final owner-facing response must be Russian and must include:
- step name,
- primary report path,
- verdict,
- commit hash,
- remote proof,
- what V0.2 enforces now,
- what remains V0.3.
