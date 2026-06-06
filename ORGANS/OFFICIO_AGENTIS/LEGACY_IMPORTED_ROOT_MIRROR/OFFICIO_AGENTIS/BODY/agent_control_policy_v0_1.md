# Agent Control Policy V0.1

## Purpose

Define control rules for Servitor behavior inside Officio scope.

## Control Clauses

1. Entry is gate-bound, not free-form.
2. Scope declaration must match actual diff paths.
3. PASS requires evidence receipts.
4. Useful generated tools must be preserved or classified.
5. Command phases must be chunked and validated.

## Allowed Actions

- Read-only recon for required paths.
- Create/strengthen Officio body artifacts inside allowed scope.
- Run checkers and parsers that write only to current task report path.

## Forbidden Actions

- out-of-scope edits;
- silent destructive cleanup;
- fake readiness claims;
- claiming implemented runtime/dashboard when only contracts exist.

## Escalation

Return `STOP` or `CLARIFY` when:
- scope is incomplete;
- blocker cannot be resolved safely;
- required evidence cannot be produced.

## Status

`ACTIVE`
