# Taskpack Form Contract V0.1

Status: `ACTIVE_STAGE2_CORRIDOR_NOTE_V0_1`
Owner organ: `ASTRONOMICON`
Support organs: `OFFICIO_AGENTIS`, `ADMINISTRATUM`, `INQUISITION`

## Purpose

This note records the agent-readable taskpack form accepted by the current Astronomicon intake gate.

## Canonical Root Files

The taskpack ZIP root must include these files with exact names:

- `MANIFEST.json`
- `TASK_SPEC.md`
- `ACCEPTANCE_GATES.md`
- `OUTPUT_REQUIREMENTS.md`

Alternate legacy names may be recognized by code for migration, but these four names are the canonical Stage2 form for new taskpacks.

## Language And Encoding

Root taskpack files are internal machine/task artifacts. They must be English, UTF8, and no BOM.

Root taskpack files must not contain Cyrillic, mojibake, or replacement characters.

Owner-facing Russian output is allowed only through Officio authority after role entry. Code, schemas, manifests, receipts, route manifests, and internal taskpack files remain English UTF8 no BOM unless an explicit Officio exception receipt says otherwise.

## Intake Gate Expectations

The intake gate must verify:

- safe extraction under `ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/<task_id>/`;
- `MANIFEST.json` contains `task_id`;
- route manifest generation uses all eight required organs;
- start ACK checks organ participation read-first files;
- admission receipt records pass, warning, or block without emitting fake launch proof.

## Required Organs

- `DOCTRINARIUM`
- `OFFICIO_AGENTIS`
- `ASTRONOMICON`
- `ADMINISTRATUM`
- `MECHANICUS`
- `INQUISITION`
- `STRATEGIUM`
- `SCHOLA_IMPERIALIS`
