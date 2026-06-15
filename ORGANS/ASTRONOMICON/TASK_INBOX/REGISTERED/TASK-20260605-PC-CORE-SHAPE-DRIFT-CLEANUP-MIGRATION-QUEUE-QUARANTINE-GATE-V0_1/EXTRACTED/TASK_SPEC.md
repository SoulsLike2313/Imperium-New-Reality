# TASK-20260605-PC-CORE-SHAPE-DRIFT-CLEANUP-MIGRATION-QUEUE-QUARANTINE-GATE-V0_1

## Mission

Execute a larger but still controlled architecture-cleanup strike on PC.

This task continues the previous Core Shape / Organ Life / Metrics / Quarantine V0.1 step. The previous step created the first governance layer, but it left warnings:

- legacy top-level areas are not migrated;
- unknown and unclassified files remain;
- Custodes has a metadata gap;
- pre-existing Astronomicon registry dirt remains outside the commit;
- POST-WORK-BUNDLE-ADMISSION-RING-V0_3 residue was left outside the commit;
- resource metrics were not measured;
- post-push self-reference closure still needs stronger no-write proof discipline.

The mission is to close these warnings as far as possible without dangerous mass relocation. The output must be a stronger machine-checkable repo-shape control layer.

## Primary Objective

Create V0.1 hardening for repo-core strictness:

1. Close or explicitly classify pre-existing registry changes.
2. Resolve or classify POST-WORK-BUNDLE-ADMISSION-RING-V0_3 residue.
3. Add missing Custodes organ-life metadata needed by core validation.
4. Harden the core self-checker so it distinguishes:
   - accepted legacy;
   - known active organ home;
   - common support;
   - unknown owner;
   - quarantine candidate;
   - active-use quarantine violation;
   - registry drift;
   - task inbox residue;
   - post-work residue.
5. Generate the first migration queue for the strict two-zone architecture:
   - ORGANS with exactly 9 organ homes;
   - SUPPORT with COMMON_IMPERIUM_SUPPORT and QUESTIONABLE_OR_QUARANTINE.
6. Create or update quarantine gate policy and checker so files in quarantine cannot be used by active task flow unless a salvage/admission receipt exists.
7. Strengthen Strategium metrics and Schola aggressive learning around repo-shape drift, dirty worktree, cost overrun, and repeated manual operator interventions.
8. Produce a complete post-work bundle and push the result.

## Required Architecture Direction

The long-term core model is:

```text
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

Throne is explicitly excluded from this 9-organ core and remains future laptop-only scope.

## Required Work Zones

Prefer these locations:

```text
ORGANS/_CORE_GOVERNANCE/
ORGANS/_CORE_GOVERNANCE/TOOLS/
ORGANS/_CORE_GOVERNANCE/MATRICES/
ORGANS/_CORE_GOVERNANCE/SCHEMAS/
ORGANS/_CORE_GOVERNANCE/TEMPLATES/

ORGANS/ADMINISTRATUM/ADDRESS_BOOK/
ORGANS/ADMINISTRATUM/MIGRATION_QUEUE/

ORGANS/CUSTODES/ORGAN_LIFE_AUDIT/
ORGANS/INQUISITION/QUARANTINE_POLICY/
ORGANS/STRATEGIUM/METRICS/
ORGANS/SCHOLA_IMPERIALIS/LEARNING/
ORGANS/MECHANICUS/TOOLS/

SUPPORT/COMMON_IMPERIUM_SUPPORT/
SUPPORT/QUESTIONABLE_OR_QUARANTINE/

REPORTS/TASK-20260605-PC-CORE-SHAPE-DRIFT-CLEANUP-MIGRATION-QUEUE-QUARANTINE-GATE-V0_1/
```

## Required Deliverables

### A. Registry and residue closure

Inspect git status at start. If there are pre-existing tracked changes:

- identify whether they are task registry changes, V0_3 residue, route residue, local-only contour residue, or unrelated dirt;
- do not blindly reset;
- either incorporate them into this task with receipts, restore if proven transient, or classify them with an explicit residue receipt.

Required receipts:

```text
REPORTS/TASK-20260605-PC-CORE-SHAPE-DRIFT-CLEANUP-MIGRATION-QUEUE-QUARANTINE-GATE-V0_1/PRE_EXISTING_DIRT_CLASSIFICATION_RECEIPT.json
REPORTS/TASK-20260605-PC-CORE-SHAPE-DRIFT-CLEANUP-MIGRATION-QUEUE-QUARANTINE-GATE-V0_1/ASTRONOMICON_REGISTRY_CLOSURE_RECEIPT.json
REPORTS/TASK-20260605-PC-CORE-SHAPE-DRIFT-CLEANUP-MIGRATION-QUEUE-QUARANTINE-GATE-V0_1/POST_WORK_V0_3_RESIDUE_CLOSURE_RECEIPT.json
```

### B. Custodes metadata repair

Repair the Custodes organ-life metadata gap found by the previous core validation.

Minimum expected artifacts:

```text
ORGANS/CUSTODES/ORGAN_CARD.json
ORGANS/CUSTODES/ORGAN_CONTRACT.md
ORGANS/CUSTODES/READ_FIRST.md
```

If already present, validate and update only what is needed.

### C. Core checker hardening

Update or add:

```text
ORGANS/_CORE_GOVERNANCE/TOOLS/core_shape_self_checker_v0_2.py
ORGANS/_CORE_GOVERNANCE/TOOLS/core_file_classifier_dry_run_v0_2.py
ORGANS/_CORE_GOVERNANCE/TOOLS/core_migration_queue_builder_v0_1.py
ORGANS/_CORE_GOVERNANCE/TOOLS/quarantine_active_use_checker_v0_1.py
ORGANS/_CORE_GOVERNANCE/TOOLS/core_shape_master_check_v0_1.py
```

If a smaller implementation is safer, keep the exact tool set smaller but document why. The master checker should run the available sub-checkers and produce one JSON report.

### D. Migration queue

Create a first migration queue, not a mass move.

Required artifacts:

```text
ORGANS/ADMINISTRATUM/MIGRATION_QUEUE/CORE_MIGRATION_QUEUE_CONTRACT_V0_1.md
ORGANS/ADMINISTRATUM/MIGRATION_QUEUE/core_migration_queue_v0_1.json
ORGANS/ADMINISTRATUM/MIGRATION_QUEUE/core_migration_queue_summary.md
```

Each entry should have:

```json
{
  "path": "...",
  "classification": "ORGAN_HOME|COMMON_SUPPORT|QUARANTINE_CANDIDATE|LEGACY_ACCEPTED|UNKNOWN_OWNER|FUTURE_SCOPE",
  "owner_organ": "ADMINISTRATUM|ASTRONOMICON|CUSTODES|DOCTRINARIUM|INQUISITION|MECHANICUS|OFFICIO_AGENTIS|SCHOLA_IMPERIALIS|STRATEGIUM|NONE|UNKNOWN",
  "recommended_action": "KEEP|MOVE_TO_ORGAN|MOVE_TO_SUPPORT|MOVE_TO_QUARANTINE|INVESTIGATE|FUTURE_SCOPE_HOLD",
  "active_use_allowed": true,
  "reason": "...",
  "risk": "LOW|MEDIUM|HIGH"
}
```

### E. Quarantine gate

Quarantine must be banned from active use.

Create or strengthen:

```text
ORGANS/INQUISITION/QUARANTINE_POLICY/quarantine_active_use_violation_matrix.json
SUPPORT/QUESTIONABLE_OR_QUARANTINE/QUARANTINE_INDEX.json
```

Checker must detect at minimum text references from active repo files to:

```text
SUPPORT/QUESTIONABLE_OR_QUARANTINE/
```

and report BLOCK unless a salvage/admission exception is present.

### F. Metrics and aggressive learning

Strategium must expand metrics around:

- core_shape_compliance_score;
- organ_life_completeness_score;
- context_locality_score;
- quarantine_pressure;
- unclassified_file_count;
- script_first_ratio;
- servitor_load_reduction_score;
- operator_bootstrap_intervention_count;
- known_alert_prevention_rate.

Schola must convert at least three concrete lessons from the last tasks into durable known-alert or preventive-rule artifacts:

- PowerShell to SSH quoting failures;
- VM2 remote git HTTPS credentials failure;
- dirty worktree blocking remote route;
- post-push self-reference proof boundary;
- taskpack language gate exact ENGLISH UTF8 policy.

### G. Bundle closure

Use existing post-work bundle V0.2 enforcement. Produce a complete report bundle, run checkers, commit, push, and provide final Russian owner summary.

## Hard No

Do not perform a mass physical migration of the repo unless:
- the migration is tiny;
- every moved path has a migration queue entry;
- imports/links are checked;
- Inquisition and Custodes receipts agree;
- bundle closure passes.

Do not use anything from `SUPPORT/QUESTIONABLE_OR_QUARANTINE/` as an active source.

Do not claim the repo is fully clean. The expected result is stronger governance plus a migration queue, not final physical perfection.
