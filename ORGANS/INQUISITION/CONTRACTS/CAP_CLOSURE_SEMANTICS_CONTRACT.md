# Cap Closure Semantics Contract

Status: `CANDIDATE_V0_1`
Owner organ: `Inquisition`

## Rule

Caps cannot disappear due to optimistic narrative.
A cap changes state only with explicit evidence and state receipt.

## Allowed states

- `OPEN`
- `MITIGATED`
- `CLOSED_BY_REPLAY`
- `CLOSED_BY_EXTERNAL_REVIEW`
- `ACCEPTED_WITH_WARNING`
- `BLOCKING`
- `SUPERSEDED`

## Closure requirements

For `CLOSED_BY_REPLAY` and `CLOSED_BY_EXTERNAL_REVIEW`:

- non-empty evidence list;
- closure head or equivalent review reference;
- trace in claim ledger.

## Contradiction gate

If cap state/evidence is contradictory, force:

- `CAP_FINALIZATION_SEMANTICS_CONTRADICTORY`
- clean PASS blocked.
