# Dirty Worktree Classification Matrix

Task: TASK-NEWGEN-STAGE1-DIRTY-FILES-CLASSIFICATION-AND-CLEANUP-PC-V0_1

| Path | Classification | Action | Owner Organ | Reason |
|---|---|---|---|---|
| `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/REPORTS/TASK-NEWGEN-EIGHT-ORGAN-MOBILIZATION-AND-ASTRONOMICON-TASK-ENTRY-FORM-PC-V0_1/synthetic_task_entry_checker_receipt.json` | LEGACY_CONFLICT_RESTORE_TO_HEAD | RESTORE_TO_HEAD_WITH_RECEIPT | ASTRONOMICON | Timestamp-only drift is non-admitted noise for this task scope; restore closes fake-green dirty provenance. |
| `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/REPORTS/TASK-NEWGEN-EIGHT-ORGAN-MOBILIZATION-AND-ASTRONOMICON-TASK-ENTRY-FORM-PC-V0_1/synthetic_task_entry_proof_report.md` | LEGACY_CONFLICT_RESTORE_TO_HEAD | RESTORE_TO_HEAD_WITH_RECEIPT | ASTRONOMICON | Non-semantic drift should not be committed as new evidence; restore is safest admitted action. |
| `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/_TASKPACK_INBOX/` | RUNTIME_EPHEMERAL_TO_DELETE | DELETE_WITH_RECEIPT | ASTRONOMICON | Keep repository canon clean; staging inbox is non-canonical and should not remain as runtime drift. |