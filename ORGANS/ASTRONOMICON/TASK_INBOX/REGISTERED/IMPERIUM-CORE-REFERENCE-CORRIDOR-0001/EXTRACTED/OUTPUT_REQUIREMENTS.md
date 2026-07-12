# Output Requirements

## Human-readable report artifacts

- `OWNER_RESULT.md`
- `ARCHITECTURE_DELTA.md`
- `AUDIT_FINDINGS_CLOSURE_MATRIX.md`
- `MIGRATION_MAP.md`
- `KNOWN_GAPS.md`
- `OWNER_REVIEW_GUIDE.md`
- `LAND_PLAN.md`
- `ROLLBACK_PLAN.md`

## Machine-readable report artifacts

- `TASK_MANIFEST.json`
- `TASK_STATE.json`
- `CAPABILITY_REGISTRY.json`
- `STATE_TRANSITION_LOG.jsonl`
- `ORGAN_PARTICIPATION_LEDGER.json`
- `EVIDENCE_INDEX.json`
- `CHECKPOINT_INDEX.json`
- `VALIDATION_MATRIX.json`
- `FILES_CHANGED.json`
- `FILES_TO_LAND.json`
- `HASH_MANIFEST.json`

## Paired receipts

Each receipt must have compact JSON and Markdown forms:

- `DRIFT_GUARD_RECEIPT`
- `WARP_CREATE_RECEIPT`
- `SAFE_EXECUTION_RECEIPT`
- `VALIDATION_RECEIPT`
- `NEGATIVE_PROOF_RECEIPT`
- `UI_BACKEND_PARITY_RECEIPT`
- `OWNER_REVIEW_READY_RECEIPT`

All detailed artifacts live under `ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001/`. No root report directory or tracked runtime archive is permitted.
