# VISUAL BRAIN TASK CORRIDOR V0.1

## Purpose
Visual Brain Task Corridor V0.1 is a truth-bound static visual layer for NewGen.
It renders a bounded corridor view from existing receipts and generated state records.

This version is foundation-only:
- no live backend orchestration;
- no autonomous organ dialogue;
- no production readiness claim.

## Upstream Dependencies
Visual Brain Task Corridor V0.1 consumes foundation artifacts from:
1. Task Kernel Registry V0.1
2. Astronomicon Task Formation V0.1
3. 8-Organ Scoping Corridor V0.1
4. Servitor Run/Rerun Loop V0.1
5. Task State + Evidence Binder V0.1

## Input Surfaces
Primary builder inputs:
1. `TASK_STATE_TRANSITION_PROPOSAL.generated.json`
2. `EVIDENCE_REPLAY_INDEX.generated.json`
3. `ORGAN_SCOPE_MERGE_RECORD.generated.json`
4. `SERVITOR_EXECUTION_SESSION.generated.json`
5. `RUN_RECORD_001.generated.json`
6. `RERUN_DECISION_RECORD.generated.json`
7. `SAMPLE_TASK_FORMATION_RECORD_V0_1.json`
8. `SAMPLE_TASK_KERNEL_OBJECT_V0_1.json`

Missing inputs are downgraded to explicit warning markers:
- `MISSING_INPUT_WARN`
- `FOUNDATION_ONLY`
- `READ_ONLY_LAB`

## Output Surfaces
Outputs created in this task:
1. State schema and sample contract (`CONTRACTS/VISUAL_BRAIN/`)
2. Builder and validator scripts (`TOOLS/VISUAL_BRAIN/` and `TOOLS/VALIDATORS/`)
3. Generated visual state JSON:
   - `VISUAL_BRAIN/TASK_CORRIDOR_V0_1/data/visual_brain_task_corridor_state.generated.json`
4. Static lab shell:
   - `index.html`, `styles.css`, `visual_brain_task_corridor.js`

## Visual Corridor Structure
The corridor surface renders:
1. Owner Intent Node
2. Astronomicon Formation
3. 8 Organ Consultation Ring
4. Servitor Execution Core
5. Run/Rerun Rail
6. Evidence Constellation
7. Owner Verdict Gate

## Truth-Binding Rules
1. Any visually green/proved state requires an `evidence_ref`.
2. Missing evidence must remain warning/partial.
3. Foundation-only markers are always visible in UI badges.
4. No state mutation is sent to backend in V0.1.
5. UI interactions are local-only (panel toggle, view mode, reduced motion).

## No-Fake-Green Boundary
Allowed claims:
1. Static rendering of receipt-backed corridor state.
2. Deterministic generation from bounded NewGen records.
3. Honest warning presentation for missing or foundation-only inputs.

Forbidden claims:
1. Production orchestration readiness.
2. Live autonomous organ dialogue.
3. Full production Visual Brain readiness.
4. Real backend execution control.

## State Semantics
Expected status vocabulary includes:
- `READ_ONLY_LAB`
- `FOUNDATION_ONLY`
- `PROVED_BY_RECEIPT`
- `PARTIAL`
- `MISSING_INPUT_WARN`
- `BLOCKED`
- `STUB`

## Bilingual UI Compatibility
This static lab keeps machine artifacts English and can be extended to RU/EN labels.
Owner-facing reports remain Russian as required by Officio response contract.

## Next Hook
Safe next consumer:
- `TASK-20260521-NEWGEN-SKILL-GROWTH-SYSTEM-PC-V0_1`

This follow-up can reuse:
1. visual corridor state schema,
2. generated state envelope,
3. evidence panel conventions,
4. validator guardrails.
