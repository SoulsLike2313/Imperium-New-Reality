# OUTPUT REQUIREMENTS

TASK_ID: TASK-20260605-PC-TRUTH-HEAD-CORRIDOR-SAVE-OFFICIO-RU-V0_1

## Required repo artifacts

The Servitor must produce or update the minimal artifacts needed for this task. Expected examples:

- `ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_ROUTE_MANIFEST_TEMPLATE.json`
- `ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_START_ACK_TEMPLATE.json`
- `ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASKPACK_FORM_CONTRACT_V0_1.md`
- Administratum current truth card or adjacent correction receipt if stale
- `REPORTS/TASK-20260605-PC-TRUTH-HEAD-CORRIDOR-SAVE-OFFICIO-RU-V0_1/FINAL_OWNER_SUMMARY_RU.md`
- `REPORTS/TASK-20260605-PC-TRUTH-HEAD-CORRIDOR-SAVE-OFFICIO-RU-V0_1/officio_servitor_role_entry_receipt.json`
- `REPORTS/TASK-20260605-PC-TRUTH-HEAD-CORRIDOR-SAVE-OFFICIO-RU-V0_1/validation_receipt.json`
- `REPORTS/TASK-20260605-PC-TRUTH-HEAD-CORRIDOR-SAVE-OFFICIO-RU-V0_1/git_commit_push_remote_closure_receipt.json`

## Required final report contents

The final owner-facing report must be Russian after Officio role entry and must include:

- task id;
- root and branch;
- files changed;
- validation commands and results;
- Officio role-entry and Russian-output confirmation;
- commit hash;
- push proof;
- remote closure proof;
- blockers or UNKNOWN_WITH_REASON items.

## Required evidence

At minimum, record evidence for:

- JSON parse success for changed JSON files;
- no BOM for task corridor JSON files;
- all eight organs present in route template;
- actual HEAD measured with git;
- remote HEAD measured after push;
- `git status --porcelain` after completion.

## Forbidden output

- No owner-facing final response in English after Officio role entry.
- No fake clean pass.
- No semantic claims not backed by receipts.
- No final completion claim before commit/push/remote closure, unless a blocker receipt explains why save was impossible.
