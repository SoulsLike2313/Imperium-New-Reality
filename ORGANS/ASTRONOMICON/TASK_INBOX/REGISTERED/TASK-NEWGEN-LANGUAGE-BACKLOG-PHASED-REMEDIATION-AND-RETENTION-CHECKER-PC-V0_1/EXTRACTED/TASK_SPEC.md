# Task Spec - Language Backlog Phased Remediation and Retention Checker

Task ID: `TASK-NEWGEN-LANGUAGE-BACKLOG-PHASED-REMEDIATION-AND-RETENTION-CHECKER-PC-V0_1`

## Background

The previous language gate replay task completed at final HEAD `23727b55020775827aa0473f72e9132830004f6c`.

Accepted outcomes:
- independent language replay passed;
- strict scope passed with zero blocking hits;
- global scan remained WARN;
- legacy backlog was created;
- registered taskpack retention policy was introduced;
- worktree was clean and remote was synced.

Remaining issues:
- legacy language backlog exists;
- taskpack retention policy needs a script-first checker;
- registered ZIP and EXTRACTED payload footprint needs inventory and classification;
- clean global language PASS must not be claimed.

## Goal

Perform one safe phased remediation slice and add a retention checker.

This task must prove that legacy language debt can be reduced and registered taskpack footprint can be checked without broad rewriting or fake-green.

## Required implementation A - Backlog intake and safe slice selection

Read the current legacy language backlog produced by the previous task.

Select a small remediation slice:
- maximum recommended size: 5 to 20 items;
- prefer deterministic P0 or P1 items;
- prefer items inside current stage reports, registered taskpack metadata, or clearly safe generated artifacts;
- avoid source code rewrites unless the fix is trivial and validated;
- avoid large historical documents unless explicitly safe;
- do not edit binary files or PDFs;
- do not edit private or local files.

Create:
- `backlog_slice_selection_report.md`
- `backlog_slice_selection_receipt.json`

The receipt must state:
- selected item count;
- skipped item count;
- selection reason;
- risk level;
- expected delta;
- why selected items do not require Owner approval.

## Required implementation B - Safe remediation

For each selected item:
- capture before hash;
- capture reason;
- apply deterministic fix;
- capture after hash;
- run relevant validators;
- record whether the hit was removed, reclassified, or left unchanged.

Allowed remediation examples:
- rewrite UTF-8 BOM text files as UTF-8 no BOM;
- move misclassified runtime owner-facing output into allowed category metadata;
- add missing metadata that marks an already valid Officio-authorized runtime owner output;
- remove accidental mojibake from newly generated report artifacts only if the intended English replacement is obvious;
- update backlog category when hit is false positive or allowed localization.

Forbidden:
- translating old Russian documents in bulk;
- deleting evidence;
- rewriting old reports without receipt;
- changing semantic content blindly;
- broad mass edits.

Create:
- `language_remediation_actions.json`
- `language_remediation_actions.md`
- `language_backlog_delta_report.md`
- `language_backlog_delta_receipt.json`

## Required implementation C - Retention checker

Add a script-first checker for registered taskpack retention.

Suggested path:

`IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TOOLS/astronomicon_taskpack_retention_checker_v0_1.py`

It must inspect:

`IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/**`

The checker must classify entries:
- task id;
- total size;
- ZIP file count;
- EXTRACTED payload size;
- manifest present;
- route manifest present;
- admission receipt present;
- hash pointer present if payload is not kept;
- large or nested review artifacts present;
- retention class.

Suggested retention classes:
- `KEEP_CANONICAL_SMALL`
- `KEEP_MANIFEST_ROUTE_RECEIPTS_ONLY`
- `HASH_AND_QUARANTINE_RECOMMENDED`
- `REVIEW_ARTIFACT_PAYLOAD_REVIEW_REQUIRED`
- `MISSING_REQUIRED_RECEIPT`
- `RUNTIME_OR_TEMP_SHOULD_NOT_BE_CANONICAL`

The checker must not delete anything.

Create:
- `taskpack_retention_checker_report.md`
- `taskpack_retention_checker_receipt.json`
- `taskpack_retention_inventory_delta.json`

## Required implementation D - Retention policy application report

Apply the checker to current registered entries.

Produce a report that says:
- how many registered entries exist;
- how many are small and safe;
- how many have EXTRACTED payloads;
- how many should later be hash-and-quarantine candidates;
- whether any entry blocks VM3 route proof;
- whether any entry blocks context optimization.

Do not move or delete payloads in this task unless the task can prove a safe and receipt-backed action.

## Required implementation E - Independent replay after changes

After remediation and retention checker work:
- rerun language filter or gate;
- rerun strict scope scan;
- record global scan status;
- record backlog delta;
- record current HEAD after commit if applicable.

Create:
- `post_remediation_independent_replay_report.md`
- `post_remediation_independent_replay_receipt.json`

## Required implementation F - Matrix and cap semantics

Update or create small matrix/cap entries only as needed:
- `LANGUAGE_BACKLOG_PHASED_REMEDIATION_MATRIX`
- `TASKPACK_RETENTION_CHECKER_MATRIX`

Do not create a broad new architecture layer.

## Required implementation G - Reports and receipts

Recommended report root:

`IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/REPORTS/TASK-NEWGEN-LANGUAGE-BACKLOG-PHASED-REMEDIATION-AND-RETENTION-CHECKER-PC-V0_1/`

Required:
- `ghost_evolve_entry_ack.json`
- `repo_truth_probe.json`
- `backlog_slice_selection_report.md`
- `backlog_slice_selection_receipt.json`
- `language_remediation_actions.md`
- `language_remediation_actions.json`
- `language_backlog_delta_report.md`
- `language_backlog_delta_receipt.json`
- `taskpack_retention_checker_report.md`
- `taskpack_retention_checker_receipt.json`
- `taskpack_retention_inventory_delta.json`
- `post_remediation_independent_replay_report.md`
- `post_remediation_independent_replay_receipt.json`
- `matrix_cap_update_report.md`
- `GHOST_EVOLVE_LANGUAGE_BACKLOG_REMEDIATION_LEARNING_BACKLOG.json`
- `GHOST_EVOLVE_LANGUAGE_BACKLOG_REMEDIATION_LEARNING_BACKLOG.md`
- `NEXT_PIPELINE_HANDOFF.json`
- `efficiency_delta_receipt.json`
- `hard_red_team_verdict.json`
- `claim_ledger.jsonl`
- `capability_split_receipt.json`
- `final_owner_summary_ru.md`
- `commit_push_receipt.json`

Note:
`final_owner_summary_ru.md` is allowed only as Officio-authorized runtime owner-facing output. It must not become machine policy or task instruction.

## Required closure behavior

PC Servitor must commit and push admitted canonical changes.

A final report must not end with:
- `PENDING_COMMIT`;
- `PENDING_PUSH_URL`;
- `PENDING_FINAL_GIT_CHECK`.

If changes are not admitted, Servitor must rollback or quarantine them with receipt, or stop with `BLOCKED_PENDING_OWNER_DECISION`.

## Allowed verdicts

- `LANGUAGE_BACKLOG_REMEDIATION_PASS_WITH_WARNINGS`
- `LANGUAGE_BACKLOG_REMEDIATION_PARTIAL`
- `LANGUAGE_BACKLOG_REMEDIATION_BLOCKED`

Clean global language PASS is forbidden.

## Forbidden

No visual IDE.
No WARP activation.
No second micro-pilot.
No VM3 execution.
No freelance or trading execution.
No mass legacy rewrite.
No private or secret scanning outside canonical safe scope.
No deleting registered taskpack payloads without retention receipt.
No history rewrite.
