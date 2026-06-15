# CAP_CLOSURE_SEMANTICS_MATRIX

Status: `CANDIDATE_NOT_CANON`
Owner organ: `Inquisition`
Support organs: Administratum, Mechanicus

## Purpose

Defines cap lifecycle states and forbids silent cap disappearance.

## Cap lifecycle states

- `OPEN`
- `MITIGATED`
- `CLOSED_BY_REPLAY`
- `CLOSED_BY_EXTERNAL_REVIEW`
- `ACCEPTED_WITH_WARNING`
- `BLOCKING`
- `SUPERSEDED`

## PASS criteria

- Every cap transition has evidence.
- Closing states require closure evidence and closure head where relevant.
- Surviving caps remain visible when only partial mitigation exists.

## WARN criteria

- Cap is mitigated but independent replay for target is still pending.
- Cap moved to `ACCEPTED_WITH_WARNING` with explicit owner-facing note.

## BLOCK criteria

- Cap marked closed without closure evidence.
- Cap contradictions are ignored while clean PASS is claimed.
- Cap state history is overwritten without supersession trail.

## Fake-green flags

- `CAP_CLOSED_WITHOUT_EVIDENCE`
- `CAP_HISTORY_ERASED`
- `CAP_IGNORED_FOR_CLEAN_PASS`

## Evidence requirements

- cap state receipts
- claim ledger entries
- red-team verdict
