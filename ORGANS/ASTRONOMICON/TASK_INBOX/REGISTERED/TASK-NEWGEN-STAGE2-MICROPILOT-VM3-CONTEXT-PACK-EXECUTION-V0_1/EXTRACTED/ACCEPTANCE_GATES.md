# ACCEPTANCE_GATES

The task may not claim clean PASS unless all mandatory gates below are satisfied.

## Gate A: Astronomicon authority

- The taskpack is admitted by Astronomicon intake.
- The task ID is resolvable by Astronomicon resolver.
- Admission and resolver receipts are preserved in the task evidence.

## Gate B: Context pack consumption proof

- `context_pack_consumption_receipt.json` exists.
- It identifies the context pack path used.
- It lists files actually read.
- It explains why broad repository reading was not required.
- It records any broad reads as exceptions with reasons.

## Gate C: Context economy proof

- `before_after_context_economy_delta.json` exists.
- It compares baseline broad-read or prior bloat estimate against context-pack usage.
- It includes numeric estimates or explicit bounded approximations.
- It does not claim exact token savings without evidence.

## Gate D: Organ block usage proof

- `organ_block_usage_receipt.json` exists.
- It records which organ blocks were used and why.
- It distinguishes mandatory, optional, and unused organ blocks.

## Gate E: Claim ledger and red-team

- `llm_focus_claim_ledger.jsonl` exists.
- `hard_red_team_verdict.json` exists.
- Any PASS claim must be backed by evidence paths.
- Any missing evidence must downgrade the verdict to WARN or BLOCK.

## Gate F: Caps carried honestly

The following caps remain active unless explicitly closed by evidence:

- `CAP_STAGE1_WITH_WARNINGS_ONLY`
- `CAP_NO_IDE_VISUAL_RELEASE_YET`
- `CAP_NO_WARP_RUNTIME`
- `CAP_EXTERNAL_FINALIZATION_RECEIPT_MISSING_OR_NEEDS_FOLLOWUP`
- `CAP_NO_LOCAL_INDEPENDENT_REPLAY_IN_REVIEW_ENVIRONMENT`

## Gate G: Git closure

If implementation artifacts are created and the verdict is PASS or PASS_WITH_WARNINGS:

- Commit the task artifacts.
- Push to origin/master.
- Prove worktree clean.
- Prove origin/master equals HEAD.
- Write `commit_push_receipt.json`.
