# KPD / Next-Task Improvement

## What was wasteful
- Initial VM3->VM2 probe script attempt failed because nested SSH consumed stdin inside a remote heredoc.
- Validator first version bound runner-ledger detection to `task_id` substring in `request_ref`, which was not stable.

## What tools were missing
- No pre-existing bidirectional VM2<->VM3 route-proof builder/validator/smoke trio existed for this contour pair.

## Tools created and preserved
- `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/TOOLS/build_bidirectional_route_proof_vm2_vm3_v0_1.py`
- `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/TOOLS/validate_bidirectional_route_proof_vm2_vm3_v0_1.py`
- `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/TOOLS/smoke_bidirectional_route_proof_vm2_vm3_v0_1.py`

## Narrower future agent profile
- `NG_TRANSFER_ROUTE_PROOF_AGENT_VM2_VM3` with built-in stdin-safe remote execution patterns and pre-wired ledger correlation checks.

## Context-pack improvement
- Add a compact "SSH nested stdin hazard" note to taskpacks involving remote shell-on-shell operations.
- Add a reusable ledger correlation contract: task-scoped refs should be matched by summary refs, not filename heuristics.

## Next automation candidate
- Add a shared helper in Transfer Console tools for id generation + request/result/ledger emission to reduce duplicate code and drift.
