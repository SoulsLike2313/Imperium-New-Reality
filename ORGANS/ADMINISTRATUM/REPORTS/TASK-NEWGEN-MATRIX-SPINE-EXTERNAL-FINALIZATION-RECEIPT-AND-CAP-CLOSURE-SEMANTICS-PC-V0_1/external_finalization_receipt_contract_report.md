# External Finalization Receipt Contract Report

Task: $taskId

## Delivered

1. New matrix: EXTERNAL_FINALIZATION_RECEIPT_MATRIX (Administratum owner).
2. New contract: EXTERNAL_FINALIZATION_RECEIPT_CONTRACT.md.
3. New schema: xternal_finalization_receipt_schema.json.
4. Matrix Spine index updated with new matrix entry.

## Mandatory receipt semantics

- Distinguish pre-commit known head from post-push verified head.
- Record explicit external delivery verification.
- Track self_head_paradox_handled and clean_pass_allowed.

## Guardrails

- CAP_SELF_HEAD_PARADOX
- CAP_AMBIGUOUS_FINAL_HEAD
- CAP_EXTERNAL_FINALIZATION_RECEIPT_MISSING
- CAP_FINALIZATION_SEMANTICS_CONTRADICTORY

Clean PASS is disallowed while these caps are active.
