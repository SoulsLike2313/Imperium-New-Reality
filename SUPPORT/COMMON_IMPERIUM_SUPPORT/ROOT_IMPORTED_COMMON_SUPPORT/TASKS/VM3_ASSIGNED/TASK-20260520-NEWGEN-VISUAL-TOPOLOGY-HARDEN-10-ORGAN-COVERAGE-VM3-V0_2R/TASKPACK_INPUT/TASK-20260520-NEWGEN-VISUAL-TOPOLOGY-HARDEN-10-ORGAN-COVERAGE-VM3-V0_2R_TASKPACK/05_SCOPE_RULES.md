# Scope rules

## Allowed write scope

- `IMPERIUM_NEW_GENERATION/SANCTUM_VISUAL_FOUNDRY/**`
- `IMPERIUM_NEW_GENERATION/TASKS/VM3_ASSIGNED/TASK-20260520-NEWGEN-VISUAL-TOPOLOGY-HARDEN-10-ORGAN-COVERAGE-VM3-V0_2R/**`

## Read-only authority scope

- `ORGANS/OFFICIO_AGENTIS/**`
- other existing Officio role/settings references in repo

## Forbidden write scope

- `ORGANS/**`
- `SANCTUM/**`
- `IMPERIUM_TEST_VERSION/**`
- root unrelated files
- VM2 work
- laptop/Throne operational work

## Artifact rule

Do not create external task folders outside the repo.  
All task artifacts must be committed inside the repo.

## Git rule

Do not use blind `git add -A` if forbidden paths are dirty.  
Prefer explicit staging:
- `git add -- IMPERIUM_NEW_GENERATION/SANCTUM_VISUAL_FOUNDRY`
- `git add -- IMPERIUM_NEW_GENERATION/TASKS/VM3_ASSIGNED/TASK-20260520-NEWGEN-VISUAL-TOPOLOGY-HARDEN-10-ORGAN-COVERAGE-VM3-V0_2R`
