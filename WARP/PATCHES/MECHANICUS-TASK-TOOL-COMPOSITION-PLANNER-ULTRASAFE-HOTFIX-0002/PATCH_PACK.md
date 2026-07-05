# PATCH PACK — MECHANICUS-TASK-TOOL-COMPOSITION-PLANNER-ULTRASAFE-HOTFIX-0002

status: `WARP_CANDIDATE`  
owner: `MECHANICUS`  
mode: `PLANNER_HARD_SAFE_HOTFIX_V2`

## Purpose

Fix the failed ultrasafe hotfix.

The v1 hotfix wrote an exception-debt plan, then the old brittle base validator still failed.

## Fix

- install planner v0.3 hard-safe;
- install base planner validator v0.2 hard-safe-aware;
- require a real composition plan, not exception-debt;
- keep no-execution boundary.
