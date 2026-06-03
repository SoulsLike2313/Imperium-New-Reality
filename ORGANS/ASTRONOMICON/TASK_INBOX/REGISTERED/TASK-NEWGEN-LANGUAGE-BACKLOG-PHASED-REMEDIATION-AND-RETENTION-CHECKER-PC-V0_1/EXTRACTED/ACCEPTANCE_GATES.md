# Acceptance Gates

## PASS_WITH_WARNINGS requires all

- Starting repo truth recorded.
- Ghost_Evolve V2 Entry ACK produced.
- All new canonical/internal files created by this task are English-only and UTF-8 without BOM.
- A small backlog slice is selected with explicit risk classification.
- Selected backlog items are remediated, reclassified, or explicitly left unchanged with evidence.
- Before and after hashes are recorded for edited files.
- Backlog delta receipt exists.
- Retention checker tool exists.
- Retention checker inspects Astronomicon registered taskpack entries.
- Retention inventory delta exists.
- Post-remediation independent replay exists.
- Strict scope remains free of blocking hits.
- Global language status remains WARN or improves; no clean global PASS is claimed.
- Matrix/cap update report exists.
- Hard red-team verdict exists and can downgrade.
- Efficiency delta receipt exists.
- Commit and push are performed for admitted changes.
- Worktree is clean after push.
- Remote origin/master equals final HEAD.

## BLOCK

- New internal taskpack or canonical files contain Cyrillic outside explicit Officio-authorized runtime-output exception.
- New text files contain UTF-8 BOM.
- No backlog slice is selected.
- Broad mass rewrite is attempted.
- Existing evidence is deleted without receipt.
- Retention checker is missing.
- Registered taskpack payloads are deleted or moved without retention receipt.
- Independent replay is missing.
- Strict scope gains blocking hits.
- Clean global language PASS is claimed while legacy backlog remains.
- Final report contains PENDING commit or push fields while claiming pass.
- No positive efficiency delta.
- Commit or push fails.
- Worktree remains dirty after finalization.

## Required caps

- `CAP_PHASED_LANGUAGE_REMEDIATION_MISSING`
- `CAP_RETENTION_CHECKER_MISSING`
- `CAP_BACKLOG_DELTA_MISSING`
- `CAP_RETENTION_INVENTORY_DELTA_MISSING`
- `CAP_UNSAFE_MASS_LANGUAGE_REWRITE`
- `CAP_GLOBAL_LANGUAGE_CLEAN_PASS_OVERCLAIM`
- `CAP_EVIDENCE_DELETED_WITHOUT_RECEIPT`
- `CAP_STRICT_SCOPE_REGRESSION`
- `CAP_PENDING_COMMIT_PUSH_FIELDS_LEFT_OPEN`
- `CAP_NO_EFFICIENCY_DELTA`
