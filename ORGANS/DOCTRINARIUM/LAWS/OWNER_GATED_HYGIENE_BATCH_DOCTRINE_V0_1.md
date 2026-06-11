# Owner-Gated Hygiene Batch Doctrine v0.1

Imperium must fight repository dirt through lanes and gates, not through blind cleanup.

## Rule

A hygiene batch has two distinct phases:

1. **Preview** — classify, count, estimate size, show risks, build owner-facing proof.
2. **Execution** — pack/copy/move/delete only after explicit owner gate.

Preview is never execution. A PASS preview means the plan is inspectable, not that source may be changed.

## Batch 001 default

- Target organ: `REPORTS_LEGACY`
- Target lane: `PACK_TO_VAULT_CANDIDATE`
- Action proposed: later Evidence Vault pack/copy
- Action forbidden now: source delete, source move, git rm

## Trinity Plus requirement

Every hygiene batch preview must include a smotrovaya/visual proof: terminal, owner markdown, HTML dashboard, and machine JSON.
