# GHOST_EVOLVE Stage2.2 Learning Backlog

## LEARN-20260531-001
- dirty_path: `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/REPORTS/TASK-NEWGEN-EIGHT-ORGAN-MOBILIZATION-AND-ASTRONOMICON-TASK-ENTRY-FORM-PC-V0_1/synthetic_task_entry_checker_receipt.json`
- affected_organ: `ASTRONOMICON`
- problem_type: `TOOLING_GAP`
- prevention: deterministic or auto-restore guard for timestamp-only synthetic drift.

## LEARN-20260531-002
- dirty_path: `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/_TASKPACK_INBOX/`
- affected_organ: `ASTRONOMICON`
- problem_type: `TASK_ENTRY_GAP`
- prevention: auto-clean staging extraction or move it outside repo.