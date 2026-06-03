# Acceptance Gates

## Gate A: Admission gate

The taskpack must be registered through Astronomicon intake and resolved through Astronomicon resolver before execution.

## Gate B: Scope gate

Do not implement IDE, WARP or external API runtime. This is a Skill foundation and working TUI/CLI prototype only.

## Gate C: Skill ownership gate

Astronomicon must be the owner of the Taskpack Registration Skill. IDE may be listed as a future caller only.

## Gate D: Contour truth gate

Every contour route attempt must produce a receipt. Live success, dry run, route missing and blocked states must be distinct.

## Gate E: VM launch-card gate

A successful VM2 or VM3 registration must open a target VM terminal showing STEP, TASK_ID, registered path, TASKPACK path and copyable `start task`.

## Gate F: No fake green gate

Do not claim PASS for unavailable VM routes, unsafe syncs, unresolved registry conflicts, intake failure or resolver failure.

## Gate G: Validation gate

All new Python must pass syntax check. All JSON outputs must parse. Required receipts must exist.

## Gate H: Git closure gate

Commit/push only after validation. Record HEAD, origin/master relation and clean worktree status.
