# SERVITOR RUN RERUN LOOP V0.1

## Purpose
Servitor Run/Rerun Loop V0.1 defines the first NewGen execution envelope that transforms:

- Task Kernel object,
- 8-organ merged scope record,

into deterministic Servitor session/run/rerun records with evidence boundaries.

This is a foundation layer only.
It is not a production autonomous executor.

## Inputs
Primary inputs:
1. `TASK_KERNEL_V0_1` object or sample equivalent.
2. `ORGAN_SCOPE_MERGE_RECORD.generated.json` from the 8-organ scoping corridor.
3. Officio and Doctrinarium ACK/WARN receipts.

Fallback input mode:
- If a primary input is missing, the builder must emit explicit WARN markers and continue in bounded foundation mode when safe.

## Outputs
The loop emits:
1. `SERVITOR_EXECUTION_SESSION.generated.json`
2. `RUN_RECORD_001.generated.json`
3. `RERUN_DECISION_RECORD.generated.json`
4. Validator report and final task receipt artifacts.

## Execution Session Lifecycle
Session states for V0.1:
- `CREATED`
- `AUTHORITY_ACKED_WITH_WARNINGS`
- `SCOPED_BY_ORGANS`
- `READY_FOR_RUN`
- `RUNNING`
- `RUN_FAILED_NEEDS_RERUN`
- `BLOCKED_NEEDS_OWNER`
- `PASSED_WITH_WARNINGS`
- `PASSED_STRICT`
- `CLOSED_FOUNDATION_ONLY`

Session object responsibilities:
1. bind scope and truth-level inputs,
2. register planned run stages,
3. expose no-fake-green boundary fields,
4. store owner/organ question hooks.

## Run Lifecycle
Run states for V0.1:
- `PLANNED`
- `STARTED`
- `CHECKED`
- `FAILED_CLASSIFIED`
- `RERUN_PLANNED`
- `PASSED_WITH_EVIDENCE`
- `BLOCKED`

Run record responsibilities:
1. track run index and status,
2. attach checks and classified failure,
3. store evidence pointers and bounded explanation.

## Rerun Decision Policy
Rerun decision values:
- `RERUN_ALLOWED`
- `RERUN_REQUIRED`
- `ASK_OWNER`
- `ASK_ORGAN`
- `BLOCKED`
- `PASS_WITH_WARNINGS`
- `PASS_STRICT`

Deterministic decision factors:
1. failure classification,
2. missing tool/skill/authority flags,
3. scope ambiguity,
4. fake-green risk marker,
5. foundation limitation marker.

## Failure Classifications
Minimum failure classes:
- `TASK_ARCHITECTURE_FAILURE`
- `SCOPE_AMBIGUITY`
- `SKILL_GAP`
- `TOOL_MISSING`
- `VALIDATOR_FAILURE`
- `VISUAL_MISMATCH`
- `FAKE_GREEN_RISK`
- `OWNER_DECISION_REQUIRED`
- `FOUNDATION_LIMITATION`

## Organ Question Hook
If scoping or execution conditions require organ clarification:
1. write question entries to session/run/rerun records,
2. classify route as `ASK_ORGAN`,
3. avoid simulating live dialogue when no live adapter exists.

## Owner Question Hook
If progression requires Owner decision:
1. set rerun decision to `ASK_OWNER` or `BLOCKED`,
2. register concise question and impact,
3. keep evidence path pointers explicit.

## No-Fake-Green Boundary
Allowed claim for V0.1:
- deterministic execution envelope records were built and validated.

Forbidden claims:
- real autonomous Servitor execution,
- live 8-organ dialogue,
- production orchestration readiness,
- successful real-world task completion based on this foundation alone.

## Next Steps
1. add guarded live adapter interfaces for organ responses,
2. bind run records to real tool execution receipts,
3. connect rerun policy to Task Kernel state transitions,
4. integrate escalation policy for Owner and organ decision loops.
