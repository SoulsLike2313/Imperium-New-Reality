# TASK_SPEC

Task ID: `TASK-NEWGEN-STAGE2-MICROPILOT-VM3-CONTEXT-PACK-EXECUTION-V0_1`

## Purpose

Run a Stage2 VM3 micro-pilot proving that Servitor can execute a small, bounded task by consuming a compact task context pack instead of reading the repository broadly.

## Scope

In scope:

- Register and resolve this task through Astronomicon intake/resolver.
- Consume the existing task context pack and context bloat detector baseline.
- Produce machine-readable receipts proving what was read, why it was enough, and what broad-read actions were avoided.
- Measure before/after context economy.
- Record organ block usage.
- Carry active warnings/caps transparently.
- Commit and push the resulting task artifacts if the task reaches PASS or PASS_WITH_WARNINGS.

Out of scope:

- IDE runtime.
- WARP runtime.
- Browser automation runtime.
- External API runtime.
- AdsPower runtime actions.
- Freelance or trading readiness.
- Full canonization of Block Spine.

## Start condition

Start only after Astronomicon admission/resolver can resolve this task ID. If resolver blocks, stop and report the authority gap.

## Required start head

`cda220333299c82931f81beee461f6cb55974462`

## Owner chat trigger

`start task`
