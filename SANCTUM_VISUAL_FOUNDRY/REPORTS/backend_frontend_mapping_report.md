# Backend Frontend Mapping Report

Source map: `REGISTRY/backend_frontend_truth_map.json`

## Mapping purpose

This report binds important frontend visual units to concrete backend/frontend truth sources, owner responsibility, and anti-fake-green proof rules.

## Core mapping summary

| Visual unit | Owner | Source type | Main source paths | Status | Key fake-green risk |
|---|---|---|---|---|---|
| `SANCTUM.BRAIN_FIELD.ORGAN_RING.MECHANICUS_NODE` | `MECHANICUS_AGENT` | api_state_and_agent_status | `state_builder.py`, `mechanicus_adapter.py`, `MECHANICUS_AGENT/state/current_status.json` | real | node looks connected while state file missing |
| `SANCTUM.RIGHT_CONTEXT_DOCK.MECHANICUS_PANEL` | `MECHANICUS_AGENT` | api_actions_and_state | `actions.py`, `state_builder.py`, `TOOL_INDEX.json` | real | UI allows command while backend blocks |
| `SANCTUM.TRUTH_STATUS_STRIP` | `INQUISITION_AGENT` | api_state | `state_builder.py`, `app.js` | real | cached PASS chips after source failure |
| `SANCTUM.COMMAND_SURFACE` | `OFFICIO_AGENTIS_AGENT` | api_actions | `actions.py`, `app.js` | real | unallowlisted command shown as runnable |
| `SANCTUM.EVIDENCE_REPORT_LAYER` | `ADMINISTRATUM_AGENT` | artifact_paths | `state_builder.py`, `mechanicus_adapter.py`, `screenshot_index.json` | real | null evidence path shown as healthy |
| `SANCTUM.RIGHT_CONTEXT_DOCK.ADMINISTRATUM_PANEL_STUB` | `ADMINISTRATUM_AGENT` | stub | `app.js` (placeholder branch) | stub | stub shown as production cockpit |

## Real/stub/locked policy in this task

- Real mapping is assigned only where source paths and current behavior exist.
- Stub mapping remains explicit for unimplemented lanes.
- Locked lanes are modeled in organ profiles (`CUSTODES_AGENT`, `THRONE_AGENT`) and are not promoted to active unit panels.

## Unknowns and warnings

- Some non-Mechanicus organ cockpit panels are intentionally not implemented in this slice.
- This skeleton maps backend truth and ownership; it does not claim final visual readiness.

## Scope purity

- No write targets in forbidden roots were introduced.
- All mapping artifacts are inside `IMPERIUM_NEW_GENERATION/SANCTUM_VISUAL_FOUNDRY`.
