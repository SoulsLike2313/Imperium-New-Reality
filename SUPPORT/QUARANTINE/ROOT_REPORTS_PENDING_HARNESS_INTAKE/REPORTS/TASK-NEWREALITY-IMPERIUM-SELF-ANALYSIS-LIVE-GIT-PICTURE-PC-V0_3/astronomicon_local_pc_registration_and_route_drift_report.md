# Astronomicon Local PC Registration and Route Drift

## Verdict

Local PC registration: `PROVEN_PASS_WITH_WARNINGS`.  
Route discovery: `DRIFT_REPAIR_REQUIRED`, not a blocker for this PC-only task.

## What works locally

The current task has complete local registration evidence:

- admission verdict `ADMISSION_PASS` at `2026-06-07T09:26:18Z`;
- language gate passed;
- safe extraction path recorded;
- task ID resolved by the Stage 2 registry;
- registered task, taskpack ZIP, extracted payload, route manifest, admission receipt, and current expected task paths recorded;
- `current_expected_task.json` points to this task;
- the registry marks this task `NEXT_EXPECTED` and `current_expected: true`;
- all eight routed participation organs are reachable;
- task start ACK verdict is `PASS_WITH_WARNINGS`.

The extracted taskpack contains `TASK_ROUTE_MANIFEST_TEMPLATE.json` and `TASK_START_ACK_TEMPLATE.json`. `MANIFEST.json` points to those names and carries the same eight organs in `organs` and `required_organs`.

## Why route drift does not block this PC task

The registration skill's `execute_registration()` handles `PC` first and returns `pc_registration(...)` before loading route config. Therefore local PC intake does not technically require VM2/VM3 configuration.

The task was admitted and resolved through local PC paths. No remote evidence is required for its mission, and no remote command was executed.

## Confirmed drift

### 1. Default route config uses the removed root prefix

The active skill is:

`ORGANS/ASTRONOMICON/SKILLS/TASKPACK_REGISTRATION_SKILL/astronomicon_taskpack_registration_skill_v0_1.py`

Its default path is constructed as:

`IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/SKILLS/TASKPACK_REGISTRATION_SKILL/contour_route_config.json`

The canonical current-root config is physically located at:

`ORGANS/ASTRONOMICON/SKILLS/TASKPACK_REGISTRATION_SKILL/contour_route_config.json`

Both configs are ignored operator-local data. The old-prefix copy exists only in the ignored five-file `IMPERIUM_NEW_GENERATION` residue. This masks the discovery bug: the stale default works while residue remains and fails when the residue is removed.

### 2. Route read order uses a missing Matrix Spine root

The current route manifest asks for:

`MATRIX_SPINE/INDEX/MATRIX_SPINE_INDEX.md`

That root path does not exist. The physical index is:

`SUPPORT/COMMON_IMPERIUM_SUPPORT/ROOT_IMPORTED_COMMON_SUPPORT/MATRIX_SPINE/INDEX/MATRIX_SPINE_INDEX.md`

This is a read-order compatibility defect. The support location is imported/candidate context, so a repair task must either admit a canonical current path or define an explicit resolver alias rather than silently treating the imported location as canon.

### 3. Mixed historical registry paths

Older registry entries retain `IMPERIUM_NEW_GENERATION/...` paths, while newer entries use current-root `ORGANS/...` paths. Historical entries should remain immutable evidence, but active resolvers must normalize current paths and label legacy paths instead of attempting them blindly.

### 4. Empty expected start head

The current route manifest and registry entry have an empty `expected_start_head`. Live git truth was still independently resolved for this task, but future admission should record the PC HEAD at registration time or explicitly mark the field `UNKNOWN_WITH_REASON`.

## Why VM2 was attempted previously

VM2 use was not accidental in the historical task. `TASK-20260605-VM2-UBUNTU-CONTOUR-COST-GATE-READINESS-V0_1` explicitly targeted `VM2_UBUNTU_OVER_SSH_FROM_PC`. Its receipt records Ubuntu 24.04.4, host `GPT2`, and VM2 root `/home/vboxuser2/IMPERIUM_NEW_GENERATION_NEW_REALITY`.

The older Astronomicon contour skill also made `PC`, `VM3`, and `VM2` peer menu choices. Its first VM2 fixture produced `WARN_ROUTE_MISSING`; later operator configuration enabled VM2 and a dedicated readiness task proved the contour.

That proof answers whether VM2 can participate. It does not establish that PC tasks should depend on VM2. A target-contour decision must come from the task manifest. PC tasks should terminate in local registration and local evidence unless their manifest explicitly authorizes a remote contour.

## Required repair for no-argument workflow

Implement deterministic discovery in this order:

1. Explicit `--route-config` path, if supplied.
2. Operator environment variable such as `ASTRONOMICON_ROUTE_CONFIG`, if set.
3. Canonical current-root path: `ORGANS/ASTRONOMICON/SKILLS/TASKPACK_REGISTRATION_SKILL/contour_route_config.json`.
4. Old-prefix compatibility fallback only when it exists, with `LEGACY_ROUTE_CONFIG_PATH_WARN` in the receipt.
5. Missing/disabled route produces `ROUTE_MISSING`; it must never synthesize remote success.

Additional hardening:

- resolve the repository root from `.git`/root markers, not from a fixed nested layout;
- do not load route config at all for `PC` contour;
- record `route_config_resolved_path`, `route_config_source`, and config hash in receipts;
- add fixtures for clean current root, legacy-only fallback, both paths present, missing config, disabled contour, and PC with no config;
- fail validation when a tool card or read-order path does not exist in the current root;
- update README, skill manifest, launchers, and tool cards to current-root paths;
- decide and record the canonical Matrix Spine address before replacing the stale read-order entry.

## Acceptance boundary for the repair

A clean pass should require:

- PC registration succeeds with both route config files absent;
- PC registration performs no SSH/remote branch;
- canonical current-root config is selected without manual arguments for VM dry-run routing;
- legacy fallback emits a warning;
- stale `IMPERIUM_NEW_GENERATION` residue is not required;
- every advertised entrypoint exists;
- no VM live execution is needed for the PC repair task.

