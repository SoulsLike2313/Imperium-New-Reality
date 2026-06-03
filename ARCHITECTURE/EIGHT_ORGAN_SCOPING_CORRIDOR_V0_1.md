# EIGHT ORGAN SCOPING CORRIDOR V0.1

## Purpose
This document defines the New Generation foundation corridor that collects and merges 8-organ scoping packets for one task object.

The corridor is deterministic and evidence-oriented.
It is not a live autonomous multi-agent runtime.

## Scope
In-scope organs for V0.1:
1. ASTRONOMICON
2. OFFICIO_AGENTIS
3. DOCTRINARIUM
4. ADMINISTRATUM
5. MECHANICUS
6. INQUISITION
7. STRATEGIUM
8. SCHOLA_IMPERIALIS

Out-of-scope:
- THRONE
- CUSTODES

## Inputs
The corridor consumes:
1. Astronomicon formation record and/or Task Kernel object.
2. Existing Organ Packet example set when available.
3. Repository contracts describing allowed and forbidden boundaries.

## Outputs
The corridor produces:
1. `SCOPE_REQUEST.generated.json`
2. `ORGAN_PACKETS.generated.json`
3. `ORGAN_SCOPE_MERGE_RECORD.generated.json`
4. Validator report and evidence bundle receipts.

## Processing Flow
1. Build one `ORGAN_SCOPE_REQUEST_V0_1` object for the target task.
2. Resolve packet source candidates for each of the 8 organs.
3. For each organ:
   - prefer existing static/sample packet if available;
   - otherwise build deterministic `FOUNDATION_STUB`;
   - never fabricate `LIVE_AGENT_RESPONSE`.
4. Normalize and merge packet guidance:
   - allowed paths
   - forbidden paths
   - required checks
   - evidence requirements
   - owner questions
5. Detect conflicts and missing coverage.
6. Emit merge record with readiness and truth limitations.

## Source Classification Rules
Allowed packet source labels:
- `STATIC_FILE`
- `SAMPLE_PACKET`
- `FOUNDATION_STUB`
- `MISSING_IMPLEMENTATION_WARN`
- `LIVE_AGENT_RESPONSE` (reserved; not used in this foundation task)

For V0.1 foundation corridor:
- `LIVE_AGENT_RESPONSE` is prohibited unless real runtime evidence is present.
- Absence of live organ responders must be explicit.

## Merge Semantics
Merge output is bounded and deterministic:
1. Arrays are de-duplicated and sorted where possible.
2. Missing organ packets create warning entries, not silent pass.
3. Conflicting guidance is preserved in `conflicts`.
4. Readiness is derived from coverage and warning severity.

Readiness levels:
- `READY`
- `READY_WITH_WARNINGS`
- `BLOCKED`
- `FOUNDATION_ONLY`

## Contract Alignment
The corridor aligns with existing New Generation foundations:
- `TASK_KERNEL_V0_1`
- `ORGAN_PACKET_SET_V0_1`
- `TASK_FORMATION_RECORD_V0_1`

It extends them by adding a merge-layer contract for one task-scoping pass.

## No-Fake-Green Boundary
This V0.1 corridor may claim only:
- deterministic collection and merge of available static/sample/stub packets.

It may not claim:
- live autonomous cross-organ agent dialogue,
- production orchestration,
- runtime execution readiness beyond foundation evidence.

## Next Step
Follow-up tasks should implement:
1. guarded live packet resolvers per organ;
2. contradiction resolution policy upgrades;
3. stage transition hook from merged scope to Servitor execution start.
