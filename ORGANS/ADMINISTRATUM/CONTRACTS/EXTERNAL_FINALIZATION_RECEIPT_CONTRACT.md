# External Finalization Receipt Contract

Status: `CANDIDATE_V0_1`
Owner organ: `Administratum`

## Core rule

A file inside a commit is not required to know the hash of that same containing commit.

## Mandatory commit/push policy

Servitor must execute commit and push for substantial task residue regardless of PASS/WARN/BLOCK verdict so Owner can inspect real history.

Allowed exception:

- `BLOCK_OWNER_INPUT_REQUIRED_TO_CONTINUE`

This exception is valid only when continuation needs explicit Owner data/decision and no safe autonomous path exists.

Forbidden for clean PASS:

- strict self-finalization claim based on guessed current hash;
- ambiguous `final_head` without semantic split;
- hiding missing external delivery verification.
- skipping commit/push without `BLOCK_OWNER_INPUT_REQUIRED_TO_CONTINUE`.

## Required semantic split

- `last_verified_head_before_this_commit`
- `receipt_content_head`
- `external_delivery_head`
- `remote_head_after_push`
- `followup_finalization_receipt_head` (optional when pending)
- `commit_performed`
- `push_performed`
- `block_reason_class` (required when commit/push is skipped)
- `owner_action_required` (required when `block_reason_class` is present)
- `owner_question_or_instruction` (required when `block_reason_class` is present)

## Clean pass gate

`clean_pass_allowed` must be `false` when any cap in this set is active:

- `CAP_SELF_HEAD_PARADOX`
- `CAP_AMBIGUOUS_FINAL_HEAD`
- `CAP_EXTERNAL_FINALIZATION_RECEIPT_MISSING`
- `CAP_FINALIZATION_SEMANTICS_CONTRADICTORY`
- `CAP_COMMIT_PUSH_POLICY_VIOLATION`
- `CAP_COMMIT_PUSH_SKIPPED_WITHOUT_OWNER_BLOCK`

`commit_performed=false` or `push_performed=false` is allowed only when:

- `block_reason_class == BLOCK_OWNER_INPUT_REQUIRED_TO_CONTINUE`;
- `owner_action_required=true`;
- `owner_question_or_instruction` is non-empty and actionable.

## Migration note

Legacy `final_head` may exist for historical trace, but cannot be treated as authoritative clean-pass proof.
