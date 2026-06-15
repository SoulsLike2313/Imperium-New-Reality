# ACCEPTANCE GATES

## Gate 1: Astronomicon admission

Required:

- taskpack is admitted through Astronomicon on PC, or an admission blocker is fully reported;
- bundled source archives remain accessible after extraction;
- TASK_ROUTE_MANIFEST_TEMPLATE.json is present in the taskpack root;
- TASK_START_ACK_TEMPLATE.json is present in the taskpack root;
- current expected task is updated if admission succeeds;
- no success is claimed without registry evidence.

PASS_WITH_WARNINGS is acceptable.
Clean PASS is forbidden unless every gate is fully proven.

## Gate 2: bundled source inventory

Required:

- Workbench ZIP is present in SOURCE_BUNDLES;
- WARP ZIP is present in SOURCE_BUNDLES;
- MetaOS ZIP is present in SOURCE_BUNDLES;
- SHA256 is recorded for all three;
- file inventories are recorded for all three;
- no bundle is imported directly to repository root.

## Gate 3: candidate import

Required:

- Workbench imported under ORGANS/IMPERIAL_IDE/WORKBENCH;
- WARP imported under ORGANS/IMPERIAL_IDE/WARP;
- MetaOS imported under ORGANS/IMPERIAL_IDE/METAOS;
- import receipts exist;
- existing Imperial IDE shell is not replaced;
- optional WPF remains candidate unless Windows build receipt exists.

## Gate 4: normalization

Required:

- governance references updated to CANON_ACTIVE;
- validated-push policy is current;
- CUSTODES is not silently added to baseline required organs;
- SAMPLE mode is clearly labelled;
- real execution flags remain blocked;
- live LLM backend remains disabled;
- missing README references are fixed or documented;
- runtime paths are ignored.

## Gate 5: Workbench integration

Required:

- Workbench integration status exists;
- Workbench launcher exists;
- Workbench TUI or GUI smoke is attempted;
- Workbench bridge loads sample or live data with honest mode label;
- Workbench is linked from Imperial IDE shell or panel registry.

## Gate 6: WARP integration

Required:

- WARP integration status exists;
- WARP launcher exists;
- WARP shell commands or command palette entries exist;
- WARP panel is registered;
- WARP smoke passes or exact blocker is recorded;
- WARP runtime paths are ignored;
- kernel promotion is not performed in this task.

## Gate 7: MetaOS integration

Required:

- MetaOS integration status exists;
- MetaOS launcher exists;
- MetaOS shell commands or command palette entries exist;
- MetaOS panel is registered;
- MetaOS smoke passes or exact blocker is recorded;
- thin servitor runtime remains candidate or dry-run;
- live LLM backend remains disabled.

## Gate 8: Mechanicus triple bridge

Required:

- Workbench bridge adapter exists or exact blocker is recorded;
- WARP bridge adapter exists or exact blocker is recorded;
- MetaOS bridge adapter exists or exact blocker is recorded;
- dry-run remains default;
- unknown tool invocation returns BLOCKED;
- real execution remains blocked;
- bridge receipt exists.

## Gate 9: Administratum bundle gate

Required:

- bundle gate adapter or integration receipt exists;
- HELD behavior is tested;
- RELEASED behavior is tested if possible;
- WARP work is not promoted to kernel automatically;
- evidence level is recorded.

## Gate 10: safety

Required:

- unsafe shell execution is unavailable;
- AllowReal is disabled;
- real servitor execution is disabled;
- live LLM backend is disabled;
- no VM2 or VM3 action occurs;
- no destructive cleanup occurs;
- no runtime directory is staged;
- no local route config or secret is staged.

## Gate 11: validation

Required:

- all created or modified JSON files parse;
- all created Python files compile;
- WARP smoke result exists;
- Workbench smoke result exists or environment blocker exists;
- MetaOS smoke result exists;
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

- PASS_WITH_WARNINGS_PUSHED_READY_FOR_OWNER_USE
- PASS_WITH_WARNINGS_PUSHED_READY_FOR_WINDOWS_GUI_SMOKE
- PASS_WITH_WARNINGS_PUSHED_READY_FOR_LIVE_TOOL_AND_LLM_GATE_DESIGN
- BLOCKED_UNTIL_BUNDLED_SOURCE_AVAILABLE
- BLOCKED_UNTIL_WORKBENCH_SAFETY_DECISION
- BLOCKED_UNTIL_WARP_GATE_DECISION
- BLOCKED_UNTIL_METAOS_GATE_DECISION
- BLOCKED_UNTIL_GIT_STATE_CLARITY
- BLOCKED_UNTIL_OWNER_DECISION
