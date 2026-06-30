# Next Task Improvement Report

## What made this task harder than necessary?
- action-state API and UI wiring had to be introduced in one slice without prior action contracts.
- validator/report lifecycle still requires manual ordering discipline.

## What should New Generation improve before next task?
- add canonical shared contract for action-run receipts and report ordering.

## Which organ should own that improvement?
- Mechanicus for tooling and validator automation.

## Which contract/schema/validator should be added?
- `sanctum_ng_action_execution_receipt.schema.json` with strict evidence/result guarantees.

## What context should be moved from taskpack into organs?
- reusable action-allowlist policy and smoke protocol.

## Did 256k context discipline improve clarity?
- yes, bounded read set reduced noise and prevented scope drift.

## What should the next task do immediately?
- harden action-server auth/safety checks and add deterministic smoke expectations for WARN vs PASS.
