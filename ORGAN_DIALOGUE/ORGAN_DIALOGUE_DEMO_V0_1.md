# ORGAN DIALOGUE DEMO V0.1

## Purpose
Foundation-only, deterministic, file-backed demo proving the bounded flow:

`Servitor/Sanctum asks -> organ responds -> thread updates -> Sanctum reads the state.`

## Demo Task
- `TASK-DEMO-ORGAN-DIALOGUE-V0_1`
- Goal: prove packetized request/response storage and read-only visibility.

## Boundaries
- No live autonomous organ intelligence.
- No production execution claim.
- No runtime mutation outside allowlisted paths.
- Every response keeps `foundation_only: true`.

## Artifacts
- Schemas: `IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/SCHEMAS/`
- Registries: `IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/REGISTRY/`
- Thread packets: `IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/THREADS/TASK-DEMO-ORGAN-DIALOGUE-V0_1/`
- Builder/validator/smoke: `IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/TOOLS/`
- Sanctum read-only reference: `IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json`

## No-Fake-Green Note
PASS in this demo proves file-backed deterministic dialogue infrastructure only.
It does not prove autonomous organ reasoning, live backend, or production readiness.
