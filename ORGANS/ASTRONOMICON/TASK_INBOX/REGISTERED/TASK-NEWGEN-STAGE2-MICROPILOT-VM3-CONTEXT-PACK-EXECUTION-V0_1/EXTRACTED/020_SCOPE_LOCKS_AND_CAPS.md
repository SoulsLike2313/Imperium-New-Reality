# SCOPE LOCKS AND ACTIVE CAPS

## Active caps carried into this task

- `CAP_STAGE1_WITH_WARNINGS_ONLY`
- `CAP_NO_IDE_VISUAL_RELEASE_YET`
- `CAP_NO_WARP_RUNTIME`
- `CAP_EXTERNAL_FINALIZATION_RECEIPT_MISSING_OR_NEEDS_FOLLOWUP`
- `CAP_NO_LOCAL_INDEPENDENT_REPLAY_IN_REVIEW_ENVIRONMENT`

These caps must be carried transparently unless the task produces direct evidence that a specific cap is closed.

## Locked zones

The following are explicitly locked:

- IDE runtime implementation
- WARP runtime implementation
- Browser automation runtime
- External API integration
- AdsPower API runtime actions
- Freelance execution lane
- Trading or market execution lane
- Any claim of full Block Spine canonization

## Allowed work

Allowed work is narrow:

- Context-pack consumption harness.
- Receipts and evidence for context-pack consumption.
- Economy measurement.
- Organ block usage measurement.
- Matrix/Ghost_Evolve learning note about context economy.
- Hard red-team review of this micro-pilot.
- Commit and push if PASS or PASS_WITH_WARNINGS is reached.

## Dirty-state rule

No final answer may say PASS or DONE while the worktree is dirty.

If the work succeeds with warnings, commit and push are still mandatory unless a hard blocker prevents them.

If a hard blocker prevents commit/push, final verdict must be `STOPPED_BLOCKED`, and the blocker must be recorded in the final report and receipts.

## Language rule

All committed machine/canonical artifacts must be English-only UTF-8 without BOM.

The only permitted Russian output is Owner-facing runtime summary, expected at:

`final_owner_summary_ru.md`
