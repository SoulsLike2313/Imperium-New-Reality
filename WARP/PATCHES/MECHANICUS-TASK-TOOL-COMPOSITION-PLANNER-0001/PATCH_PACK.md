# PATCH PACK — MECHANICUS-TASK-TOOL-COMPOSITION-PLANNER-0001

status: `WARP_CANDIDATE`  
owner: `MECHANICUS + CUSTODES + THRONE`  
mode: `TASK_TOOL_COMPOSITION_PLANNER`

## Purpose

Add Mechanicus function: plan tool composition for Patch Packs / Task Packs.

Mechanicus must inspect a task and recommend which languages, tools, validators and missing capabilities are needed.

## Core idea

```text
Task demand -> capability classes -> lane/tool candidates -> mathematical score -> recommended stack -> missing capability gaps.
```

## Boundary

The planner does not execute the task, install packages, claim runtime proof or claim 100% clean.
