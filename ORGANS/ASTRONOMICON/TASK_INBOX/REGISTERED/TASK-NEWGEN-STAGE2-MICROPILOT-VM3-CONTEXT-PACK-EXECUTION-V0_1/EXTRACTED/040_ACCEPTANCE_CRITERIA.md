# ACCEPTANCE CRITERIA

## Minimum PASS_WITH_WARNINGS

All of these must be true:

- Starting HEAD was verified as `cda220333299c82931f81beee461f6cb55974462`.
- Worktree was clean before edits.
- A context pack was located, generated, or seed-wrapped with honest provenance.
- A replayable consumption harness exists.
- `context_pack_consumption_receipt.json` exists.
- `before_after_context_economy_delta.json` exists.
- `organ_block_usage_receipt.json` exists.
- `manual_read_log.jsonl` exists.
- `llm_focus_claim_ledger.jsonl` exists.
- `hard_red_team_verdict.json` exists.
- `final_owner_summary_ru.md` exists.
- IDE/WARP/API/browser/freelance/trading scopes remained locked.
- Commit and push were completed, or a hard blocker was recorded.

## Clean PASS is allowed only if

All PASS_WITH_WARNINGS criteria are met, and additionally:

- no unlogged manual broad reads occurred;
- context economy is positive and evidence-backed;
- no active cap is falsely closed;
- final worktree is clean;
- origin/master equals HEAD;
- the hard red-team verdict permits clean PASS.

## Mandatory downgrades

Downgrade to WARN if:

- context pack was seed-wrapped instead of freshly generated;
- some optional organ context was missing;
- economy baseline is approximate;
- external finalization cap remains open.

Downgrade to BLOCK if:

- starting HEAD mismatch;
- dirty start without explicit Owner-approved continuation;
- context pack cannot be found or built;
- script cannot be replayed;
- required receipts are missing;
- forbidden scopes were touched;
- final tree is dirty while claiming done.

## Forbidden claims

The final report must not claim:

- IDE runtime exists.
- WARP runtime exists.
- AdsPower/API integration is implemented.
- Browser chamber is operational.
- Freelance or trading lanes are ready.
- Block Spine is fully canonized.
