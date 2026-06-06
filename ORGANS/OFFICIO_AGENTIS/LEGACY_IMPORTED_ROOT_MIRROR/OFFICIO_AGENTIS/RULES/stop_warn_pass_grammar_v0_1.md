# STOP/WARN/PASS Grammar V0.1

## STOP

Use `STOP` when:
- git truth mismatch;
- required task contracts are missing;
- forbidden paths are required;
- command failure creates unsafe partial dirty state;
- evidence for critical claim cannot be produced.

## WARN

Use `WARN` when:
- core deliverables exist but some non-blocking quality gaps remain;
- TUI is basic but real;
- report contains explicit not-run notes with reasons.

`WARN` never allows fake-green claims.

## PASS

Use `PASS` only when:
- acceptance criteria are fully satisfied;
- required receipts are present and parseable;
- touched paths are in scope;
- final report is evidence-bound.

## Forbidden Verdict Patterns

- `PASS` without receipts.
- broad readiness claims outside task scope.
- claiming implemented runtime/UI behavior when only contracts exist.
