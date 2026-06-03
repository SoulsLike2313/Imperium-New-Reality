# Task Spec - Language Gate Independent Replay, Legacy Backlog, and Retention Policy

Task ID: `TASK-NEWGEN-LANGUAGE-GATE-INDEPENDENT-REPLAY-STRICT-SCOPE-LEGACY-BACKLOG-RETENTION-POLICY-PC-V0_1`

## Background

The previous language authority and mojibake filter task completed at final HEAD `b5bd8a0ca8a91a458f13b9aa5e183151dec91452`.

It created:
- Officio language authority;
- Inquisition mojibake filter;
- Astronomicon language gate;
- fixtures with successful results;
- a final clean and synced repository state.

However, independent review kept the result at PASS_WITH_WARNINGS because:
- global language scan still has legacy warnings;
- some red-team artifacts contain stale repo-truth snapshots;
- commit taxonomy is split across artifact, receipt, and final closure commits;
- registered taskpack ZIP and EXTRACTED artifacts need a retention/quarantine policy;
- clean language PASS must not be claimed while legacy backlog remains.

## Goal

Stabilize the language authority layer without doing a broad cleanup.

This task must:
1. replay the language gate after the final HEAD;
2. produce strict-scope independent replay receipts;
3. classify legacy language and encoding hits;
4. create a durable backlog for future remediation;
5. create a retention policy for registered taskpacks and extracted payloads;
6. make stale repo-truth snapshots explicit;
7. preserve EN-only and UTF-8 no-BOM discipline.

## Required implementation A - Independent replay

Run the existing Inquisition mojibake filter, Astronomicon taskpack language gate, and language fixture runner after current HEAD is synced.

Produce:
- independent replay command log;
- independent replay JSON receipt;
- independent replay markdown summary;
- exact HEAD and branch fields;
- worktree clean field before and after replay.

The replay must not depend on stale artifact reports from the previous task.

## Required implementation B - Strict-scope scan receipt

Create a strict-scope scan mode or receipt.

The strict scope should focus on:
- new language authority artifacts;
- Inquisition filter and fixtures;
- Astronomicon language gate;
- Officio language authority policy;
- Matrix Spine language and encoding matrices;
- current taskpack registered artifacts;
- current report bundle.

The strict-scope receipt must say:
- scanned roots;
- exclusions;
- hit count by severity;
- whether strict scope has BLOCK hits;
- whether legacy hits are outside strict scope.

## Required implementation C - Legacy language backlog

Create a backlog from global scan hits. Do not fix all legacy files in this task.

Required categories:
- `ALLOWED_RUNTIME_OWNER_OUTPUT`
- `ALLOWED_LOCALIZATION_RESOURCE`
- `LEGACY_TO_REMEDIATE`
- `NEW_BLOCKING_VIOLATION`
- `FALSE_POSITIVE`
- `SAFE_BINARY_OR_PDF_IGNORED`
- `NEEDS_OWNER_OR_ORGAN_DECISION`

Required files:
- `legacy_language_backlog.json`
- `legacy_language_backlog.md`
- `legacy_language_backlog_summary.csv` if useful

Each backlog item should include:
- path;
- hit type;
- severity;
- category;
- owner organ if known;
- recommended remediation path;
- whether it blocks optimization phase;
- whether it blocks next micro-pilot.

## Required implementation D - Stale repo-truth classification

Scan recent report bundles for fields or files indicating stale truth, especially:
- hard red-team repo truth captured before final closure;
- old HEAD in red-team artifact;
- dirty state that was later fixed by closure commit;
- `PENDING_COMMIT`, `PENDING_PUSH_URL`, `PENDING_FINAL_GIT_CHECK`.

Do not rewrite old history.

Create:
- `stale_repo_truth_classification_report.md`
- `stale_repo_truth_classification_receipt.json`

Classify stale truth as:
- `PRE_FINALIZATION_SNAPSHOT_ALLOWED`
- `STALE_REQUIRES_FOLLOWUP`
- `CURRENT_TRUTH`
- `BLOCKING_CONFLICT`

## Required implementation E - Head taxonomy and finalization taxonomy

Create or update a small contract explaining:
- subject implementation head;
- artifact bundle commit;
- receipt commit;
- closure/finalization commit;
- current remote HEAD;
- when red-team repo truth is allowed to be pre-finalization;
- when it is blocking.

Suggested artifact:
`IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/CONTRACTS/HEAD_TAXONOMY_AND_FINALIZATION_RECEIPT_V0_1.md`

and/or JSON equivalent.

## Required implementation F - Registered taskpack retention policy

Create an Astronomicon or Administratum policy for:

`IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/**`

Policy must cover:
- ZIP file retention;
- EXTRACTED folder retention;
- receipts and route manifest retention;
- when to keep full taskpack payload;
- when to hash and quarantine payload outside canonical repo;
- when to keep only manifest, route, receipt, and hash pointer;
- binary and large-file policy;
- review artifact retention policy;
- cleanup commands must not delete evidence without receipt.

Suggested artifacts:
- `TASKPACK_RETENTION_POLICY_V0_1.md`
- `TASKPACK_RETENTION_POLICY_V0_1.json`
- `taskpack_retention_inventory_report.md`
- `taskpack_retention_inventory.json`

## Required implementation G - Astronomicon admission update

If safe and small, update Astronomicon language gate or admission receipts so they can record:
- strict-scope pass;
- global legacy warnings;
- retention class of registered taskpack payload.

Do not overbuild.

## Required implementation H - Reports and receipts

Recommended report root:

`IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/REPORTS/TASK-NEWGEN-LANGUAGE-GATE-INDEPENDENT-REPLAY-STRICT-SCOPE-LEGACY-BACKLOG-RETENTION-POLICY-PC-V0_1/`

Required:
- `ghost_evolve_entry_ack.json`
- `repo_truth_probe.json`
- `independent_language_replay_report.md`
- `independent_language_replay_receipt.json`
- `strict_scope_language_scan_report.md`
- `strict_scope_language_scan_receipt.json`
- `legacy_language_backlog.md`
- `legacy_language_backlog.json`
- `stale_repo_truth_classification_report.md`
- `stale_repo_truth_classification_receipt.json`
- `head_taxonomy_update_report.md`
- `taskpack_retention_policy_report.md`
- `taskpack_retention_inventory_report.md`
- `taskpack_retention_inventory.json`
- `GHOST_EVOLVE_LANGUAGE_GATE_REPLAY_LEARNING_BACKLOG.json`
- `GHOST_EVOLVE_LANGUAGE_GATE_REPLAY_LEARNING_BACKLOG.md`
- `NEXT_PIPELINE_HANDOFF.json`
- `efficiency_delta_receipt.json`
- `hard_red_team_verdict.json`
- `claim_ledger.jsonl`
- `capability_split_receipt.json`
- `final_owner_summary_ru.md`
- `commit_push_receipt.json`

Note:
`final_owner_summary_ru.md` is allowed only as Officio-authorized runtime owner-facing output. It must not become a machine policy source.

## Required closure behavior

PC Servitor must commit and push admitted canonical changes.

A final report must not end with:
- `PENDING_COMMIT`;
- `PENDING_PUSH_URL`;
- `PENDING_FINAL_GIT_CHECK`.

If changes are not admitted, Servitor must rollback or quarantine them with receipt, or stop with `BLOCKED_PENDING_OWNER_DECISION`.

## Allowed verdicts

- `LANGUAGE_GATE_REPLAY_PASS_WITH_WARNINGS`
- `LANGUAGE_GATE_REPLAY_PARTIAL`
- `LANGUAGE_GATE_REPLAY_BLOCKED`

Clean PASS is forbidden unless strict-scope scan has no BLOCK hits, legacy backlog is created, stale repo-truth is classified, and independent review later accepts the result.

## Forbidden

No visual IDE.
No WARP activation.
No second micro-pilot.
No freelance or trading execution.
No mass legacy rewrite.
No private or secret scanning outside canonical safe scope.
No deleting registered taskpack payloads without retention receipt.
No history rewrite.
