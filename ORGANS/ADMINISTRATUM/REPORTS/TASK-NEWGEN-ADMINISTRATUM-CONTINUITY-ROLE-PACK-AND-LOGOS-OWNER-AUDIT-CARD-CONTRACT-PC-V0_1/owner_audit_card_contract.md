# Owner Audit Card Contract

Contract ID: `OWNER_AUDIT_CARD_CONTRACT_V0_1`
Owner organ: `ADMINISTRATUM`
Status: `CANDIDATE_V0_1`

## Trigger

Use this format when Owner provides task evidence, screenshot, review ZIP, Servitor output, or says a short verification phrase such as `check` / `verify`.

## Required section order

| Order | Section | Required output shape |
| --- | --- | --- |
| 0 | Trigger | 1-2 lines |
| 1 | Quick verdict | Table with fixed fields |
| 2 | Accepted evidence | Table: area / accepted / why it matters |
| 3 | Concerns | Table: risk or cap / status / action |
| 4 | Logos conclusion | 1-2 short engineering paragraphs |
| 5 | Next task value | Exactly two short paragraphs |

## Quick verdict fixed fields

- Step
- Verdict
- Final head
- Main artifact head
- Git closure
- Main accepted result
- Clean PASS

## Rules

- Keep output compact and evidence-first.
- Do not dump raw JSON in owner-facing chat.
- Separate accepted evidence from carried caps.
- Do not claim clean PASS when global caps remain active.
- `Next task value` must contain exactly two short paragraphs.
