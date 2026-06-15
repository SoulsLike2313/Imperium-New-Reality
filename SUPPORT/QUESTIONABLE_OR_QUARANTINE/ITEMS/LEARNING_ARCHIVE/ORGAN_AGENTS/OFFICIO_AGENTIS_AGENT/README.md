# OFFICIO_AGENTIS_AGENT Foundation V0.1

Officio Agentis is the IMPERIUM organ of agent role/settings/focus control.
It does not execute business tasks directly. It defines how other agents must execute.

## Scope

- Repository scope: `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/OFFICIO_AGENTIS_AGENT/**`
- Runtime/output root (default): `E:\IMPERIUM_CONTEXT\LOCAL\OFFICIO_AGENTIS\RUNS`
- Response bundles: `E:\IMPERIUM_CONTEXT\LOCAL\OFFICIO_AGENTIS\OUTBOX\...`

## V0.1 Capability

- Base Half contracts for execution discipline.
- Identity Half contracts for organ mission and limits.
- Role registry for `SERVITOR`, `LOGOS_PRIME`, and `LOGOS_SPECULUM`.
- Mode registry for `EXECUTOR`, `AUDITOR`, `ARCHITECT`, and `REPAIRER`.
- Settings registries for permissions, forbidden actions, stop conditions, evidence, and response formats.
- Evidence policy and response contracts.
- CLI runner `TOOLS/officio_agent_runner.py` with status/role/settings/pack/matrix/compliance commands.

## Core Law

- No evidence = no DONE.
- No ACK = no work.
- No fake green.

## Basic Runner Usage

```powershell
py -3 IMPERIUM_NEW_GENERATION\ORGAN_AGENTS\OFFICIO_AGENTIS_AGENT\TOOLS\officio_agent_runner.py status
py -3 IMPERIUM_NEW_GENERATION\ORGAN_AGENTS\OFFICIO_AGENTIS_AGENT\TOOLS\officio_agent_runner.py role-get --agent SERVITOR
py -3 IMPERIUM_NEW_GENERATION\ORGAN_AGENTS\OFFICIO_AGENTIS_AGENT\TOOLS\officio_agent_runner.py settings-get --agent SERVITOR --mode EXECUTOR
py -3 IMPERIUM_NEW_GENERATION\ORGAN_AGENTS\OFFICIO_AGENTIS_AGENT\TOOLS\officio_agent_runner.py pack-build-role --agent SERVITOR
py -3 IMPERIUM_NEW_GENERATION\ORGAN_AGENTS\OFFICIO_AGENTIS_AGENT\TOOLS\officio_agent_runner.py check-all
```

