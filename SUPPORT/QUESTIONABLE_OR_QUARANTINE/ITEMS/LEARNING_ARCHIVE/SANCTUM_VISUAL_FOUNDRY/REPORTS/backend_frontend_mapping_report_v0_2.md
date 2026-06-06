# Backend Frontend Mapping Report V0.2

Task: `TASK-20260520-NEWGEN-VISUAL-TOPOLOGY-HARDEN-10-ORGAN-COVERAGE-VM3-V0_2R`
Source map: `REGISTRY/backend_frontend_truth_map.json`

## Mapping summary
| Visual unit | Status | Backend status | Truth owner | Data owner | Key risk |
|---|---|---|---|---|---|
| `SANCTUM.SHELL.GLOBAL_FRAME` | `real` | `real` | `OFFICIO_AGENTIS_AGENT` | `SANCTUM_STATE_BUILDER` | Decorative frame can look healthy while backend is disconnected. |
| `SANCTUM.BRAIN_FIELD.NEURAL_CORE` | `candidate` | `candidate` | `UNKNOWN` | `SANCTUM_STATE_BUILDER` | Core pulse can be mistaken as health confirmation. |
| `SANCTUM.BRAIN_FIELD.ORGAN_RING` | `candidate` | `candidate` | `OFFICIO_AGENTIS_AGENT` | `SANCTUM_STATE_BUILDER` | Unimplemented organs can look active without explicit stub labels. |
| `SANCTUM.BRAIN_FIELD.ORGAN_RING.ADMINISTRATUM_NODE` | `stub` | `unknown` | `ADMINISTRATUM_AGENT` | `UNKNOWN` | Stub node shown as real organ cockpit. |
| `SANCTUM.BRAIN_FIELD.ORGAN_RING.ASTRONOMICON_NODE` | `stub` | `unknown` | `ASTRONOMICON_AGENT` | `UNKNOWN` | Stub node shown as real organ cockpit. |
| `SANCTUM.BRAIN_FIELD.ORGAN_RING.MECHANICUS_NODE` | `real` | `real` | `MECHANICUS_AGENT` | `SANCTUM_STATE_BUILDER` | Connected style while state source missing. |
| `SANCTUM.BRAIN_FIELD.ORGAN_RING.OFFICIO_NODE` | `stub` | `unknown` | `OFFICIO_AGENTIS_AGENT` | `UNKNOWN` | Stub node shown as real organ cockpit. |
| `SANCTUM.BRAIN_FIELD.ORGAN_RING.INQUISITION_NODE` | `stub` | `unknown` | `INQUISITION_AGENT` | `UNKNOWN` | Stub node shown as real organ cockpit. |
| `SANCTUM.BRAIN_FIELD.ORGAN_RING.DOCTRINARIUM_NODE` | `stub` | `unknown` | `DOCTRINARIUM_AGENT` | `UNKNOWN` | Stub node shown as real organ cockpit. |
| `SANCTUM.BRAIN_FIELD.ORGAN_RING.STRATEGIUM_NODE` | `stub` | `unknown` | `STRATEGIUM_AGENT` | `UNKNOWN` | Stub node shown as real organ cockpit. |
| `SANCTUM.BRAIN_FIELD.ORGAN_RING.SCHOLA_NODE` | `stub` | `unknown` | `SCHOLA_IMPERIALIS_AGENT` | `UNKNOWN` | Stub node shown as real organ cockpit. |
| `SANCTUM.BRAIN_FIELD.ORGAN_RING.CUSTODES_NODE_LOCKED` | `locked` | `locked` | `CUSTODES_AGENT` | `OWNER_GATE_REQUIRED` | Locked lane represented as implementable-ready without owner gate. |
| `SANCTUM.BRAIN_FIELD.ORGAN_RING.THRONE_NODE_LOCKED` | `locked` | `locked` | `THRONE_AGENT` | `OWNER_GATE_REQUIRED` | Locked lane represented as implementable-ready without owner gate. |
| `SANCTUM.BRAIN_FIELD.NEURAL_LINKS` | `candidate` | `candidate` | `ASTRONOMICON_AGENT` | `SANCTUM_STATE_BUILDER` | Animated links imply live data flow without evidence. |
| `SANCTUM.BRAIN_FIELD.ACTIVITY_PULSE_LAYER` | `candidate` | `candidate` | `INQUISITION_AGENT` | `SANCTUM_STATE_BUILDER` | Activity pulse can imply healthy execution while backend stalled. |
| `SANCTUM.RIGHT_CONTEXT_DOCK` | `real` | `real` | `OFFICIO_AGENTIS_AGENT` | `SANCTUM_STATE_BUILDER` | Dock cards can appear ready while child panels are stub. |
| `SANCTUM.RIGHT_CONTEXT_DOCK.MECHANICUS_PANEL` | `candidate` | `candidate` | `MECHANICUS_AGENT` | `SANCTUM_STATE_BUILDER` | UI action lane visible while backend execution blocked. |
| `SANCTUM.RIGHT_CONTEXT_DOCK.ADMINISTRATUM_PANEL_STUB` | `stub` | `unknown` | `ADMINISTRATUM_AGENT` | `UNKNOWN` | Stub panel represented as real cockpit lane. |
| `SANCTUM.RIGHT_CONTEXT_DOCK.ASTRONOMICON_PANEL_STUB` | `stub` | `unknown` | `ASTRONOMICON_AGENT` | `UNKNOWN` | Stub panel represented as real cockpit lane. |
| `SANCTUM.RIGHT_CONTEXT_DOCK.OFFICIO_PANEL_STUB` | `stub` | `unknown` | `OFFICIO_AGENTIS_AGENT` | `UNKNOWN` | Stub panel represented as real cockpit lane. |
| `SANCTUM.RIGHT_CONTEXT_DOCK.INQUISITION_PANEL_STUB` | `stub` | `unknown` | `INQUISITION_AGENT` | `UNKNOWN` | Stub panel represented as real cockpit lane. |
| `SANCTUM.RIGHT_CONTEXT_DOCK.DOCTRINARIUM_PANEL_STUB` | `stub` | `unknown` | `DOCTRINARIUM_AGENT` | `UNKNOWN` | Stub panel represented as real cockpit lane. |
| `SANCTUM.RIGHT_CONTEXT_DOCK.STRATEGIUM_PANEL_STUB` | `stub` | `unknown` | `STRATEGIUM_AGENT` | `UNKNOWN` | Stub panel represented as real cockpit lane. |
| `SANCTUM.RIGHT_CONTEXT_DOCK.SCHOLA_PANEL_STUB` | `stub` | `unknown` | `SCHOLA_IMPERIALIS_AGENT` | `UNKNOWN` | Stub panel represented as real cockpit lane. |
| `SANCTUM.RIGHT_CONTEXT_DOCK.CUSTODES_PANEL_LOCKED` | `locked` | `locked` | `CUSTODES_AGENT` | `OWNER_GATE_REQUIRED` | Locked panel displayed as operable cockpit. |
| `SANCTUM.RIGHT_CONTEXT_DOCK.THRONE_PANEL_LOCKED` | `locked` | `locked` | `THRONE_AGENT` | `OWNER_GATE_REQUIRED` | Locked panel displayed as operable cockpit. |
| `SANCTUM.TRUTH_STATUS_STRIP` | `candidate` | `candidate` | `INQUISITION_AGENT` | `SANCTUM_STATE_BUILDER` | Cached PASS chip after backend failure. |
| `SANCTUM.COMMAND_SURFACE` | `candidate` | `candidate` | `OFFICIO_AGENTIS_AGENT` | `SANCTUM_STATE_BUILDER` | Command appears executable despite backend block. |
| `SANCTUM.EVIDENCE_REPORT_LAYER` | `candidate` | `candidate` | `ADMINISTRATUM_AGENT` | `SANCTUM_STATE_BUILDER` | Null evidence path displayed as valid report. |

## Anti-fake-green constraints
- Stub and locked units are explicitly non-real.
- Candidate/real units require backend sources and proof requirements.
- UNKNOWN backend sources include explicit reasons in passports/truth map.
