# Mechanicus IDE Bridge Foundation

Status: `CANON_ACTIVE_FOUNDATION`

The Imperial IDE must request tool activity through Mechanicus. The bridge starts with dry-run tool receipts and registry reads.

## Bridge Rules

1. The IDE cannot call arbitrary shell commands directly.
2. Every tool request names a registered `tool_id`.
3. Dry-run is required by default.
4. Real execution requires a future owner-approved sandbox, argument schema, allowlist, and receipts.
5. Mechanicus command receipts are the evidence boundary for IDE tool actions.
