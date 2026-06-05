# Post Work Bundle Contract V0.2

Status: `CANDIDATE_V0_2`
Owner organ: `ADMINISTRATUM`

## Purpose

V0.2 turns the V0.1 post-work bundle prototype into an enforced closure path. The bundle is accepted only when required indexes, receipts, organ ring rows, remote proof fields, and heavy artifact policy pass schema-backed checks.

## Required Enforcements

- Validate bundle manifest, bundle index card, receipt index, file delta index, and organ ring receipt against repository schemas.
- Require all nine post-work organs.
- Block final acceptance when any required organ receipt reports `BLOCK`.
- Require Officio, Inquisition, Custodes, Schola, and Mechanicus receipts.
- Require remote proof fields while preserving the self-reference boundary before commit.
- Emit a repair request when a blocking defect is found.
- Prove the repair loop with fixtures that block and then pass after repair.

## Authority Boundary

Administratum V0.2 may claim `POST_WORK_BUNDLE_SCHEMA_PASS` or `POST_WORK_BUNDLE_SCHEMA_BLOCK`. It may not claim semantic truth, full Custodes authority, Inquisition purity, Throne readiness, or WARP runtime readiness.
