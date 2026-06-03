# TASK-NEWGEN-MECHANICUS-ARSENAL-MASS-INTAKE-BATCH-001-PC-V0_1

## Mission

Begin the large, correct Mechanicus Arsenal integration on PC.

This is not a tool installation task. It is a mass intake foundation task.

Mechanicus must learn many capabilities, tools, practices, algorithms, examples, and playbooks through cards, categories, validation plans, status discipline, Owner questions, and next validation queue.

## Core law

No Arsenal card = the capability does not exist for IMPERIUM.  
No validation receipt = no CANON.  
No usage contract = Servitor cannot use it as a trusted capability.  
No source/license/trust note = cannot go beyond CANDIDATE/SANDBOX.  
No secret/cost/privacy policy = cloud/LLM adapters cannot become CANON.

## Required result

- all Arsenal categories contain capability folders;
- at least 80 capability cards exist;
- most cards may be CANDIDATE;
- CANON only with evidence/receipt;
- LOCAL_LLM/CLOUD_LLM_ADAPTERS remain reserved/candidate-only;
- next validation queue exists;
- Servitor scope export seed exists;
- Owner Questions exist for major tool choices.

## Preferred capability folder

`IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/<CATEGORY>/<CAPABILITY_ID>/`

Preferred files:
- `capability_card.json`
- `README.md`
- `validation_plan.md`
- `usage_contract.md`
- `risks.md`
- `validation_receipts/`
- `examples/` if appropriate

## Input seed

Use:

`INTAKE_BATCHES/candidate_batches_v0_1.json`

You may adjust IDs/names to match existing local schema, but preserve intent and report changes.

## Required reports

Create:

`IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-ARSENAL-MASS-INTAKE-BATCH-001-PC-V0_1/`

Required:
1. `FINAL_REPORT.md`
2. `mass_intake_manifest.json`
3. `category_coverage_report.json`
4. `fake_canon_detection_report.json`
5. `next_validation_queue.json`
6. `servitor_capability_scope_seed_report.json`
7. `owner_questions_report.json`
8. `llm_reserved_policy_report.json`
9. `arsenal_mass_intake_check_report.json`
10. `closure_receipt.json`

## Checker

Add/update a lightweight checker if reasonable:

`IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_mechanicus_arsenal_mass_intake_v0_1.py`

It should verify categories, card JSON, required fields, valid statuses, no fake CANON, no LLM/cloud CANON, category coverage, no obvious runtime junk.

## Commit/push

Commit message:

`TASK-20260524: add Mechanicus Arsenal mass intake batch 001`

Next recommended task after PASS:

`TASK-NEWGEN-MECHANICUS-ARSENAL-VALIDATION-BATCH-001-PC-V0_1`
