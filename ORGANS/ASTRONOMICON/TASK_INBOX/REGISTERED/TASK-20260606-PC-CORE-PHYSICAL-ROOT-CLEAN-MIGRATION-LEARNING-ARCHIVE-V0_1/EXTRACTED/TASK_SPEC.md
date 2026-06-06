# TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1

## Mission
Perform a large but gated physical repository shape cleanup on the PC contour.

The repository must move toward the owner's strict active-core form:

```text
ROOT/
  ORGANS/
    ADMINISTRATUM/
    ASTRONOMICON/
    CUSTODES/
    DOCTRINARIUM/
    INQUISITION/
    MECHANICUS/
    OFFICIO_AGENTIS/
    SCHOLA_IMPERIALIS/
    STRATEGIUM/
  SUPPORT/
    COMMON_IMPERIUM_SUPPORT/
    QUESTIONABLE_OR_QUARANTINE/
```

Throne is excluded from the 9-organ core and remains future/laptop-only scope.

## Prime directive
Do not merely describe cleanup. Perform a real, safe, git-tracked physical migration where validation permits it.

The active root must be reduced as aggressively as safely possible. Anything that is not one of the 9 organ homes and is not legitimate common support must be moved out of active root into SUPPORT, quarantine, or learning archive.

## Required safety model
1. Use git status before work.
2. Preserve all content. No destructive deletion.
3. Use git mv for tracked moves where possible.
4. If an item cannot be moved safely, create HOLD_WITH_REASON in the migration queue.
5. Do not claim full cleanup unless the active root check proves it.
6. Do not use quarantine as active runtime source.
7. Keep task registration/inbox/report evidence valid.
8. Run validators after migration.
9. Commit and normal non-force push accepted changes.
10. Final owner output must be Russian after OFFICIO role entry.

## Migration policy
Top-level active root directories must be classified and moved under one of these destinations:

### A. Organ homes
Only these 9 directories are canonical organ homes under ORGANS/:
- ADMINISTRATUM
- ASTRONOMICON
- CUSTODES
- DOCTRINARIUM
- INQUISITION
- MECHANICUS
- OFFICIO_AGENTIS
- SCHOLA_IMPERIALIS
- STRATEGIUM

Top-level duplicate organ mirrors such as ADMINISTRATUM, ASTRONOMICON, DOCTRINARIUM, INQUISITION, MECHANICUS, OFFICIO_AGENTIS must be treated as legacy root mirrors. Move or merge them into proper ORGANS/<ORGAN>/LEGACY_IMPORTED_ROOT_MIRROR/ only if safe and address-booked. If not safe, move to SUPPORT/QUESTIONABLE_OR_QUARANTINE/ITEMS/LEGACY_ROOT_MIRRORS/ with HOLD_WITH_REASON.

### B. Common support
Shared infrastructure that legitimately serves multiple organs goes under SUPPORT/COMMON_IMPERIUM_SUPPORT/ with classification receipt. Examples may include shared schema registry, contour bridge, language core, taskpack runtime, git runtime, shared validators, root documents, and support policies.

### C. Learning archive / failed experiments
Legacy front-end, visual, Sanctum, old visual brain, training/demo/prototype surfaces, failed or abandoned backends, and experimental UI/backend material should leave active root. Do not delete it. Move it into an explicit learning archive under:

```text
SUPPORT/QUESTIONABLE_OR_QUARANTINE/ITEMS/LEARNING_ARCHIVE/
```

This includes obvious candidates such as SANCTUM_*, VISUAL_BRAIN, old visual foundry/prototype layers, abandoned training/demo surfaces, and similar old pain, unless a validator proves they are current active support.

### D. Quarantine
Unknown, duplicate, stale, temporary, unowned, or questionable material goes under:

```text
SUPPORT/QUESTIONABLE_OR_QUARANTINE/ITEMS/
```

Every moved quarantine item must get an index entry with original_path, new_path, reason, suspected_owner, active_use_banned=true, and salvage_required=true.

## Required artifacts
Create or update:

```text
ORGANS/_CORE_GOVERNANCE/TOOLS/core_root_shape_enforcer_v0_1.py
ORGANS/_CORE_GOVERNANCE/TOOLS/core_migration_executor_v0_1.py
ORGANS/_CORE_GOVERNANCE/TOOLS/core_active_root_allowlist_checker_v0_1.py
ORGANS/_CORE_GOVERNANCE/MATRICES/core_root_migration_matrix_v0_1.json
ORGANS/_CORE_GOVERNANCE/MATRICES/legacy_learning_archive_matrix_v0_1.json
ORGANS/_CORE_GOVERNANCE/METRICS/core_physical_cleanliness_metric_v0_1.json
ORGANS/_CORE_GOVERNANCE/METRICS/active_root_impurity_metric_v0_1.json
ORGANS/ADMINISTRATUM/ADDRESS_BOOK/physical_root_migration_address_book_v0_1.json
ORGANS/INQUISITION/QUARANTINE_POLICY/quarantine_salvage_request.schema.json
ORGANS/INQUISITION/QUARANTINE_POLICY/active_root_impurity_alert_matrix_v0_1.json
ORGANS/SCHOLA_IMPERIALIS/LEARNING/legacy_pain_learning_archive_contract_v0_1.md
ORGANS/STRATEGIUM/METRICS/physical_migration_cost_metric_v0_1.json
ORGANS/MECHANICUS/TOOLS/CORE_PHYSICAL_MIGRATION_TOOLCHAIN_CARD.json
SUPPORT/COMMON_IMPERIUM_SUPPORT/README.md
SUPPORT/QUESTIONABLE_OR_QUARANTINE/QUARANTINE_INDEX.json
SUPPORT/QUESTIONABLE_OR_QUARANTINE/ITEMS/LEARNING_ARCHIVE/README.md
```

Reports must include:

```text
REPORTS/TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1/FINAL_OWNER_SUMMARY_RU.md
REPORTS/TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1/CORE_ACTIVE_ROOT_ALLOWLIST_CHECK_REPORT.json
REPORTS/TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1/CORE_PHYSICAL_MIGRATION_REPORT.json
REPORTS/TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1/CORE_MIGRATION_EXECUTION_RECEIPT.json
REPORTS/TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1/QUARANTINE_INDEX_UPDATE_RECEIPT.json
REPORTS/TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1/LEARNING_ARCHIVE_UPDATE_RECEIPT.json
REPORTS/TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1/ADMINISTRATUM_ADDRESS_BOOK_UPDATE_RECEIPT.json
REPORTS/TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1/INQUISITION_ACTIVE_USE_SCAN_RECEIPT.json
REPORTS/TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1/MECHANICUS_TOOL_DELTA_RECEIPT.json
REPORTS/TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1/STRATEGIUM_PHYSICAL_CLEANUP_COST_RECEIPT.json
REPORTS/TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1/SCHOLA_AGGRESSIVE_ORGAN_LEARNING_RECEIPT.json
REPORTS/TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1/CUSTODES_CORE_SHAPE_AUDIT_RECEIPT.json
REPORTS/TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1/POST_WORK_BUNDLE_INDEX_CARD.json
```

## Validation commands
Servitor must run available existing checkers plus new checkers. At minimum:

```text
python ORGANS/_CORE_GOVERNANCE/TOOLS/core_active_root_allowlist_checker_v0_1.py --root . --out REPORTS/TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1/CORE_ACTIVE_ROOT_ALLOWLIST_CHECK_REPORT.json
python ORGANS/_CORE_GOVERNANCE/TOOLS/core_shape_master_check_v0_1.py --root . --out REPORTS/TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1/CORE_SHAPE_MASTER_CHECK_REPORT.json
python ORGANS/_CORE_GOVERNANCE/TOOLS/quarantine_active_use_checker_v0_1.py --root . --out REPORTS/TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1/QUARANTINE_ACTIVE_USE_CHECK_REPORT.json
python ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/administratum_post_work_bundle_checker_v0_1.py --task-id TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1 --root . --out REPORTS/TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1/ADMINISTRATUM_POST_WORK_BUNDLE_CHECKER_REPORT.json
```

If a command path differs, discover the existing checker path and record the actual command in receipts.

## Enhanced Ghost Evolve requirements
This is not a normal file move task. Servitor must teach the organs aggressively:

- Administratum learns physical address ownership.
- Inquisition learns active root impurity and quarantine use violations.
- Mechanicus learns migration toolchain passports.
- Strategium learns physical cleanup cost and impurity metrics.
- Schola captures legacy pain as learning material.
- Custodes audits whether organs actually guarded the new shape.
- Astronomicon records task route integrity.
- Officio enforces role and Russian owner output.
- Doctrinarium confirms law/scope: Throne excluded, no claim of full semantic truth.

## Scope boundaries
Allowed: physical movement of legacy/root clutter into SUPPORT or quarantine/learning archive when safe.
Allowed: creation of compatibility notes and address-book entries.
Allowed: update imports/paths only where required by moved active support.
Forbidden: destructive delete.
Forbidden: moving .git.
Forbidden: claiming full clean if allowlist checker warns.
Forbidden: using quarantine content as active runtime source.
Forbidden: expanding to UI redesign or feature development.
Forbidden: full semantic truth claim.
