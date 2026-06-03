# EXTERNAL_FINALIZATION_RECEIPT_MATRIX

Status: `CANDIDATE_NOT_CANON`
Owner organ: `Administratum`
Support organs: Inquisition, Mechanicus, Astronomicon

## Purpose

Defines honest commit finalization semantics that avoid the self-head paradox.
A file inside commit X must not pretend it can know hash X before commit X exists.
Also enforces commit/push visibility policy for Owner.

## Required fields

- `receipt_subject_head`
- `last_verified_head_before_this_commit`
- `receipt_content_head`
- `external_delivery_head`
- `remote_head_after_push`
- `verification_timestamp_utc`
- `verification_actor`
- `worktree_clean_after_push`
- `origin_master_sync_after_push`
- `verification_method`
- `self_head_paradox_handled`
- `commit_performed`
- `push_performed`
- `block_reason_class`
- `owner_action_required`
- `owner_question_or_instruction`
- `caps_triggered`
- `clean_pass_allowed`

## PASS criteria

- No ambiguous `final_head` authority claim is used for clean PASS.
- Receipt clearly separates pre-commit known head and post-push verified head.
- External/follow-up delivery verification is explicit.
- Commit/push is executed for substantial tasks, or explicit owner-input block is documented.

## WARN criteria

- External delivery verification is pending but explicitly capped.
- Historical legacy receipt still uses transitional fields without clean PASS claim.
- Commit/push skipped only because `BLOCK_OWNER_INPUT_REQUIRED_TO_CONTINUE`, with clear owner question.

## BLOCK criteria

- Receipt claims strict self-finalization from inside containing commit.
- Contradictory finalization semantics still allow clean PASS.
- Required verification booleans are missing or unknown.
- Commit/push skipped without explicit owner-input block reason and action request.

## Fake-green flags

- `SELF_HEAD_PARADOX_UNHANDLED`
- `AMBIGUOUS_FINAL_HEAD`
- `EXTERNAL_FINALIZATION_RECEIPT_MISSING`
- `FINALIZATION_SEMANTICS_CONTRADICTORY`
- `COMMIT_PUSH_POLICY_VIOLATION`
- `COMMIT_PUSH_SKIPPED_WITHOUT_OWNER_BLOCK`

## Evidence requirements

- `external_finalization_receipt.json`
- `external_finalization_receipt_schema.json`
- fixture/checker receipt showing fail + pass paths
