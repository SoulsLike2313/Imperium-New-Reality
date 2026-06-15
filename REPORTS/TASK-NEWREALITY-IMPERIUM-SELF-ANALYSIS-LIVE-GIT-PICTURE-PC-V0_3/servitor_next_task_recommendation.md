# Servitor Next Task Recommendation

Recommended task ID:

`TASK-NEWREALITY-ASTRONOMICON-PC-FIRST-ROOT-DISCOVERY-AND-ROUTE-CONFIG-HARDENING-PC-V0_1`

## Why this should be next

The biggest operational risk found by this task is not missing cleanup; it is path discovery drift in the task-entry organ. Astronomicon can admit PC taskpacks now, but its no-argument route config discovery still points to the removed `IMPERIUM_NEW_GENERATION` prefix and is currently masked by ignored residue.

If cleanup happens before route discovery is repaired, a normal-looking removal of stale residue can break the no-argument operator workflow. Repairing Astronomicon first makes later cleanup safer and easier to verify.

## Scope

Allowed:

- PC-only local code and docs under `ORGANS/ASTRONOMICON/**` and necessary report path;
- update skill default route config discovery;
- add current-root path validation fixtures;
- record warnings for legacy fallback;
- update task-entry read-order docs/cards to current-root paths or explicit resolver aliases;
- prove PC registration does not load or require VM routes.

Forbidden:

- VM2/VM3 live execution;
- SSH;
- remote sync;
- cleanup/deletion of ignored residue;
- canon admission;
- changing Emperor Passport or Constitution.

## Minimum acceptance gates

- PC registration succeeds with no route config present.
- PC registration never performs remote route logic.
- Canonical current-root config is discovered without `--route-config` for VM dry-run mode.
- Legacy `IMPERIUM_NEW_GENERATION` config fallback emits a receipt warning and is not required.
- `MATRIX_SPINE` read-order drift is repaired through current support path or an explicit resolver alias.
- Tool cards and README entrypoints use existing current-root paths.
- Fixtures cover missing config, current config, legacy fallback, disabled VM route, PC no-config, and both paths present.
- Final report includes command receipts and git truth.

## Expected outcome

Verdict target: `PASS_WITH_WARNINGS_PC_TASK_ENTRY_HARDENED`.

After that, a separate cleanup/retention task can safely address duplicate evidence, ignored old-prefix residue, and quarantine size without breaking Astronomicon.

