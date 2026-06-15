# Officio authority intake gate

## Non-negotiable rule

This taskpack is not role authority.

The agent must obtain role/settings/response contract from canonical Officio sources if available.  
The taskpack may only provide task scope and addresses.

## Read-only authority search addresses

Search/read only. Do not modify these paths:

1. `ORGANS/OFFICIO_AGENTIS/`
2. `ORGANS/OFFICIO_AGENTIS/**`
3. `IMPERIUM_NEW_GENERATION/**/OFFICIO*`
4. `IMPERIUM_NEW_GENERATION/**/ROLE*`
5. `IMPERIUM_NEW_GENERATION/**/CONTRACT*`
6. any explicitly referenced Officio role pack, role registry, response contract, language policy, Servitor/VM worker settings, or gateway contract already present in repo.

## Required output before implementation

Create one of these inside:

`IMPERIUM_NEW_GENERATION/TASKS/VM3_ASSIGNED/TASK-20260520-NEWGEN-VISUAL-TOPOLOGY-HARDEN-10-ORGAN-COVERAGE-VM3-V0_2R/`

### If Officio authority found

`OFFICIO_ROLE_ACK_VM3_SERVITOR.json`

Required fields:
- `ack_id`
- `task_id`
- `authority_status`: `FOUND`
- `canonical_files_read`
- `role_family`
- `role_profile`
- `execution_contour`
- `language_rules`
- `response_format_rules`
- `scope_rules_from_officio`
- `commit_push_rules_from_officio`
- `stop_conditions_from_officio`
- `evidence_rules_from_officio`
- `taskpack_rules_are_task_specific_not_role_authority`: `true`
- `limitations`

### If Officio authority missing/incomplete

`OFFICIO_ROLE_AUTHORITY_MISSING_WARN.json`

Required fields:
- `task_id`
- `authority_status`: `MISSING_OR_INCOMPLETE`
- `searched_paths`
- `missing_items`
- `risk`
- `owner_correction_used`
- `taskpack_rules_are_task_specific_not_role_authority`: `true`
- `continue_mode`: `WARN_UNDER_OWNER_TASK_SCOPE_ONLY` or `BLOCK_PENDING_OWNER`

## Stop condition

If the agent cannot determine any role/settings/response authority and cannot safely continue under Owner correction, it must stop with BLOCK.

## Work log requirement

Append to `WORK_LOG.md`:

`Taskpack is not role authority. Officio authority intake completed or missing-authority WARN recorded before implementation.`
