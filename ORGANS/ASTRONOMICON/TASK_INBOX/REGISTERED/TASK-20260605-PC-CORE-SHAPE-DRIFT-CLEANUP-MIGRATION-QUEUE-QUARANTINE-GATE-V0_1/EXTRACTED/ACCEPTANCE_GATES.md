# Acceptance Gates for TASK-20260605-PC-CORE-SHAPE-DRIFT-CLEANUP-MIGRATION-QUEUE-QUARANTINE-GATE-V0_1

## Admission and role gates

- Astronomicon registered this taskpack successfully.
- Servitor enters role through OFFICIO_AGENTIS before mutation.
- Owner-facing final summary is Russian through OFFICIO.
- Machine artifacts remain ENGLISH UTF8 NO_BOM.

## Git and contour gates

- Work is executed on PC root only: `E:/IMPERIUM_NEW_GENERATION_NEW_REALITY`.
- Ancient Empire and parent folders are not used as active sources.
- Starting git status is captured.
- Pre-existing dirt is classified before any repair.
- Final git status is clean, except explicitly local ignored files.
- Commit and normal non-force push are performed.
- Final proof shows local HEAD equals origin/master after push, or a clear BLOCK is reported.

## Core shape hardening gates

Must exist or be updated:

- `ORGANS/_CORE_GOVERNANCE/`
- `SUPPORT/COMMON_IMPERIUM_SUPPORT/`
- `SUPPORT/QUESTIONABLE_OR_QUARANTINE/`
- `ORGANS/ADMINISTRATUM/MIGRATION_QUEUE/`

Must produce:

- core self-validation report;
- dry-run classifier report;
- migration queue;
- quarantine active-use checker report;
- organ-life validation report;
- Custodes organ-life metadata repair or explicit already-valid receipt.

## Required receipts

The final report bundle must include:

```text
PRE_EXISTING_DIRT_CLASSIFICATION_RECEIPT.json
ASTRONOMICON_REGISTRY_CLOSURE_RECEIPT.json
POST_WORK_V0_3_RESIDUE_CLOSURE_RECEIPT.json
CORE_SELF_VALIDATION_REPORT.json
CORE_FILE_CLASSIFIER_DRY_RUN_REPORT.json
CORE_MIGRATION_QUEUE_REPORT.json
QUARANTINE_ACTIVE_USE_CHECK_REPORT.json
ORGAN_LIFE_VALIDATION_REPORT.json
CUSTODES_ORGAN_LIFE_AUDIT_RECEIPT.json
INQUISITION_QUARANTINE_POLICY_RECEIPT.json
STRATEGIUM_CORE_METRICS_RECEIPT.json
SCHOLA_AGGRESSIVE_LEARNING_RECEIPT.json
ADMINISTRATUM_ADDRESS_BOOK_UPDATE_RECEIPT.json
POST_WORK_BUNDLE_INDEX_CARD.json
POST_WORK_ORGAN_RING_RECEIPT.json
FINAL_OWNER_SUMMARY_RU.md
```

## Checker gates

At minimum, run:

```text
python ORGANS/_CORE_GOVERNANCE/TOOLS/core_shape_self_checker_v0_1.py --root .
```

If V0.2/V0.3 tools are created, run them too. The final summary must list every checker command and verdict.

The post-work bundle checker must pass or return an explicit repair request.

## Quarantine gates

- Quarantine active-use ban is documented.
- Quarantine active-use checker exists or a clear blocker is reported.
- Any active reference to `SUPPORT/QUESTIONABLE_OR_QUARANTINE/` must be BLOCK unless an explicit salvage/admission receipt exists.
- No task output may instruct future agents to use quarantine as canonical source.

## Migration safety gates

- No mass delete.
- No mass physical move unless safe and explicitly justified.
- Migration queue is generated before any move.
- Unknown owner files are not silently accepted.
- Unknown owner files are classified as UNKNOWN_OWNER or QUARANTINE_CANDIDATE.

## Metrics gates

Strategium must output:

- planned budget;
- actual cost class;
- files changed count;
- report files count;
- checker count;
- operator/Prime/Servitor intervention classification if knowable;
- value delta;
- next task budget recommendation;
- KPD verdict.

Unknown real token/RAM/VRAM values must be `UNKNOWN_WITH_REASON`, not fabricated.

## Learning gates

Schola must convert repeated failures into at least three durable preventive learning artifacts. Lessons must point to target organs and target artifact types.

## Verdict rules

- Clean PASS is allowed only if all required checkers pass and no unresolved dirty state remains.
- PASS_WITH_WARNINGS is acceptable if warnings are explicit, scoped, and represented in next-task route.
- BLOCK must be returned if registry dirt, active quarantine use, broken bundle closure, or push failure remains unresolved.
