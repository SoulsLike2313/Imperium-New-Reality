# Next Task Improvement Report

## Recommended next task
- `TASK-20260523-NEWGEN-PQG-ACTION-ROLLBACK-CONTRACT-VM3-V0_1`

## Why
- Acceptance semantics now distinguish strict/warn/partial/blocked states.
- Next improvement is to make continuation safety explicit via rollback contract discipline.

## Improvements
- Bind ACTION_ROLLBACK outcomes to acceptance states.
- Link partial acceptance flows to negative-test expectations.
- Add explicit ownership fields for partial acceptance decisions in rollback receipts.
