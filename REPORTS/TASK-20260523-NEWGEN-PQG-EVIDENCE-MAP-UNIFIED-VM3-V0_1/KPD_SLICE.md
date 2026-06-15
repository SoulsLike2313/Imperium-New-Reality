# KPD Slice

## Useful outputs
- Added unified evidence map, freshness index, normalization table, and not-proven register with schemas.
- Added reusable builder and validator for unified evidence foundation.
- Added minimal Sanctum NG read-only truth visibility for unified evidence/freshness references.

## Waste / friction
- Legacy validator compatibility required extra bridge receipts.
- Existing Sanctum refresh runner is coupled to an older action-layer report contract.

## Tool preservation
- `IMPERIUM_NEW_GENERATION/TRUTH/TOOLS/evidence_map_unified_builder.py` -> `ABSORB_NOW` (foundation reusable tool).
- `IMPERIUM_NEW_GENERATION/TRUTH/TOOLS/evidence_map_unified_validator.py` -> `ABSORB_NOW` (foundation reusable validator).

## Narrower future agent profile
- `NEWGEN_TRUTH_EVIDENCE_INDEX_SERVITOR` for truth-only map/freshness/index maintenance.

## Automation next
- Add a contract-aware unified validator mode that can validate both legacy and new report bundles without compatibility bridge files.
