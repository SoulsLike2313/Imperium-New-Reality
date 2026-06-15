# Officio Owner Language Routing

Owner-facing runtime output is Russian.

Machine artifacts, taskpack internals, JSON, schemas, scripts, filenames, receipts, and canonical repo documents are English, UTF-8, no BOM.

This task must not rely on Owner manually correcting Servitor behavior.

If live Owner-facing language drifts away from Russian, record the event as agent-control failure in:

- `servitor_control_chain_receipt.json`
- `CLAIM_LEDGER.json`
- `RED_TEAM_VERDICT.json`

Do not treat manual Owner correction as successful organ control.

The target architecture:

- Officio issues Servitor runtime control.
- Astronomicon injects launch context.
- Doctrinarium defines obedience law.
- Inquisition measures compliance.
- Administratum records continuity.
- Mechanicus provides validators.
- Servitor obeys organ-issued directives.

Any Servitor model can be used in the future. Codex is the first local CLI target, but the control chain must be model-agnostic.
