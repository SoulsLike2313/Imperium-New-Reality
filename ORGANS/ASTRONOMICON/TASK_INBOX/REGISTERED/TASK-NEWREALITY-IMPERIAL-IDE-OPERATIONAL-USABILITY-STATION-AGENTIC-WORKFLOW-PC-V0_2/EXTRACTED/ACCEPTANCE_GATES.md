# ACCEPTANCE GATES

## Gate 1: Astronomicon admission

Required:

- taskpack is admitted through Astronomicon on PC, or an admission blocker is fully reported;
- TASK_ROUTE_MANIFEST_TEMPLATE.json is present in the taskpack root;
- TASK_START_ACK_TEMPLATE.json is present in the taskpack root;
- current expected task is updated if admission succeeds;
- no success is claimed without registry evidence.

PASS_WITH_WARNINGS is acceptable.
Clean PASS is forbidden unless every gate is fully proven.

## Gate 2: current system preflight

Required:

- Governance is CANON_ACTIVE or exact blocker recorded;
- Workbench TUI exists;
- Workbench GUI exists or exact blocker recorded;
- OPS exists;
- WARP status file exists or exact blocker recorded;
- MetaOS status file exists or exact blocker recorded;
- Mechanicus command policy exists or exact blocker recorded.

## Gate 3: station architecture

Required:

- ORGANS/IMPERIAL_IDE/STATION exists;
- station state model exists;
- station router exists;
- station receipts helper exists;
- station workflow exists;
- station panels registry exists and parses;
- operational state schema exists and parses.

## Gate 4: unified TUI

Required:

- existing Workbench TUI is preserved;
- operational menus are added;
- Task Console entry exists;
- Build Taskpack entry exists;
- Register Taskpack entry exists;
- Agent and Servitor view exists;
- Safety view exists;
- Git Closure view exists;
- TUI station smoke exists.

## Gate 5: Workbench GUI

Required:

- GUI structural smoke is attempted;
- Task Console panel or equivalent section exists;
- Agent Roster panel or equivalent section exists;
- Lifecycle panel or equivalent section exists;
- Safety Center panel or equivalent section exists;
- Git Closure panel or equivalent section exists;
- existing organ panels are not removed.

## Gate 6: agents and servitors

Required:

- agent registry exists and parses;
- servitor roster exists and parses;
- agent card schema exists and parses;
- agent status schema exists and parses;
- Servitor Prime exists;
- organ servitors exist for baseline organs;
- WARP and MetaOS servitors exist;
- each agent has owner_organ, allowed_actions, blocked_actions, status, and execution_mode.

## Gate 7: task console usability

Required:

- task templates are visible from station;
- new task intent can be created or smoke-created;
- task can be classified or structured blocker recorded;
- route preview is available or blocker recorded;
- taskpack can be built;
- taskpack can be validated.

## Gate 8: live registration gate

Required:

- dry-run registration remains default;
- live local PC registration action exists or exact blocker recorded;
- live registration is only for validated generated taskpacks;
- registration receipt exists;
- launch card is captured or exact blocker recorded;
- remote contour registration is not enabled.

## Gate 9: lifecycle tracker

Required:

- lifecycle tracker exists;
- lifecycle state schema exists;
- lifecycle stages are recorded;
- handoff-ready is distinct from execution-done;
- lifecycle smoke exists.

## Gate 10: reports, receipts, and git closure

Required:

- latest reports can be listed;
- latest receipts can be listed;
- safety state is visible;
- git status and HEAD/origin are visible;
- git closure status is visible;
- push is not claimed without receipt.

## Gate 11: safety

Required:

- real servitor execution remains disabled;
- live LLM backend remains disabled;
- unsafe shell remains blocked;
- unknown tool remains blocked;
- no VM2 or VM3 action;
- no destructive cleanup;
- no runtime directory staged;
- no local route config or secret staged.

## Gate 12: validation

Required:

- all created or modified JSON files parse;
- all created or modified Python files compile;
- station smoke passes or exact blocker recorded;
- Workbench TUI smoke passes or exact blocker recorded;
- generated taskpack smoke passes;
- validation receipt exists;
- git diff is inside allowed_write_scope.

## Gate 13: validated push

Required for PASS:

- commit created with task ID;
- push to origin/master completed;
- post-push HEAD equals origin/master;
- git_commit_push_receipt.json exists;
- no failed validation is hidden.

Push is allowed for validated task outputs.
Push is required for success.
Push is forbidden only for dirty, secret, destructive, out-of-scope, unsafe, or failed-validation changes.

## Final verdicts allowed

- PASS_WITH_WARNINGS_PUSHED_READY_FOR_OWNER_OPERATIONAL_USE
- PASS_WITH_WARNINGS_PUSHED_READY_FOR_LIVE_SERVITOR_EXECUTION_GATE
- PASS_WITH_WARNINGS_PUSHED_READY_FOR_OWNER_REVIEW
- BLOCKED_UNTIL_TUI_INTEGRATION_DECISION
- BLOCKED_UNTIL_REGISTRATION_GATE_FIX
- BLOCKED_UNTIL_SAFETY_DECISION
- BLOCKED_UNTIL_GIT_STATE_CLARITY
- BLOCKED_UNTIL_OWNER_DECISION
