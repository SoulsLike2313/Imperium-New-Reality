# OFFICIO ROLE ACK CONTRACT V0.1

## Purpose

Enforce explicit admission before work for Servitor/Logos/Speculum/local organ agents.

## Required ACK block

Minimum admission block:

```text
ROLE_ACK: <role_id accepted>
LANGUAGE_ACK: <owner-facing RU accepted>
SCOPE_ACK: <allowed paths and forbidden paths accepted>
STOP_CONDITIONS_ACK: <non-empty stop conditions accepted>
FORBIDDEN_ACTIONS_ACK: <forbidden actions accepted>
```

## Required fields

- task id;
- current head;
- role id;
- allowed write paths;
- forbidden paths;
- expected receipts;
- stop conditions;
- ACK verdict (`PASS | STOP | CLARIFY`).

## Fail conditions

- missing any required ACK;
- partial ACK with unresolved blocker;
- declared scope contradicts expected task scope.

## Enforcement

No ACK means no admission (`NO_GATE_ACK_NO_WORK`).
