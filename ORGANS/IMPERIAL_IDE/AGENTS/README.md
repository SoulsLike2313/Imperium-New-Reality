# Imperial IDE Agents and Servitors

This directory defines the visible agent roster used by the Operational Station.

- `agent_registry.json` is the canonical role and boundary registry.
- `servitor_roster.json` is the compact operator-facing roster.
- `agent_runtime_state.json` is a checked-in truthful baseline, not a claim of autonomous execution.
- `agent_card.schema.json` and `agent_status.schema.json` define validation contracts.

`ACTIVE` means the bounded local adapter is available. `DRY_RUN` means it can inspect or prepare artifacts without performing the governed action. `BLOCKED` means a required authority or execution backend is intentionally absent.

Real LLM execution, arbitrary shell execution, remote dispatch, and remote registration remain disabled. Prime is represented as an external handoff authority, not an embedded autonomous agent.
