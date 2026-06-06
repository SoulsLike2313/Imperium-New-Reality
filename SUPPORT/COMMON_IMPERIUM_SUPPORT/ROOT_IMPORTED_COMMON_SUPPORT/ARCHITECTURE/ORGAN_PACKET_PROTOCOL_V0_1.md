# ORGAN PACKET PROTOCOL V0.1

## Task binding
- task_id: `TASK-20260521-NEWGEN-ORGAN-PACKET-CONTRACT-PC-V0_1`
- mode: bounded contract foundation
- non-goal: no live orchestration claim

## Protocol purpose
Organ Packet Protocol allows a Servitor to collect task-scoped advisory packets from 8 New Generation organs.
This artifact defines the format and control rules for packet exchange artifacts.

## In-scope organs
1. ASTRONOMICON
2. OFFICIO_AGENTIS
3. DOCTRINARIUM
4. ADMINISTRATUM
5. MECHANICUS
6. INQUISITION
7. STRATEGIUM
8. SCHOLA_IMPERIALIS

Out-of-scope for this version:
- THRONE
- CUSTODES

## Packet model
Each packet is task-bound and must include:
- identity fields (`schema_version`, `packet_id`, `task_id`, `organ_id`)
- control status (`packet_status`, `live_status`, `confidence`)
- task guidance vectors (`scope_advice`, `allowed_actions`, `forbidden_actions`, checks)
- collaboration questions (`questions_for_owner`, `questions_for_other_organs`)
- execution requirements (`skill_requirements`, `tool_requirements`, `stop_conditions`)
- proof object (`basis_paths`, `basis_commands`, `limitations`)

## Packet set model
A packet set is valid only when:
- all packets refer to one `task_id`;
- there are exactly 8 packets for the 8 in-scope organs;
- THRONE and CUSTODES are absent;
- no duplicated `organ_id`;
- packet status, live status, confidence values are from controlled enums;
- non-live claim is explicit.

## Required enums
`packet_status`:
- READY
- READY_WITH_WARNINGS
- BLOCKED
- MISSING_AUTHORITY
- NOT_APPLICABLE
- EXAMPLE_ONLY

`live_status`:
- LIVE
- STUB
- EXAMPLE_ONLY
- NOT_IMPLEMENTED

`confidence`:
- PROVED
- STRONG
- PLAUSIBLE
- UNKNOWN
- FAILED
- FAKE_GREEN_RISK

## No-fake-green corridor
- Example packet sets must carry non-live markers.
- `LIVE` status in this task is prohibited by validator policy.
- Protocol artifacts are not evidence of runtime organ communication.

## Ownership and expected packet focus
- ASTRONOMICON: task decomposition and stage map.
- OFFICIO_AGENTIS: role and response contract linkage.
- DOCTRINARIUM: gate and law constraints.
- ADMINISTRATUM: reporting and receipt requirements.
- MECHANICUS: tool and validator requirements.
- INQUISITION: contradiction and risk detection.
- STRATEGIUM: priority and sequencing decisions.
- SCHOLA_IMPERIALIS: skill readiness and training gaps.

## Versioning
- version: `0.1`
- compatibility: strict within this schema revision
- migration: deferred to future task kernel registry implementation
