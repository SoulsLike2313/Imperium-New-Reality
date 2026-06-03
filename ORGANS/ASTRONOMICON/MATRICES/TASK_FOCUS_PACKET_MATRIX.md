# TASK_FOCUS_PACKET_MATRIX

Status: `CANDIDATE_NOT_CANON`
Owner organ: `Astronomicon`
Support organs: Officio Agentis, Mechanicus, Inquisition, Administratum

## Purpose

Defines the compact packet an agent receives before work: task intent, route, owner organs, outputs, gates, settings, evidence and red-team checks.

## Required questions

- What is the task intent?
- What are allowed and forbidden scopes?
- Which organ packets are relevant?
- Which output files are required?
- Which gates determine PASS/WARN/BLOCK?

## PASS criteria

- Packet created before work
- Organ owners declared
- Outputs and gates declared
- Evidence boundary declared

## WARN criteria

- Some organ packet missing but gap declared
- Owner question open with cap

## BLOCK criteria

- No focus packet
- No task route
- No stop conditions
- No final output contract

## Fake-green flags

- `BROAD_TASK_NO_ROUTE`
- `NO_OUTPUT_CONTRACT`
- `NO_STOP_CONDITIONS`

## Evidence requirements

- `TASK_FOCUS_PACKET.json`
- `ROLE_ENTRY_ACK.json`
- `OWNER_QUESTION_LEDGER.json`
