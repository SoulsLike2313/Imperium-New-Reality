# Cap Closure Semantics Report

Task: $taskId

## Delivered

- New Inquisition matrix: CAP_CLOSURE_SEMANTICS_MATRIX.
- New Inquisition contract: CAP_CLOSURE_SEMANTICS_CONTRACT.md.
- New schema: cap_closure_state_schema.json.

## Lifecycle states

- OPEN
- MITIGATED
- CLOSED_BY_REPLAY
- CLOSED_BY_EXTERNAL_REVIEW
- ACCEPTED_WITH_WARNING
- BLOCKING
- SUPERSEDED

## Core rule

Cap state transitions require evidence; closed states require closure proof.
No silent cap disappearance is allowed.

## Blocking contradiction

If cap closure is contradictory, force CAP_FINALIZATION_SEMANTICS_CONTRADICTORY and block clean PASS.
