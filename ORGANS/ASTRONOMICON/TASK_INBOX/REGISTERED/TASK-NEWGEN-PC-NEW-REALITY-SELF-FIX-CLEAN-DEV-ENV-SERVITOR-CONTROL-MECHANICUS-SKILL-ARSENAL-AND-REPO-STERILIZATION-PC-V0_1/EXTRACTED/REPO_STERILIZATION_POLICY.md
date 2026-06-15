# Repository Sterilization Policy

New Reality must become a sterile, controlled development root.

Do not delete files in this task. Use quarantine.

File classes:

- `ACTIVE_CORE`: required for organs, task intake, Skills, validators, schemas, root contracts.
- `ACTIVE_REPORTS`: useful reports, receipts, bundles, closure proofs.
- `CANDIDATE_REVIEW`: useful but not canon; draft, experiment, tool candidate, possible salvage.
- `QUARANTINE`: stale, duplicate, generated, runtime leftovers, temporary exports, non-active clutter.
- `DO_NOT_TOUCH`: critical or unclear files that must not move without separate task.

Quarantine root:

`QUARANTINE/REPO_STERILIZATION/<TASK_ID>/`

For each moved file, record:

- source path
- target path
- classification
- reason
- SHA256
- restore allowed
- restore command or note

After quarantine, run smoke validators to prove active functionality still works.
