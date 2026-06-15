# Visual Unit Inventory

| Visual address | Type | Owner organ | Backend source | States | Perf tier | Token set | Status |
|---|---|---|---|---|---|---|---|
| `SANCTUM.SHELL.GLOBAL_FRAME` | shell_frame | `OFFICIO_AGENTIS_AGENT` | `SANCTUM_MINI/static/index.html` + `styles.css` | idle/active/warn/error/unknown | CHEAP | `sanctum_shell_tokens` | real |
| `SANCTUM.BRAIN_FIELD.NEURAL_CORE` | hero_core | `MECHANICUS_AGENT` | `SANCTUM_MINI/static/app.js` | idle/active/warn/error/unknown | EXPENSIVE | `brain_core_tokens` | real |
| `SANCTUM.BRAIN_FIELD.ORGAN_RING` | organ_ring | `OFFICIO_AGENTIS_AGENT` | `SANCTUM_MINI/static/app.js` | real/placeholder/locked/unknown | CHEAP | `organ_ring_tokens` | real |
| `SANCTUM.BRAIN_FIELD.ORGAN_RING.MECHANICUS_NODE` | organ_node | `MECHANICUS_AGENT` | `state_builder.py` + `mechanicus_adapter.py` + `MECHANICUS_AGENT/state/current_status.json` | connected/warn/error/blocked/unknown | CHEAP | `mechanicus_node_tokens` | real |
| `SANCTUM.BRAIN_FIELD.NEURAL_LINKS` | connector_layer | `ASTRONOMICON_AGENT` | `SANCTUM_MINI/static/app.js` (`BRAIN_LINKS`) | static/highlighted/disabled_low_power | CHEAP | `neural_link_tokens` | real |
| `SANCTUM.BRAIN_FIELD.ACTIVITY_PULSE_LAYER` | activity_overlay | `INQUISITION_AGENT` | `event_stream.py` + `SANCTUM_MINI/static/app.js` | idle/event_pulse/fallback/disabled_low_power | MEDIUM | `activity_pulse_tokens` | real |
| `SANCTUM.RIGHT_CONTEXT_DOCK` | context_dock | `OFFICIO_AGENTIS_AGENT` | `SANCTUM_MINI/static/index.html` + `styles.css` | collapsed/expanded/focus/unknown | CHEAP | `right_dock_tokens` | real |
| `SANCTUM.RIGHT_CONTEXT_DOCK.MECHANICUS_PANEL` | organ_panel | `MECHANICUS_AGENT` | `actions.py` + `state_builder.py` + `TOOL_INDEX.json` | idle/active/blocked/error/unknown | CHEAP | `mechanicus_panel_tokens` | real |
| `SANCTUM.RIGHT_CONTEXT_DOCK.ADMINISTRATUM_PANEL_STUB` | organ_panel_stub | `ADMINISTRATUM_AGENT` | `SANCTUM_MINI/static/app.js` (stub lane) | stub/hidden/unknown | STATIC | `stub_panel_tokens` | stub |
| `SANCTUM.TRUTH_STATUS_STRIP` | truth_strip | `INQUISITION_AGENT` | `state_builder.py` + `SANCTUM_MINI/static/app.js` | pass/warn/error/unknown | STATIC | `truth_strip_tokens` | real |
| `SANCTUM.COMMAND_SURFACE` | command_surface | `OFFICIO_AGENTIS_AGENT` | `actions.py` + `SANCTUM_MINI/static/app.js` | ready/pending/blocked/error | CHEAP | `command_surface_tokens` | real |
| `SANCTUM.EVIDENCE_REPORT_LAYER` | evidence_layer | `ADMINISTRATUM_AGENT` | `mechanicus_adapter.py` + `state_builder.py` + `SCREENSHOTS/screenshot_index.json` | available/missing/stale/unknown | STATIC | `evidence_layer_tokens` | real |

## Organ profile status map

- Real profiles: `SANCTUM_SHELL`, `MECHANICUS_AGENT`
- Stub profiles: `ADMINISTRATUM_AGENT`, `ASTRONOMICON_AGENT`, `OFFICIO_AGENTIS_AGENT`, `INQUISITION_AGENT`, `DOCTRINARIUM_AGENT`, `STRATEGIUM_AGENT`, `SCHOLA_IMPERIALIS_AGENT`
- Locked profiles: `CUSTODES_AGENT`, `THRONE_AGENT`
