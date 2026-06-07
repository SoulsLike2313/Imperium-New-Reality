# DIRTY CLASSIFIER BLUEPRINT

## Goal

Git dirty state must be actionable.

## Categories

- CANONICAL_REPORT_ARTIFACT;
- FRESH_TASK_OUTPUT_CANDIDATE;
- OLD_UNRELATED_ARTIFACT;
- RUNTIME_ARTIFACT;
- GENERATED_TASKPACK_RUNTIME;
- LOCAL_CONFIG;
- SECRET_RISK;
- STAGE_CANDIDATE;
- IGNORE_CANDIDATE;
- QUARANTINE_CANDIDATE;
- DELETE_REQUIRES_OWNER_APPROVAL;
- UNKNOWN_REVIEW_REQUIRED.

## Required behavior

The classifier must explain what each dirty path is, whether it blocks push, and what action is recommended.

It must not delete files.

It must not stage files without validation and receipt.
