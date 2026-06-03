# Acceptance Gates

## PASS_WITH_WARNINGS requires all

- Starting repo truth recorded.
- Ghost_Evolve V2 Entry ACK produced.
- All new canonical/internal files created by this task are English-only and UTF-8 without BOM.
- Independent replay of language filter/gate/fixtures is performed after current final HEAD.
- Independent replay receipt includes exact HEAD, branch, worktree clean state, and command evidence.
- Strict-scope language scan receipt exists.
- Legacy language backlog exists and classifies global hits without mass rewrite.
- Stale repo-truth classification exists.
- Head taxonomy and finalization taxonomy are documented or updated.
- Taskpack retention policy exists.
- Taskpack retention inventory exists.
- No clean language PASS is claimed while legacy backlog remains.
- Hard red-team verdict exists and can downgrade.
- Efficiency delta receipt exists.
- Commit and push are performed for admitted changes.
- Worktree is clean after push.
- Remote origin/master equals final HEAD.

## BLOCK

- New internal taskpack or canonical files contain Cyrillic outside explicit Officio-authorized runtime-output exception.
- New text files contain UTF-8 BOM.
- Independent replay is missing.
- Strict-scope scan receipt is missing.
- Legacy hits are ignored.
- Legacy hits are mass-rewritten without explicit scope and receipts.
- Stale repo-truth is ignored.
- Registered taskpack retention policy is missing.
- Final report contains PENDING commit or push fields while claiming pass.
- No positive efficiency delta.
- Commit or push fails.
- Worktree remains dirty after finalization.

## Required caps

- `CAP_INDEPENDENT_LANGUAGE_REPLAY_MISSING`
- `CAP_STRICT_SCOPE_LANGUAGE_RECEIPT_MISSING`
- `CAP_LEGACY_LANGUAGE_BACKLOG_MISSING`
- `CAP_STALE_REPO_TRUTH_NOT_CLASSIFIED`
- `CAP_TASKPACK_RETENTION_POLICY_MISSING`
- `CAP_LANGUAGE_CLEAN_PASS_OVERCLAIM`
- `CAP_HEAD_TAXONOMY_UNCLEAR`
- `CAP_REGISTERED_TASKPACK_FOOTPRINT_UNCLASSIFIED`
- `CAP_PENDING_COMMIT_PUSH_FIELDS_LEFT_OPEN`
- `CAP_NO_EFFICIENCY_DELTA`
