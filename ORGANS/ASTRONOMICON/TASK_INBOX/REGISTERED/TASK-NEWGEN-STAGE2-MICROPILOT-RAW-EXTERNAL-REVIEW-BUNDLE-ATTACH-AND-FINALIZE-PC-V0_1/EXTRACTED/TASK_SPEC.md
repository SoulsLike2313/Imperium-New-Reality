# Task Spec

## Task ID

`TASK-NEWGEN-STAGE2-MICROPILOT-RAW-EXTERNAL-REVIEW-BUNDLE-ATTACH-AND-FINALIZE-PC-V0_1`

## Purpose

On the PC contour, attach raw external review bundles supplied by Owner, verify them by hash, and make a final honest decision for the remaining Stage2 micro-pilot external-finalization cap.

This task must not expand into IDE, WARP, browser/API runtime, freelance readiness, trading readiness, or launcher implementation.

## Background

Previous accepted task:

`TASK-NEWGEN-STAGE2-MICROPILOT-EXTERNAL-FINALIZATION-AND-INDEPENDENT-REPLAY-CAP-CLOSURE-VM3-V0_1`

Final reviewed HEAD:

`1c435a944ed6fbf8bbe5ef7c24a0b8a29c1c9860`

Accepted status:

`PASS_WITH_WARNINGS__LOCAL_INDEPENDENT_REPLAY_CLOSED__EXTERNAL_FINALIZATION_NARROWED__GLOBAL_CAPS_ACTIVE`

Closed cap:

`CAP_NO_LOCAL_INDEPENDENT_REPLAY_IN_REVIEW_ENVIRONMENT`

Remaining cap to adjudicate:

`CAP_EXTERNAL_FINALIZATION_RECEIPT_MISSING_OR_NEEDS_FOLLOWUP`

Reason it was not fully closed:

Raw external review bundles were not yet attached as controlled evidence. Owner has now supplied raw review bundles to attach or verify on the PC contour.

## Required work

1. Verify PC repo state at `E:/IMPERIUM` and expected HEAD chain.
2. Stop if the worktree is dirty before admission, unless only taskpack-local staging is explicitly owner-approved.
3. Extract or copy nested raw external review bundles from `EXTERNAL_REVIEW_BUNDLES/` into a controlled repo evidence path.
4. Hash-check every raw bundle against `INPUTS/raw_external_review_bundle_inventory_input.json`.
5. Classify each bundle by reviewer, target head, and task relation.
6. Verify whether the f3123e5 Stage2 micro-pilot external reviews are present and hash-checked.
7. Verify whether the 1c435a9 cap-closure external reviews are present and hash-checked.
8. Decide whether `CAP_EXTERNAL_FINALIZATION_RECEIPT_MISSING_OR_NEEDS_FOLLOWUP` is now `CLOSED`, remains `NARROWED`, or must be `CARRIED`.
9. Preserve Astronomicon positive-control cases learned during the taskpack launch sequence.
10. Register Owner-discussed future launcher requirements as next task candidates, without implementing them.
11. Commit and push if outputs are complete and no blocker remains.

## Required repo paths

Use these preferred paths unless a stronger existing convention exists:

- Raw external review bundles:
  `IMPERIUM_NEW_GENERATION/BLOCK_SPINE/EXTERNAL_REVIEWS/TASK-NEWGEN-STAGE2-MICROPILOT-RAW-EXTERNAL-REVIEW-BUNDLE-ATTACH-AND-FINALIZE-PC-V0_1/`

- Reports:
  `IMPERIUM_NEW_GENERATION/BLOCK_SPINE/REPORTS/TASK-NEWGEN-STAGE2-MICROPILOT-RAW-EXTERNAL-REVIEW-BUNDLE-ATTACH-AND-FINALIZE-PC-V0_1/`

- Learning or next-task notes may be placed under the report directory, or under organ-specific note locations if existing conventions already define them.

## Important owner discussion to integrate

Two future launcher mechanisms must be registered as next-task candidates:

1. Astronomicon-owned VM3 taskpack launcher and IDE handoff bridge.
2. Administratum-owned continuity pack launcher and Logos-Prime handoff bridge.

Do not implement either in this task. Only preserve the decision and create clean candidate records.
