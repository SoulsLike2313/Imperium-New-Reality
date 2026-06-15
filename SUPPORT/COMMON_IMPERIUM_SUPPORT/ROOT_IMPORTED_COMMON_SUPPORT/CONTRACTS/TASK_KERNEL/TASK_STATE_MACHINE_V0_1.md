# TASK STATE MACHINE V0.1

## Purpose
Defines controlled task lifecycle states for New Generation Task Kernel objects.

## Required states
- `DRAFT`
- `REGISTERED`
- `SCOPING_WITH_ORGANS`
- `READY_FOR_SERVITOR`
- `RUNNING`
- `FAILED_NEEDS_RERUN`
- `BLOCKED_NEEDS_OWNER`
- `PASSED_WITH_WARNINGS`
- `PASSED_STRICT`
- `QUARANTINED`
- `CLOSED`

## Reference transitions
- `DRAFT -> REGISTERED`
- `REGISTERED -> SCOPING_WITH_ORGANS`
- `SCOPING_WITH_ORGANS -> READY_FOR_SERVITOR`
- `READY_FOR_SERVITOR -> RUNNING`
- `RUNNING -> PASSED_STRICT`
- `RUNNING -> PASSED_WITH_WARNINGS`
- `RUNNING -> FAILED_NEEDS_RERUN`
- `RUNNING -> BLOCKED_NEEDS_OWNER`
- `FAILED_NEEDS_RERUN -> READY_FOR_SERVITOR`
- `BLOCKED_NEEDS_OWNER -> QUARANTINED`
- `BLOCKED_NEEDS_OWNER -> READY_FOR_SERVITOR`
- `PASSED_STRICT -> CLOSED`
- `PASSED_WITH_WARNINGS -> CLOSED`
- `QUARANTINED -> CLOSED`

## Guard rules
- No transition to `PASSED_STRICT` without validator pass and evidence bundle.
- `BLOCKED_NEEDS_OWNER` requires explicit owner decision before rerun.
- `QUARANTINED` means execution is paused until uncertainty/risk is resolved.
- Foundation tasks must keep `truth_status` non-live unless runtime proof exists.

## Non-live contract reminder
This state machine is a foundation artifact and does not prove live orchestration.

