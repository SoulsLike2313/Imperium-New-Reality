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

## Gate 2: shell entrypoints

Required:

- Imperial IDE shell directory exists;
- imperial_ide_cli.py exists;
- imperial_ide_tui.py exists or a precise blocker is recorded;
- shell_router.py exists or equivalent routing is implemented;
- run_imperial_ide.ps1 exists;
- non-interactive smoke is available.

## Gate 3: shell commands

Required commands must exist or return structured BLOCKED status:

- doctor;
- status;
- dashboard;
- tasks;
- current-task;
- reports;
- latest-report;
- receipts;
- tools;
- capabilities;
- policy;
- extensions;
- workspace;
- validate;
- dry-run-tool;
- help.

## Gate 4: panels

Required:

- panel registry exists and parses;
- overview panel exists;
- governance panel exists;
- tasks panel exists;
- reports panel exists;
- receipts panel exists;
- tools panel exists;
- capabilities panel exists;
- command policy panel exists;
- extensions panel exists;
- workspace panel exists;
- validation panel exists.

## Gate 5: Mechanicus bridge

Required:

- bridge loads tool registry;
- bridge loads capability registry;
- bridge loads command policy;
- bridge can list tools;
- bridge can list capabilities;
- bridge can create dry-run receipt;
- unsafe real execution remains blocked;
- no arbitrary shell gateway is enabled.

## Gate 6: Astronomicon dashboard integration

Required:

- shell can locate task inbox registered directory or record blocker;
- shell can list registered tasks or record blocker;
- shell can show current expected task or record absence;
- shell can list reports or record absence;
- shell can show receipts or record absence.

## Gate 7: workspace and extension model

Required:

- workspace state exists and parses;
- workspace state manager exists or blocker is recorded;
- extension registry exists and parses;
- extension loader exists or blocker is recorded;
- example Mechanicus extension exists and parses;
- no extension grants unrestricted execution authority.

## Gate 8: safety

Required:

- dry-run is default for tool invocation;
- real execution is blocked unless explicitly allowlisted and receipted;
- unsafe shell execution is not available;
- secrets and local route configs are not staged;
- no VM2 or VM3 command is run;
- no destructive cleanup is performed.

## Gate 9: validation

Required:

- all created or modified JSON files parse;
- all created Python files compile;
- shell doctor smoke passes or exact blocker is recorded;
- dashboard smoke passes or exact blocker is recorded;
- Mechanicus dry-run smoke passes or exact blocker is recorded;
- validation receipt exists;
- git diff is inside allowed_write_scope.

## Gate 10: validated push

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

- PASS_WITH_WARNINGS_PUSHED_READY_FOR_GUI_WORKBENCH_BUILD
- PASS_WITH_WARNINGS_PUSHED_READY_FOR_OWNER_REVIEW
- BLOCKED_UNTIL_SHELL_SAFETY_DECISION
- BLOCKED_UNTIL_MECHANICUS_BRIDGE_DECISION
- BLOCKED_UNTIL_GIT_STATE_CLARITY
- BLOCKED_UNTIL_OWNER_DECISION
