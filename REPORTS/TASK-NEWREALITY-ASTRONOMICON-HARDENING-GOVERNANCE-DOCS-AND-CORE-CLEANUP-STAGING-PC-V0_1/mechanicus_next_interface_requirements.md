# Mechanicus Next Interface Requirements

Task: TASK-NEWREALITY-ASTRONOMICON-HARDENING-GOVERNANCE-DOCS-AND-CORE-CLEANUP-STAGING-PC-V0_1

Mechanicus needs a durable interface for reusable tools so operators can distinguish proven capability from candidate scripts.

## Required Tool Fields

- `tool_id`
- `owner_organ`
- `path`
- `command_interfaces`
- `dependencies`
- `dependency_class`
- `risk_class`
- `default_mode` when applicable
- `status`
- `allowlisted_for_reuse`
- `last_replay_timestamp_utc` and `last_replay_receipt_path` when proven

## Status Rules

- `PROVEN_*` requires a current replay receipt.
- `CANDIDATE_*` may be indexed but not treated as stable reusable capability.
- Missing paths or failed replay must become `BLOCKED` or `MISSING`, not PASS.

## CLI Requirement

Each reusable CLI tool should expose a smoke or dry-run command with deterministic JSON output where practical.

## Governance Requirement

No uncarded or unseeded tool should be advertised as reusable Mechanicus capability.
