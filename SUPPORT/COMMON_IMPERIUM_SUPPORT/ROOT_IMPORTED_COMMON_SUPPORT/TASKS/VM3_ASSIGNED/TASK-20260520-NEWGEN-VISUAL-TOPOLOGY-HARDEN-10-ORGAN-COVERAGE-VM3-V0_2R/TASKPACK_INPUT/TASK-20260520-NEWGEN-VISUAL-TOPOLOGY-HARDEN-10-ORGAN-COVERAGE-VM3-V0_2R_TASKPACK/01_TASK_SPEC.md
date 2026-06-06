# Task specification

## Task ID

`TASK-20260520-NEWGEN-VISUAL-TOPOLOGY-HARDEN-10-ORGAN-COVERAGE-VM3-V0_2R`

## Objective

Harden the existing Visual Topology V0.1 skeleton into V0.2 by adding full 10-organ coverage, full right-context panel coverage, repaired ownership semantics, stronger backend/frontend truth mapping, and validator V0.2.

## Mandatory precondition

Before implementation, complete `09_OFFICIO_AUTHORITY_INTAKE_GATE.md`.

## Required work

### 1. Full 10-organ visual unit coverage

Create/update visual unit passports:

- `SANCTUM.BRAIN_FIELD.ORGAN_RING.ADMINISTRATUM_NODE`
- `SANCTUM.BRAIN_FIELD.ORGAN_RING.ASTRONOMICON_NODE`
- `SANCTUM.BRAIN_FIELD.ORGAN_RING.MECHANICUS_NODE`
- `SANCTUM.BRAIN_FIELD.ORGAN_RING.OFFICIO_NODE`
- `SANCTUM.BRAIN_FIELD.ORGAN_RING.INQUISITION_NODE`
- `SANCTUM.BRAIN_FIELD.ORGAN_RING.DOCTRINARIUM_NODE`
- `SANCTUM.BRAIN_FIELD.ORGAN_RING.STRATEGIUM_NODE`
- `SANCTUM.BRAIN_FIELD.ORGAN_RING.SCHOLA_NODE`
- `SANCTUM.BRAIN_FIELD.ORGAN_RING.CUSTODES_NODE_LOCKED`
- `SANCTUM.BRAIN_FIELD.ORGAN_RING.THRONE_NODE_LOCKED`

Every passport must include:
- `visual_unit_id`
- `parent`
- `type`
- `visual_owner`
- `truth_owner`
- `data_source_owner`
- `organ_subject`
- `implementation_owner`
- `backend_source`
- `backend_source_status`
- `backend_source_unknown_reason` when unknown
- `allowed_states`
- `truth_rules`
- `visual_tokens`
- `texture`
- `glow`
- `motion`
- `perf_tier`
- `proof_requirements`
- `integration_status`
- `fake_green_risks`

### 2. Full right-context panel coverage

Create/update:

- `SANCTUM.RIGHT_CONTEXT_DOCK.MECHANICUS_PANEL`
- `SANCTUM.RIGHT_CONTEXT_DOCK.ADMINISTRATUM_PANEL_STUB`
- `SANCTUM.RIGHT_CONTEXT_DOCK.ASTRONOMICON_PANEL_STUB`
- `SANCTUM.RIGHT_CONTEXT_DOCK.OFFICIO_PANEL_STUB`
- `SANCTUM.RIGHT_CONTEXT_DOCK.INQUISITION_PANEL_STUB`
- `SANCTUM.RIGHT_CONTEXT_DOCK.DOCTRINARIUM_PANEL_STUB`
- `SANCTUM.RIGHT_CONTEXT_DOCK.STRATEGIUM_PANEL_STUB`
- `SANCTUM.RIGHT_CONTEXT_DOCK.SCHOLA_PANEL_STUB`
- `SANCTUM.RIGHT_CONTEXT_DOCK.CUSTODES_PANEL_LOCKED`
- `SANCTUM.RIGHT_CONTEXT_DOCK.THRONE_PANEL_LOCKED`

Custodes and Throne must remain locked. Stub panels must be marked stub. Do not invent readiness.

### 3. Ownership model repair

Normalize these fields:
- `visual_owner`
- `truth_owner`
- `data_source_owner`
- `organ_subject`
- `implementation_owner`

Important: `SANCTUM.BRAIN_FIELD.NEURAL_CORE` must not be owned by Mechanicus.

### 4. Registry update

Update:

`IMPERIUM_NEW_GENERATION/SANCTUM_VISUAL_FOUNDRY/REGISTRY/visual_address_registry.json`

It must include all required visual units and parent/child relationships.

### 5. Backend/frontend truth map V0.2

Update:

`IMPERIUM_NEW_GENERATION/SANCTUM_VISUAL_FOUNDRY/REGISTRY/backend_frontend_truth_map.json`

Every important unit must map to:
- backend source or UNKNOWN;
- status: real/candidate/stub/locked/unknown;
- ownership fields;
- fake-green risks;
- proof requirements.

### 6. Validator V0.2

Update/create:

`IMPERIUM_NEW_GENERATION/SANCTUM_VISUAL_FOUNDRY/VALIDATORS/validate_visual_topology.py`

It must check:
- Officio ACK or missing-authority report exists;
- all 10 organ node units exist;
- all 10 right panel units exist;
- Custodes/Throne node and panel units are not marked real;
- stub organs are marked stub;
- required ownership fields exist;
- every real/candidate unit has backend source or explicit UNKNOWN reason;
- registry references existing visual unit files;
- backend/frontend truth map references existing units;
- required performance tiers exist;
- no forbidden roots are used as write targets;
- final report HEAD is not stale if report includes HEAD;
- validator writes a JSON report.

### 7. Reports

Create/update:

- `REPORTS/visual_topology_v0_2_hardening_report.md`
- `REPORTS/visual_unit_inventory_v0_2.md`
- `REPORTS/backend_frontend_mapping_report_v0_2.md`
- `REPORTS/validator_v0_2_report.json`
- `REPORTS/OWNER_REPORT_RU.md`
- `RECEIPTS/FINAL_RECEIPT_V0_2.json`

### 8. Task artifacts

Store task artifacts inside:

`IMPERIUM_NEW_GENERATION/TASKS/VM3_ASSIGNED/TASK-20260520-NEWGEN-VISUAL-TOPOLOGY-HARDEN-10-ORGAN-COVERAGE-VM3-V0_2R/`

Recommended:
- `START_ACK.md`
- `WORK_LOG.md`
- `GIT_STATUS_BEFORE.txt`
- `GIT_STATUS_AFTER.txt`
- `VALIDATION_COMMANDS.txt`
- Officio ACK/WARN JSON

### 9. Commit and push

If gates pass:
- commit all legitimate changes;
- push to GitHub;
- report commit hash and clean/dirty status.

Commit message:

`TASK-20260520: harden New Generation visual topology coverage`
