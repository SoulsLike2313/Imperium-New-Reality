# ASTRONOMICON TASK FORMATION V0.1

## Purpose
Astronomicon Task Formation V0.1 is a bounded foundation that converts a short Owner intent (2-5 lines) into a deterministic formation record.
The record is designed to bridge the intake message and the Task Kernel / Organ Packet corridor already defined in New Generation.

## What This Version Implements
Implemented now:
1. Structured intake contract (`TASK_FORMATION_REQUEST_V0_1`).
2. Deterministic formation record contract (`TASK_FORMATION_RECORD_V0_1`).
3. Stage-map preview contract (`STAGE_MAP_PREVIEW_V0_1`).
4. Deterministic builder tool for request-to-record transformation.
5. Validator with required-file, parseability, generated-output, and no-fake-green checks.

Foundation-only boundaries:
1. No live packet fetch from organs.
2. No autonomous run/rerun execution engine.
3. No production runtime orchestration claim.

## Corridor Position
Current corridor path:
1. Owner provides short intent request.
2. Astronomicon normalizes the request to structured form.
3. Astronomicon generates a Task Kernel draft-compatible object.
4. Astronomicon emits stage map preview and Servitor start block.
5. Servitor can start a bounded execution task using generated block.
6. Owner questions are emitted when intake is underspecified.

Future corridor extensions:
1. Attach real organ packet collection loop.
2. Attach rerun and blocked-escalation loop.
3. Attach runtime verification/evidence aggregation loop.

## Input Contract
Input file type:
- `IMPERIUM_NEW_GENERATION/CONTRACTS/ASTRONOMICON/TASK_FORMATION_REQUEST_V0_1.schema.json`

Minimum intake vectors:
- Owner raw intent text.
- Contour (`PC`, `VM2`, `VM3`, `UNKNOWN`).
- Scope boundaries (`allowed_paths`, `forbidden_paths`).
- Auto-closure expectation and non-live guard.

## Output Contract
Primary output:
- `TASK_FORMATION_RECORD_V0_1` JSON containing task draft scope, required organs, stage map preview, start block, limitations, and self-verdict.

Secondary output:
- Markdown formation report for quick Owner/Servitor inspection.

## Task Kernel Draft Compatibility
The formation record does not replace `TASK_KERNEL_V0_1`.
It provides draft-ready fields aligned with kernel concepts:
1. `task_id` and `task_title`.
2. `scope`, `allowed_paths`, `forbidden_paths`.
3. `required_organs` fixed to 8 in-scope organs.
4. Stage progression preview.
5. `evidence_policy` and `owner_questions` placeholders.
6. Contract pointers to Task Kernel and Organ Packet artifacts.

## Stage Map Preview Role
Stage map preview is a planning artifact only.
It is not runtime evidence.

Expected ownership contour:
1. `ASTRONOMICON`: intake normalization and initial decomposition.
2. `OFFICIO_AGENTIS`: executor-mode and response-contract alignment.
3. `DOCTRINARIUM`: gate/law alignment and no-fake-green constraints.
4. `ADMINISTRATUM`: receipt bundle completeness.
5. `MECHANICUS`: tooling/validator readiness.

## Servitor Start Block
Every formation output contains a dry start block of 2-5 lines:
1. task line,
2. mode line,
3. required-read line,
4. goal line,
5. finish criteria line.

This block is intentionally concise and reusable as the first execution prompt seed.

## No-Fake-Green Limits
Mandatory truth for V0.1:
1. Foundation-only deliverable.
2. No live multi-organ consultation claim.
3. No autonomous Servitor orchestration claim.
4. No production-readiness claim.

If these limits are violated, validator must mark failure or warnings.

## Future Tasks
Next tasks should implement:
1. Organ packet pull and merge planner (8-organ corridor).
2. Stage transition manager with blocked-state escalation.
3. Task Kernel registry write-back integration.
4. Servitor run/rerun deterministic runtime with receipts.
