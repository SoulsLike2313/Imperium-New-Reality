# OUTPUT REQUIREMENTS

Task ID: `TASK-20260605-PC-IMPERIUM-CORE-SHAPE-ORGAN-LIFE-METRICS-QUARANTINE-V0_1`

## Required final report directory

```text
REPORTS/TASK-20260605-PC-IMPERIUM-CORE-SHAPE-ORGAN-LIFE-METRICS-QUARANTINE-V0_1/
```

## Required report files

```text
FINAL_OWNER_SUMMARY_RU.md
CORE_SELF_VALIDATION_REPORT.json
CORE_FILE_CLASSIFIER_DRY_RUN_REPORT.json
ORGAN_LIFE_VALIDATION_REPORT.json
ADMINISTRATUM_ADDRESS_BOOK_SEED_RECEIPT.json
STRATEGIUM_METRICS_REGISTRY_RECEIPT.json
SCHOLA_AGGRESSIVE_LEARNING_RECEIPT.json
INQUISITION_QUARANTINE_POLICY_RECEIPT.json
CUSTODES_ORGAN_LIFE_AUDIT_RECEIPT.json
MECHANICUS_TOOL_REGISTRATION_RECEIPT.json
POST_WORK_BUNDLE_INDEX_CARD.json
POST_WORK_BUNDLE_MANIFEST.json
POST_WORK_RECEIPT_INDEX.json
POST_WORK_ORGAN_RING_RECEIPT.json
INQUISITION_CONTRADICTION_SCAN_RECEIPT.json
REMOTE_CLOSURE_RECEIPT.json
GIT_CLOSURE_RECEIPT.json
```

## Required owner summary content

The Russian owner summary must clearly explain:

- what core shape was introduced;
- why the repository is not physically migrated yet;
- what 9 organ homes mean;
- what support zone means;
- what quarantine means and why active use is banned;
- what metrics were introduced;
- what checkers were created;
- what alerts were found;
- what remains V0.2/V0.3 work;
- exact commit hash and remote proof if pushed.

## Required machine evidence

All JSON receipts must be valid JSON, ENGLISH UTF8 NO_BOM, and must include:

- task_id;
- timestamp_utc when applicable;
- verdict;
- checked evidence or UNKNOWN_WITH_REASON;
- warnings;
- blockers;
- next action.

## Bundle policy

The report bundle must represent the historical delta of the task, not only the Git commit.

The GitHub-safe index must be committed. Heavy artifacts may be local-only if indexed with sha256 and path policy.

## Cost policy

Strategium must record planned cost class, actual cost class, file count, command/checker count if known, and KPD verdict.

If token usage, RAM usage, CPU usage, or VRAM usage are not measured, the value must be UNKNOWN_WITH_REASON.

## Learning policy

Schola must capture at least one concrete aggressive organ learning rule that can become a preventive alert or checker later.

## Quarantine policy

No active workflow may depend on files inside `SUPPORT/QUESTIONABLE_OR_QUARANTINE/` unless a salvage/admission receipt is created.

## Closure command expectation

The Servitor must provide commands used for validation and closure in the final report, so the Owner or future agent can replay the checks.
