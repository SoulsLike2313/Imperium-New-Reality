# Doctrinarium Non-BLOCK Git Closure Law

Status: `CANDIDATE_V0_1`
Owner organ: `DOCTRINARIUM`

## Rule

Every completed non-BLOCK task must be committed and pushed unless one explicit allowed exception applies.

## Required closure sequence

1. Run required checks.
2. Stage only allowed files.
3. Commit.
4. Push.
5. Verify `origin/master == HEAD`.
6. Write fresh `commit_push_receipt.json`.
7. Include commit links in final response.

## Allowed exceptions

- BLOCK verdict.
- Unsafe gate.
- Dirty conflict requiring Owner decision.
- Failed required checks.
- Explicit Owner instruction not to commit/push.

Any exception must be recorded with evidence. No fake closure.
