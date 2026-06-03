# Acceptance criteria

A PASS_WITH_WARNINGS is acceptable if target caps are closed or narrowed with honest receipts and all carried caps remain explicit.

A clean PASS is allowed only if:
- external_finalization_receipt.json exists and supports closure of the external finalization cap;
- independent_replay_receipt.json exists and supports closure of the local independent replay cap;
- cap_closure_decision.json marks no unresolved target cap;
- positive-control fixtures are recorded;
- hard_red_team_verdict.json agrees with the closure decision;
- commit/push succeeds and worktree is clean.

A BLOCK is required if:
- this TASK_ID cannot be resolved through Astronomicon;
- previous Stage2 evidence cannot be located;
- independent replay cannot be executed or honestly simulated with a replay-equivalent method;
- output receipts are missing;
- the task tries to expand into IDE, WARP, browser, API, freelance, or trading runtime.
