# Officio authority intake gate

## Non-negotiable rule

This taskpack is not role authority.

The agent must obtain role/settings/response contract from canonical Officio sources if available.

## Read-only authority search addresses

Search/read only. Do not modify these paths:

1. `ORGANS/OFFICIO_AGENTIS/`
2. `ORGANS/OFFICIO_AGENTIS/**`
3. `IMPERIUM_NEW_GENERATION/**/OFFICIO*`
4. `IMPERIUM_NEW_GENERATION/**/ROLE*`
5. `IMPERIUM_NEW_GENERATION/**/CONTRACT*`
6. Any explicitly referenced role pack, role registry, response contract, language policy, Servitor/VM worker settings, or gateway contract already present in repo.

## Required output before implementation

Create one of these inside:

`IMPERIUM_NEW_GENERATION/TASKS/VM3_ASSIGNED/TASK-20260520-NEWGEN-MECHANICUS-PANEL-VISUAL-SLICE-VM3-V0_1/`

### If Officio authority found

`OFFICIO_ROLE_ACK_VM3_SERVITOR.json`

### If Officio authority missing/incomplete

`OFFICIO_ROLE_AUTHORITY_MISSING_WARN.json`
