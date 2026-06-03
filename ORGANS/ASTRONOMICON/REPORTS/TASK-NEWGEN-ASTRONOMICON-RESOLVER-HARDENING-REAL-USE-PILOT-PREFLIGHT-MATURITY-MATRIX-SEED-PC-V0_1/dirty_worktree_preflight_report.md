# Dirty Worktree Preflight Report

Task ID: TASK-NEWGEN-ASTRONOMICON-RESOLVER-HARDENING-REAL-USE-PILOT-PREFLIGHT-MATURITY-MATRIX-SEED-PC-V0_1
Timestamp UTC: $(System.Collections.Specialized.OrderedDictionary.timestamp_utc)

## Summary

- Worktree clean at start: $(if(IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/REPORTS/TASK-NEWGEN-EIGHT-ORGAN-MOBILIZATION-AND-ASTRONOMICON-TASK-ENTRY-FORM-PC-V0_1/synthetic_task_entry_checker_receipt.json IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/REPORTS/TASK-NEWGEN-EIGHT-ORGAN-MOBILIZATION-AND-ASTRONOMICON-TASK-ENTRY-FORM-PC-V0_1/synthetic_task_entry_proof_report.md ARTIFACTS/TASKPACK_INTAKE/.Count -eq 0){'yes'}else{'no'})
- Dirty path count: $(IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/REPORTS/TASK-NEWGEN-EIGHT-ORGAN-MOBILIZATION-AND-ASTRONOMICON-TASK-ENTRY-FORM-PC-V0_1/synthetic_task_entry_checker_receipt.json IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/REPORTS/TASK-NEWGEN-EIGHT-ORGAN-MOBILIZATION-AND-ASTRONOMICON-TASK-ENTRY-FORM-PC-V0_1/synthetic_task_entry_proof_report.md ARTIFACTS/TASKPACK_INTAKE/.Count)
- Inherited pre-existing dirty paths detected: $(IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/REPORTS/TASK-NEWGEN-EIGHT-ORGAN-MOBILIZATION-AND-ASTRONOMICON-TASK-ENTRY-FORM-PC-V0_1/synthetic_task_entry_checker_receipt.json IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/REPORTS/TASK-NEWGEN-EIGHT-ORGAN-MOBILIZATION-AND-ASTRONOMICON-TASK-ENTRY-FORM-PC-V0_1/synthetic_task_entry_proof_report.md.Count)
- Additional non-inherited dirty paths detected: $(ARTIFACTS/TASKPACK_INTAKE/.Count)

## Classification

### Pre-existing inherited dirty paths
- $_ : preserved as inherited Stage1 report dirt; do not overwrite/revert in this task.
- $_ : preserved as inherited Stage1 report dirt; do not overwrite/revert in this task.


### Additional dirty paths at task start
- $_ : classify during task as task-created vs external drift.


## Safety decision

- Proceed mode: WARN_CONTINUE
- Reason: taskpack explicitly allows continuation under inherited dirty warning when provenance is declared and no destructive overwrite/revert is performed.
- Cap carried: CAP_DIRTY_WORKTREE_UNCLASSIFIED remains OPEN until final reconciliation.
