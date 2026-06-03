# Corridor Naming Policy Report

Task: `TASK-NEWGEN-MATRIX-SPINE-CLOSURE-PROVENANCE-CORRIDOR-NAMING-AND-REVIEW-PIPELINE-HARDENING-VM3-V0_1`

## Policy
- Allowed typed terms: `synthetic_corridor`, `real_runtime_corridor`, `warp_corridor`.
- Untyped owner-facing phrase `runtime corridor` is forbidden.

## Enforcement Evidence
- `CAP_UNTYPED_RUNTIME_CLAIM` detected by negative fixture: yes
- `CAP_SYNTHETIC_CLAIMED_AS_REAL` detected by negative fixture: yes
- `CAP_WARP_CLAIMED_WITHOUT_UNLOCK` detected by negative fixture: yes
- `CAP_NO_FINAL_CLOSURE_VERIFIER` detected by negative fixture: yes
- `CAP_NO_NEXT_PIPELINE_HANDOFF` detected by negative fixture: yes
- `CAP_RUNTIME_OUTPUT_UNCLASSIFIED` detected by negative fixture: yes

## Replay
- `bash IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.sh`
