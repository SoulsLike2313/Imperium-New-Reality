# Evidence Ledger and Continuity Contract

Status: `CANDIDATE_V0_1`

Every important task must leave source/evidence boundary, claim ledger, input/output artifact list, receipts, replay commands where available, next allowed task, and continuity note for next Logos/Servitor.

Mandatory closure residue:

- `commit_push_receipt.json` is required for substantial tasks;
- default expectation is commit+push executed even on WARN/BLOCK outcomes;
- if commit/push is skipped, receipt must explicitly declare `BLOCK_OWNER_INPUT_REQUIRED_TO_CONTINUE` with exact Owner action required.
