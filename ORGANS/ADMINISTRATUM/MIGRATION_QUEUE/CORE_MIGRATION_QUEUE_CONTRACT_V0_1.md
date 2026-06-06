# Core Migration Queue Contract V0.1

Status: ACTIVE_DRY_RUN_QUEUE_CONTRACT
Owner organ: ADMINISTRATUM
Guard organs: INQUISITION, CUSTODES

## Purpose

The core migration queue records where files should remain, be investigated, or be considered for a future scoped move. It is a planning artifact only.

## Required Entry Fields

- path
- classification
- owner_organ
- recommended_action
- active_use_allowed
- reason
- risk

## Allowed Classifications

- ORGAN_HOME
- COMMON_SUPPORT
- QUARANTINE_CANDIDATE
- LEGACY_ACCEPTED
- UNKNOWN_OWNER
- FUTURE_SCOPE

## Allowed Recommended Actions

- KEEP
- MOVE_TO_ORGAN
- MOVE_TO_SUPPORT
- MOVE_TO_QUARANTINE
- INVESTIGATE
- FUTURE_SCOPE_HOLD

## Hard Boundary

This contract does not authorize mass physical migration, delete operations, import rewrites, or full cleanup claims. Any MOVE_* recommendation remains dry-run until a separate task explicitly scopes the move and records before/after evidence.
