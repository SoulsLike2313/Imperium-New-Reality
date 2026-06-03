# TASKPACK_RETENTION_POLICY_V0_1

Status: `CANDIDATE_NOT_CANON`
Owner organ: `ASTRONOMICON`
Support organs: `ADMINISTRATUM`, `INQUISITION`

## Scope

Applies to `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/**`.

## Retention rules

1. Keep current active taskpack (`ZIP + EXTRACTED + route/admission receipts`) in canonical repo.
2. Keep `MANIFEST`, `TASK_ROUTE_MANIFEST`, and `TASKPACK_ADMISSION_RECEIPT` for every registered task.
3. Review artifacts and large binary payloads should be hash-indexed and considered for quarantine pointer workflow.
4. Never delete evidence payloads without writing an explicit retention receipt.
5. For old completed tasks, keep pointer-level metadata in repo and plan external quarantine for heavy payloads.

## Action classes

- `KEEP_CANONICAL`: retain full payload in repo.
- `HASH_AND_QUARANTINE`: keep metadata+hash pointer, move heavy payload externally in follow-up.
- `KEEP_POINTER_ONLY`: retain manifest/route/receipt/hash pointer only.
- `DELETE_WITH_RECEIPT`: allowed only for non-evidence temporary payloads with explicit receipt.
- `BLOCK_FOR_OWNER_REVIEW`: do not mutate until owner decision.
