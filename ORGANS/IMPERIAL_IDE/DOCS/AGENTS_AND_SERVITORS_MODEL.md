# Agents and Servitors Model

`AGENTS/agent_registry.json` defines twelve visible operational roles: Prime, Astronomicon, Mechanicus, Administratum, Inquisition, Strategium, Doctrinarium, Officio Agentis, Schola Imperialis, WARP, MetaOS, and Imperial IDE.

An `ACTIVE` status means a bounded local adapter is available. It does not imply autonomous model execution. `DRY_RUN` permits inspection, preparation, or route preview. `BLOCKED` identifies missing authority or backend explicitly.

Servitor Prime is an external handoff target with `EXTERNAL_HANDOFF_ONLY`. Real LLM calls, autonomous spawning, arbitrary shell, remote dispatch, and remote registration remain blocked. Every card declares capabilities, allowed actions, blocked actions, risk class, execution mode, and handoff mode.
