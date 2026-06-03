# OWNER_AUDIT_CARD_CONTRACT_V0_1

Status: `CANDIDATE_V0_1`
Owner organ: `ADMINISTRATUM`
Support organs: `OFFICIO_AGENTIS`, `INQUISITION`, `MECHANICUS`

## Purpose

Define a compact, evidence-first review format used when Owner asks to `check` / `verify` a task output bundle, screenshot, or Servitor delivery.

## Trigger

Use this contract when any of these is true:

- Owner provides a task result and asks short verification (`check`, `verify`, equivalent).
- Owner provides screenshot/review bundle without requesting another specific report format.
- Astronomicon route marks verification closure step for this task.

## Required visible order

| Order | Section | Required shape |
| --- | --- | --- |
| 0 | Trigger | 1-2 lines |
| 1 | Quick verdict | Markdown table with fixed fields |
| 2 | Accepted evidence | Table: area / accepted / why it matters |
| 3 | Concerns | Table: risk or cap / status / action |
| 4 | Logos conclusion | 1-2 short engineering paragraphs |
| 5 | Next task value | Exactly two short paragraphs |

## Quick verdict fixed fields

- `Step`
- `Verdict`
- `Final head`
- `Main artifact head`
- `Git closure`
- `Main accepted result`
- `Clean PASS`

## Rules

- Keep output compact; do not dump raw receipts into chat.
- Separate accepted evidence from carried caps.
- Do not claim clean PASS while global caps remain active.
- Section `Next task value` must contain exactly two short paragraphs.
- If Owner asks for taskpack generation after audit, taskpack may be generated as separate step.

## Ownership split

- `ADMINISTRATUM`: continuity truth, evidence boundary, handoff linkage.
- `OFFICIO_AGENTIS`: owner-facing response lane and response contract integration.
- `INQUISITION`: fake-green downgrade policy and clean-context checks.
- `MECHANICUS`: schema and machine artifact validation.

