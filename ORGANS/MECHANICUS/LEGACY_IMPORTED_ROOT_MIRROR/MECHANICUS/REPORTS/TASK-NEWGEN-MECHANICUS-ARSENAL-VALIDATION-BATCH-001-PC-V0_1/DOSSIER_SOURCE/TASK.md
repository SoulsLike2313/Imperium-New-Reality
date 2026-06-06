# TASK-NEWGEN-MECHANICUS-ARSENAL-VALIDATION-BATCH-001-PC-V0_1

## Mission

Run Mechanicus Arsenal Validation Batch 001 through **Ghost_Evolve organ-body execution**.

This task must validate foundational capabilities and teach Mechanicus how to validate tools in the future.

The task is successful only if:

1. selected P0/P1/P2-lite capabilities are validated or honestly marked missing;
2. receipts are created;
3. card statuses are updated only with evidence;
4. reusable Mechanicus tools/checkers/playbooks are created or improved;
5. Mechanicus can repeat part of the workflow without Servitor re-explaining it;
6. Inquisition receives cleanliness/fake-green report;
7. Administratum-ready evidence map exists.

## Organ route map

### Primary body: Mechanicus

Servitor must enter Mechanicus body.

Mechanicus owns:

- capability cards;
- tool validation;
- validation receipts;
- usage contracts;
- capability scope exports;
- tool/checker registration;
- fake-CANON detection;
- Owner questions about tool choices.

### Oversight: Inquisition

Inquisition receives:

- fake-CANON findings;
- uncontrolled install/network attempts;
- runtime junk/dirt findings;
- quarantine recommendations.

### Evidence memory: Administratum

Administratum receives:

- report path map;
- receipt map;
- changed card map;
- commit-ready evidence summary.

## Validation scope

Use:

`VALIDATION_SCOPE_OWNER_APPROVED_V0_1.json`

Priority:

1. P0 Mechanicus spine
2. P1 code quality foundation
3. P2 evidence/search lite
4. P3 visual readiness detection only
5. P5 LLM/cloud reserved, not validated

## Required reusable Mechanicus outputs

Create or improve:

1. `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_capability_validator_v0_1.py`
2. `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_validation_receipt_builder_v0_1.py`
3. `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_capability_scope_exporter_v0_1.py`
4. `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_fake_canon_detector_v0_2.py` or improve existing detector and document location.
5. `IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/PLAYBOOKS/MECHANICUS_TOOL_VALIDATION_PLAYBOOK_V0_1.md`
6. `IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/LESSONS/MECHANICUS_MEMORY_LESSON_001.md`

If a listed script already exists under another name, do not duplicate blindly. Improve or wrap it and report.

## Validation receipts

For each validated capability, create a receipt under the relevant capability folder or central receipts path.

Each receipt must include:

- capability_id;
- command/check performed;
- exit_code or PASS/FAIL;
- stdout/stderr excerpt;
- side effects;
- network_used;
- files created/modified;
- validation verdict;
- promotion recommendation.

## Status update rules

- `CANDIDATE → SANDBOX`: allowed if local validation passes and usage remains bounded.
- `SANDBOX → CANON`: allowed only with strong evidence/receipt and safe bounded use.
- `CANON` must never appear without evidence.
- missing tool remains `CANDIDATE` and receives Owner question or validation queue item.
- LLM/cloud remains reserved/candidate-only.

## Required reports

Create:

`IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-ARSENAL-VALIDATION-BATCH-001-PC-V0_1/`

Required files:

1. `FINAL_REPORT.md`
2. `validation_batch_manifest.json`
3. `validation_results.json`
4. `capability_status_change_report.json`
5. `validation_receipts_index.json`
6. `mechanicus_reusable_capabilities_report.json`
7. `capability_scope_export_report.json`
8. `fake_canon_detector_report.json`
9. `inquisition_cleanliness_report.json`
10. `administratum_evidence_map.json`
11. `ghost_evolve_training_proof.json`
12. `owner_questions_report.json`
13. `closure_receipt.json`

## Proof that Mechanicus learned

Create `ghost_evolve_training_proof.json` with:

- before_manual_work list;
- after_mechanicus_capabilities list;
- reusable scripts created/improved;
- how to run them again;
- what future Servitor no longer has to do manually;
- receipts proving scripts run;
- limitations.

## Commit/push

Commit message:

`TASK-20260524: validate Mechanicus Arsenal batch 001`

## Next recommended task

If PASS/PASS_WITH_WARNINGS:

`TASK-NEWGEN-MECHANICUS-CAPABILITY-SCOPE-EXPORT-PC-V0_1`

or if validation exposes missing basics:

`TASK-NEWGEN-MECHANICUS-ARSENAL-VALIDATION-FOLLOWUP-PC-V0_1`
