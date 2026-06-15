# ACCEPTANCE GATES

## Gate 1: Astronomicon admission

Required:

- taskpack is admitted through Astronomicon on PC, or an admission blocker is fully reported;
- bundled OPS source archive remains accessible after extraction;
- TASK_ROUTE_MANIFEST_TEMPLATE.json is present in the taskpack root;
- TASK_START_ACK_TEMPLATE.json is present in the taskpack root;
- current expected task is updated if admission succeeds;
- no success is claimed without registry evidence.

PASS_WITH_WARNINGS is acceptable.
Clean PASS is forbidden unless every gate is fully proven.

## Gate 2: source inventory

Required:

- IMPERIUM_IDE_OPERATIONAL_V0_1.zip is present in SOURCE_BUNDLES;
- SHA256 is recorded;
- file inventory is recorded;
- candidate status is recorded;
- no bundle is imported directly to repository root.

## Gate 3: OPS import

Required:

- OPS imported under ORGANS/IMPERIAL_IDE/OPS;
- internal structure includes OPS/ENGINE/imperium_ops;
- CLI exists under OPS/CLI or equivalent;
- TUI exists under OPS/TUI or equivalent;
- TESTS exists or source absence is recorded;
- import receipt exists;
- existing Imperial IDE shell is not replaced.

## Gate 4: known bug fixes

Required:

- validate_intent returns tuple[bool, list[str]];
- CLI classify no longer crashes with ValueError;
- CLI and TUI can locate OPS engine after integration;
- push policy wording is aligned with validated-push law;
- live registration path is explicit or safely blocked with reason.

## Gate 5: Astronomicon-compatible builder

Required:

- builder can create six root files;
- generated MANIFEST schema_version is astronomicon.taskpack.v0_1;
- generated MANIFEST contains language_and_encoding_policy.cyrillic_in_taskpack;
- generated MANIFEST contains required_organs;
- generated MANIFEST contains organ_route;
- generated taskpack root files parse and are UTF-8 no BOM;
- generated taskpack smoke receipt exists.

## Gate 6: CLI activation

Required commands or structured blockers:

- ops;
- ops-smoke;
- task-console;
- classify-task;
- build-taskpack;
- register-taskpack;
- launch-card;
- lifecycle;
- lifecycle-smoke;
- git-closure;
- task-templates.

## Gate 7: GUI Workbench wiring

Required:

- Task Console panel or registry entry exists;
- Taskpack Builder panel or registry entry exists;
- Registration panel or registry entry exists;
- Launch Card panel or registry entry exists;
- Lifecycle panel or registry entry exists;
- Git Closure panel or registry entry exists;
- existing Workbench still opens or exact blocker is recorded.

## Gate 8: TUI activation

Required:

- TUI exposes task console path or structured blocker;
- TUI exposes build taskpack path or structured blocker;
- TUI exposes launch card or structured blocker;
- TUI exposes lifecycle dry-run or structured blocker;
- TUI smoke or non-interactive menu validation exists.

## Gate 9: template library

Required:

- task_templates.json exists and parses;
- minimum templates are present:
  audit, repair, build, integration, cleanup_staging, mechanicus_tool, ide_extension, warp_experiment, metaos_orchestration, governance_update, report_generation.

## Gate 10: lifecycle and safety

Required:

- lifecycle dry-run smoke exists;
- fake-green bare PASS is caught;
- incomplete bundle is HELD;
- complete bundle is RELEASED if safe or exact blocker recorded;
- real servitor execution remains blocked;
- live LLM backend remains disabled;
- unsafe shell remains blocked;
- no VM2 or VM3 action;
- no runtime directory staged.

## Gate 11: validation

Required:

- all created or modified JSON files parse;
- all created or modified Python files compile;
- OPS smoke passes or exact blocker recorded;
- generated taskpack smoke passes;
- validation receipt exists;
- git diff is inside allowed_write_scope.

## Gate 12: validated push

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

- PASS_WITH_WARNINGS_PUSHED_READY_FOR_INSIDE_IDE_TASK_CREATION
- PASS_WITH_WARNINGS_PUSHED_READY_FOR_OWNER_REVIEW
- PASS_WITH_WARNINGS_PUSHED_READY_FOR_LIVE_REGISTRATION_GATE
- BLOCKED_UNTIL_OPS_IMPORT_FIX
- BLOCKED_UNTIL_TASKPACK_BUILDER_FIX
- BLOCKED_UNTIL_SAFETY_DECISION
- BLOCKED_UNTIL_GIT_STATE_CLARITY
- BLOCKED_UNTIL_OWNER_DECISION
