# TASK KERNEL REGISTRY V0.1

## Purpose
This document defines the New Generation Task Kernel / Registry foundation.
It converts short Owner intent into a registered task object contract with bounded state progression.

## Corridor intent
Target conceptual corridor:
1. Owner short intent (2-5 lines).
2. Astronomicon task object formation.
3. Organ packet collection against the task object.
4. Servitor execution and rerun discipline.
5. Evidence bundle and Owner verdict.

This task provides contracts and examples only.
It does not claim live orchestration runtime.

## Core artifacts
- `CONTRACTS/TASK_KERNEL/TASK_KERNEL_V0_1.schema.json`
- `CONTRACTS/TASK_KERNEL/TASK_REGISTRY_INDEX_V0_1.schema.json`
- `CONTRACTS/TASK_KERNEL/TASK_STATE_MACHINE_V0_1.md`
- `CONTRACTS/TASK_KERNEL/EXAMPLES/SAMPLE_TASK_KERNEL_OBJECT_V0_1.json`
- `TASKS/REGISTRY/TASK_INDEX_V0_1.json`

## Task Kernel object role
Task Kernel is the canonical task envelope for New Generation workflows.
It must define:
- identity and metadata;
- scope and boundaries;
- required organs and packet reference;
- stage map and run policy;
- evidence and bundle policy;
- truth/non-live status and explicit limitations.

## Registry role
Task Registry index is a compact index of task kernels.
It provides:
- discoverability;
- status scan;
- safe handoff points for future kernel runner tasks.

## Foundation-only truth
- Contract artifacts are machine-readable and deterministic.
- Example object demonstrates structure only.
- Live multi-organ execution is explicitly marked as future work.

## Next foundation direction
Expected next task:
- `TASK-NEWGEN-TASK-KERNEL-REGISTRY-PC-V0_1` follow-up run/rerun utilities
or
- dedicated task-kernel runner admission task (Owner decision).

