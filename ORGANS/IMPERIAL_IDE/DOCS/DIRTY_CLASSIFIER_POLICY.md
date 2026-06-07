# Dirty Classifier Policy

Status: CANDIDATE_V0_1

## Categories

The classifier uses these task categories: CANONICAL_REPORT_ARTIFACT, FRESH_TASK_OUTPUT_CANDIDATE, OLD_UNRELATED_ARTIFACT, RUNTIME_ARTIFACT, GENERATED_TASKPACK_RUNTIME, LOCAL_CONFIG, SECRET_RISK, STAGE_CANDIDATE, IGNORE_CANDIDATE, QUARANTINE_CANDIDATE, DELETE_REQUIRES_OWNER_APPROVAL, UNKNOWN_REVIEW_REQUIRED.

## Rules

- Never delete files.
- Never stage SECRET_RISK, LOCAL_CONFIG, runtime artifacts, or unknown paths.
- Stage current task outputs only after validation.
- Known unrelated ZIPs stay unstaged unless their source task or owner-approved cleanup handles them.

## Push state

Push can proceed only after validated in-scope staging and no staged blockers. Dirty unrelated artifacts must remain visible in receipts; no clean-tree claim is made while they remain.
