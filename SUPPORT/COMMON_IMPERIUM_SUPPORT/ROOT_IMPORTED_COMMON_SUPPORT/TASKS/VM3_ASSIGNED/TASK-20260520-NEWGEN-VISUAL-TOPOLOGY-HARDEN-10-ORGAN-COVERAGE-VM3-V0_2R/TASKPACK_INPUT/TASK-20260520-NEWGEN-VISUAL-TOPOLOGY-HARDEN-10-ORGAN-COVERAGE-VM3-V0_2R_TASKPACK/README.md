# TASKPACK README

Task ID: `TASK-20260520-NEWGEN-VISUAL-TOPOLOGY-HARDEN-10-ORGAN-COVERAGE-VM3-V0_2R`

## Mission

Harden the New Generation Visual Topology skeleton so it becomes a reliable frontend architecture foundation.

This revised taskpack fixes the previous flaw: the taskpack must not act as role authority.  
It includes a hard Officio authority intake gate before implementation.

## Baseline

Previous accepted skeleton commit:

`5b2cb210b21404eb44427183544d31ca0e47f3ff`

V0.1 created the first Visual Topology skeleton, but review found WARN gaps:
- incomplete 10-organ node coverage;
- incomplete right-context panel coverage;
- weak ownership model;
- validator not semantic enough;
- possible stale HEAD in reports.

## This task is not

- not a visual concept task;
- not a CSS polish task;
- not a final UI implementation;
- not a merge of main/test into New Generation;
- not a VM2 task;
- not a laptop/Throne task.

## This task is

A V0.2 hardening step for:

`IMPERIUM_NEW_GENERATION/SANCTUM_VISUAL_FOUNDRY`
