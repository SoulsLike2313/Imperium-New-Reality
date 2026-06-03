# TASK STATE EVIDENCE BINDER V0.1

## Purpose
Task State + Evidence Binder V0.1 is a bounded NewGen foundation layer that binds:

1. Task Kernel object,
2. 8-organ scope merge record,
3. Servitor execution session,
4. run record,
5. rerun decision record,

into deterministic task-state transition proposals and replayable evidence index records.

## Inputs
Primary expected inputs:
1. `TASK_KERNEL` object (sample or generated),
2. `ORGAN_SCOPE_MERGE_RECORD.generated.json`,
3. `SERVITOR_EXECUTION_SESSION.generated.json`,
4. `RUN_RECORD_001.generated.json`,
5. `RERUN_DECISION_RECORD.generated.json`.

Fallback policy:
- Missing inputs are allowed only in foundation mode with explicit markers:
  - `FOUNDATION_SAMPLE_INPUT`,
  - `MISSING_INPUT_WARN`,
  - `FOUNDATION_ONLY`,
  - `NOT_PRODUCTION_EXECUTOR`.

## Outputs
Binder outputs:
1. `TASK_STATE_TRANSITION_PROPOSAL.generated.json`
2. `EVIDENCE_REPLAY_INDEX.generated.json`
3. validator report and evidence receipts in task report folder.

## Transition Proposal Lifecycle
Transition proposal lifecycle (foundation):
1. collect source record statuses,
2. infer current state from run/rerun/session inputs,
3. propose bounded next state,
4. classify failure/risk,
5. mark owner/organ escalation needs,
6. bind evidence replay index reference.

States are proposals, not live runtime truth mutations.

## Evidence Replay Index Lifecycle
Evidence replay index lifecycle:
1. gather evidence pointers from available records,
2. register replay order for deterministic inspection,
3. list missing evidence explicitly,
4. declare allowed and forbidden truth claims.

Index role for future visual brain:
- provide replayable evidence map for UI state rendering.

## No-Fake-Green Boundary
Allowed claims:
1. deterministic generation of transition and replay-index artifacts,
2. explicit missing-input warnings,
3. bounded truth-claim allow/forbid lists.

Forbidden claims:
1. production autonomous execution,
2. live organ dialogue,
3. guaranteed runtime truth coverage,
4. full visual brain readiness in this task.

## Relation to Existing Foundations
Binder is downstream of:
1. `TASK_KERNEL_REGISTRY_V0_1`,
2. `EIGHT_ORGAN_SCOPING_CORRIDOR_V0_1`,
3. `SERVITOR_RUN_RERUN_LOOP_V0_1`.

Binder does not replace those layers.
It adds the state/evidence bridge required before visual corridor work.

## Owner/Organ Escalation Fields
Transition proposal must expose:
1. `owner_escalation_required`,
2. `organ_escalation_required`,
3. explicit `failure_classification`,
4. explicit `fake_green_risk`.

## Next-Step Hook
Primary consumer after this task:
- `TASK-20260521-NEWGEN-VISUAL-BRAIN-TASK-CORRIDOR-PC-V0_1`

This next task can render truthful visual state by consuming:
1. transition proposal,
2. evidence replay index,
3. explicit limitation markers.
