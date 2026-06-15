# TASKPACK_RETENTION_CHECKER_MATRIX

Status: `CANDIDATE_NOT_CANON`
Owner organ: `Astronomicon`
Support organs: `Mechanicus`, `Inquisition`, `Administratum`

## Purpose

Define script-first retention checker requirements for registered taskpack payloads.

## Criteria

### TRC-01
- Criterion ID: `TRC-01_REGISTERED_INVENTORY_REQUIRED`
- PASS logic: checker scans `TASK_INBOX/REGISTERED` and emits entry inventory.
- WARN logic: inventory exists with partial optional metadata.
- BLOCK logic: checker missing or registered entries not scanned.
- Cap mapping: `CAP_RETENTION_CHECKER_MISSING`.

### TRC-02
- Criterion ID: `TRC-02_RETENTION_CLASS_REQUIRED`
- PASS logic: each entry has retention class and recommended action.
- WARN logic: classes exist but follow-up classification is pending.
- BLOCK logic: entries missing class or required receipt markers.
- Cap mapping: `CAP_RETENTION_INVENTORY_DELTA_MISSING`.

### TRC-03
- Criterion ID: `TRC-03_NO_DESTRUCTIVE_ACTIONS`
- PASS logic: checker is read-only and does not delete/move payloads.
- WARN logic: quarantine recommendation exists without execution.
- BLOCK logic: payload is deleted/moved without receipt-backed retention route.
- Cap mapping: `CAP_EVIDENCE_DELETED_WITHOUT_RECEIPT`.

## Evidence requirements

- `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TOOLS/astronomicon_taskpack_retention_checker_v0_1.py`
- `taskpack_retention_checker_receipt.json`
- `taskpack_retention_inventory_delta.json`
