# LLM_FORCE_FOCUS_MATRIX

Status: `CANDIDATE_NOT_CANON`
Owner organ: `Officio Agentis`
Support organs: Astronomicon, Mechanicus, Inquisition, Administratum

## Purpose

Defines how IMPERIUM focuses a large LLM through role, route, settings, output contract, tool boundary and red-team closure instead of relying on one giant prompt.

## Required questions

- Which role/mode should the LLM enter?
- Which organ owns the current task?
- What is the compact task focus packet?
- Which settings, formats and forbidden behaviors apply?
- What can be solved script-first and what remains agent-only?
- What red-team checks must downgrade the answer?

## PASS criteria

- Task Focus Packet is built before work
- Role/format/language are read from Officio
- Task route is read from Astronomicon
- Capability/tool boundary is read from Mechanicus
- Fake-green caps are read from Inquisition

## WARN criteria

- One authority source missing but declared as AUTHORITY_GAP
- Manual reasoning used but tagged as AGENT_REASONING_ONLY
- Owner questions remain but cap is explicit

## BLOCK criteria

- LLM starts implementation without focus packet
- Taskpack invents role instead of reading Officio
- Agent claims system capability without script-first evidence
- Final answer lacks red-team downgrade opportunity

## Fake-green flags

- `PROMPT_AS_AUTHORITY`
- `ROLE_INVENTED_BY_AGENT`
- `MANUAL_REASONING_AS_SYSTEM_CAPABILITY`
- `NO_RED_TEAM_MODE`

## Evidence requirements

- `ROLE_ENTRY_ACK`
- `TASK_FOCUS_PACKET`
- `CAPABILITY_SPLIT_RECEIPT`
- `RED_TEAM_VERDICT`
