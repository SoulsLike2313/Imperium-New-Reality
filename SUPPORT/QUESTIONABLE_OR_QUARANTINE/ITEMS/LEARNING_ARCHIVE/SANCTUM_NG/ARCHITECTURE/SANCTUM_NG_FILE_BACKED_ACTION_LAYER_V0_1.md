# SANCTUM NG FILE-BACKED ACTION LAYER V0.1

## Purpose
Provide a bounded, local-only action foundation for Sanctum NG so the UI can run safe allowlisted operations without pretending production autonomy.

## Scope
This layer is foundation-only and local:
- localhost HTTP server only
- file-backed request/result records
- explicit allowlist action execution
- no arbitrary shell
- no arbitrary file read/write
- no external network calls

## Core Components
1. Action registry
- `IMPERIUM_NEW_GENERATION/SANCTUM_NG/REGISTRY/SANCTUM_NG_ACTION_REGISTRY_V0_1.json`
- single source of truth for action metadata, safety boundaries, and execution status (`WIRED`, `PREVIEW_ONLY`, `NOT_WIRED`, `BLOCKED`)

2. Contracts
- `sanctum_ng_action_request.schema.json`
- `sanctum_ng_action_result.schema.json`
- `sanctum_ng_action_registry.schema.json`

3. Local action server
- `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TOOLS/sanctum_ng_action_server.py`
- routes:
  - `GET /api/state`
  - `GET /api/actions`
  - `POST /api/actions/<ACTION_ID>`
- serves Sanctum NG app from `SANCTUM_NG/APP`

4. Validation and smoke
- `sanctum_ng_action_layer_validator.py`
- `sanctum_ng_action_layer_smoke.py`

5. UI truth surface
- action panel with connection state
- run button gating by connection + `WIRED`
- explicit preview/not-connected limitations
- last action result evidence path

## Safety Model
Action execution is hard-bounded by:
- allowlisted action IDs only
- action-specific fixed command templates
- fixed repo-local known paths
- fixed report/action-log destinations
- explicit forbidden path set

Any action outside registry or outside `WIRED` status is rejected as non-executable.

## Action Lifecycle
1. UI requests action execution through `POST /api/actions/<ACTION_ID>`.
2. Server writes request record (JSON).
3. Server executes bounded allowlisted routine.
4. Server writes result record (JSON) with status and evidence refs.
5. UI renders result and keeps limitation visibility.

## Truth and Claim Discipline
- `CONNECTED` is shown only after successful server API handshake.
- `file://` mode always marks `ACTION_SERVER_NOT_CONNECTED`.
- No production/backend autonomy claim is emitted by this layer.

## Known Limitations
- Foundation layer only; not a production orchestration backend.
- No autonomous organ dialogue.
- No runtime hard-block over every shell surface; compliance remains receipt-driven.
