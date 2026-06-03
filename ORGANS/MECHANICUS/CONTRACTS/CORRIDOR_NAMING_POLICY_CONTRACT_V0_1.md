# Corridor Naming Policy Contract V0.1

Owner organ: `Mechanicus`
Support organs: `Inquisition`, `Officio Agentis`, `Administratum`
Status: `CANDIDATE_RUNTIME_READY`

## Allowed corridor terms
- `synthetic_corridor`: replay/training proof only.
- `real_runtime_corridor`: real taskpack execution path with end-to-end receipts.
- `warp_corridor`: future path, locked unless Owner unlock is explicit.

## Forbidden owner-facing phrase
- Untyped phrase `runtime corridor` without one of the allowed typed terms.

## Mandatory caps
- `CAP_UNTYPED_RUNTIME_CLAIM`
- `CAP_SYNTHETIC_CLAIMED_AS_REAL`
- `CAP_WARP_CLAIMED_WITHOUT_UNLOCK`

## Enforcement
- Negative fixtures in `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/FIXTURES/negative_fixture_manifest.json`.
- Validator: `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/validate_matrix_spine.py`.
