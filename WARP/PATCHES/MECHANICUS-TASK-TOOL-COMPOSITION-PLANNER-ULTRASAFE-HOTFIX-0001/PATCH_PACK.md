# PATCH PACK — MECHANICUS-TASK-TOOL-COMPOSITION-PLANNER-ULTRASAFE-HOTFIX-0001

status: `WARP_CANDIDATE`  
owner: `MECHANICUS`  
mode: `PLANNER_ULTRASAFE_HOTFIX`

## Purpose

Fix failed `MECHANICUS-TASK-TOOL-COMPOSITION-PLANNER-0001`.

Failure observed:

```text
tool composition planner did not run/write plan
```

## Fix

- replaces planner with v0.2 ultrasafe;
- planner always writes a plan or exception-debt plan;
- fallback taxonomy/scoring are embedded;
- original validator is rerun and must pass.
