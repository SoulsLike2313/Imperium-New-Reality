# Action Rollback Contract V0.1 (Foundation)

## Purpose
Define mandatory rollback declarations for NewGen actions before any future write/mutation expansion (including organ dialogue packet writes, scope merges, and task-state mutations).

## Contract Rule
No mutable action may be treated as PASS without explicit rollback expectations and evidence requirements.

## Required Mutation Classes
- `READ_ONLY_ACTION`
- `GENERATED_STATE_REFRESH`
- `REPORT_WRITE_ACTION`
- `REGISTRY_UPDATE_ACTION`
- `TASK_STATE_MUTATION`
- `ORGAN_DIALOGUE_PACKET_WRITE`
- `SCOPE_MERGE_MUTATION`
- `DANGEROUS_ACTION`

## Required Rollback Verdicts
- `ROLLBACK_NOT_REQUIRED`
- `ROLLBACK_BY_REBUILD`
- `ROLLBACK_BY_BACKUP_RESTORE`
- `ROLLBACK_BY_GIT_RESTORE`
- `ROLLBACK_REQUIRES_OWNER`
- `ROLLBACK_NOT_DEFINED_BLOCK`
- `DANGEROUS_ACTION_BLOCKED`

## Required Fields Per Action Contract
- `action_id`
- `mutation_class`
- `allowed_paths`
- `backup_required`
- `rollback_method`
- `rollback_evidence_required`
- `owner_approval_required`
- `failure_policy`
- `no_fake_green_rule`
- `preconditions`
- `postconditions`

## Safety Boundary
- Dangerous actions are blocked unless explicit owner approval contract reference exists.
- Foundation-only: no destructive mutation testing is claimed by this task.
- This layer defines policy and validation, not autonomous mutation execution.
