# KPD / Next Task Improvement

## What slowed this task
- VM3 raw inbox/request-result artifacts were not available on VM2, so PC_TO_VM3 had to stay at `WARN_PARTIAL` despite salvage PASS traces.
- Re-running builder/smoke appends new request/result/ledger entries each run, which increases noise in state history.

## What should be moved from taskpack into organs/registries
- A canonical `route_proof_recovery` contract/schema under `TRANSFER_CONSOLE/CONTRACTS`.
- A stable route-proof status vocabulary (`PROVED`, `RECOVERED_PROVED`, `WARN_PARTIAL`, `BLOCKED_ROUTE_UNAVAILABLE`) for reuse.

## What validator/gate would reduce next prompt size
- A dedicated gate for "partial-recovery honesty" that enforces `WARN` on blocked/unavailable routes.
- A compact fixture-mode for transfer runner tests to avoid repetitive ledger growth during validation loops.

## Recommended next task
- `TASK-NEXT-TRANSFER-ROUTE-PROOF-VM2-VM3-LIVE-PROBE-ENABLEMENT-V0_1`:
  - install/verify `imperium-vm3` alias or explicit route in VM2 scope,
  - run one bounded VM2->VM3 probe with hash/size receipt,
  - upgrade verdict from `WARN_PARTIAL` to scoped `PASS` if evidence is concrete.
