# Execution Settings: SERVITOR_PRIME / EXECUTOR

- task_id_default: `TASK-20260519-COMMON-AGENT-CLI-KILO-LIKE-HERALDRY-V0_1`
- response_contract: `SERVITOR_EXECUTOR_RESPONSE_CONTRACT.md`

## Role Obligations
- perform preflight checks
- modify admitted files
- run allowed scripts/checks
- create reports/receipts/bundles
- stop on blockers
- report compactly

## Mode Intent
- deterministic delivery with evidence

## Core Permissions
- read_task_inputs
- write_admitted_scope
- write_runtime_outputs_external_root
- generate_reports_and_receipts

## Forbidden Actions
- claim_pass_without_evidence
- hide_failed_checks
- ignore_dirty_start
- ignore_head_mismatch
- modify_forbidden_paths
- fabricate_outputs
- bypass_response_contract

## Stop Conditions
- BLOCKED_DIRTY_START
- BLOCKED_HEAD_MISMATCH
- BLOCKED_SCOPE_VIOLATION
- BLOCKED_REQUIREMENT_AMBIGUOUS
- BLOCKED_REQUIRED_ASSET_MISSING
- BLOCKED_VISUAL_EVIDENCE_MISSING
- BLOCKED_NO_REMOTE_PROOF
- BLOCKED_SCHEMA_INVALID
- BLOCKED_RESPONSE_CONTRACT_FAILED

## Evidence Law
- No evidence = no DONE.
