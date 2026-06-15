# Visual Topology Report

Task: `TASK-20260520-NEWGEN-SANCTUM-VISUAL-TOPOLOGY-ADDRESS-REGISTRY-PC-V0_1`

## Topology root

- Registry file: `REGISTRY/visual_address_registry.json`
- Root id: `VISUAL_SYSTEM.SANCTUM_SHELL`

## Address hierarchy

```text
VISUAL_SYSTEM.SANCTUM_SHELL
├── SANCTUM.SHELL.GLOBAL_FRAME
├── SANCTUM.BRAIN_FIELD
│   ├── SANCTUM.BRAIN_FIELD.NEURAL_CORE
│   ├── SANCTUM.BRAIN_FIELD.ORGAN_RING
│   │   └── SANCTUM.BRAIN_FIELD.ORGAN_RING.MECHANICUS_NODE
│   ├── SANCTUM.BRAIN_FIELD.NEURAL_LINKS
│   └── SANCTUM.BRAIN_FIELD.ACTIVITY_PULSE_LAYER
├── SANCTUM.RIGHT_CONTEXT_DOCK
│   ├── SANCTUM.RIGHT_CONTEXT_DOCK.MECHANICUS_PANEL
│   └── SANCTUM.RIGHT_CONTEXT_DOCK.ADMINISTRATUM_PANEL_STUB
└── SANCTUM.CONTROL_SURFACES
    ├── SANCTUM.TRUTH_STATUS_STRIP
    ├── SANCTUM.COMMAND_SURFACE
    └── SANCTUM.EVIDENCE_REPORT_LAYER
```

## Address laws

1. DOT naming required: `SANCTUM.<GROUP>.<UNIT>[.<SUBUNIT>]`.
2. Each address maps to one passport file in `VISUAL_UNITS/`.
3. Unit must declare explicit `integration_status` (`real/stub/locked/...`).
4. Unit must include backend source and proof requirements.
5. Performance tier must exist in `MOTION/motion_budget_v0_1.json`.

## Status model

- `real`: active mapping with declared backend/source proof.
- `stub`: reserved lane with explicit non-readiness.
- `locked`: owner-gated lane; no fake activation allowed.

## Performance model outcome

- Tiers used: `STATIC`, `CHEAP`, `MEDIUM`, `EXPENSIVE`, `DISABLED_LOW_POWER`.
- Enforced hero rule: exactly one `EXPENSIVE` unit (`SANCTUM.BRAIN_FIELD.NEURAL_CORE`).
- Truth/evidence surfaces are constrained to `STATIC`.

## Why this solves current failure mode

- Moves work from generic card styling to explicit unit contracts.
- Separates decorative identity (token/texture/motion) from truth source rules.
- Makes per-unit iteration isolated and auditable.
- Prevents fake-green by requiring source+proof on each key visual layer.
