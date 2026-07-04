# PATCH PACK — MECHANICUS-UI-WORKSHOP-NO-MONOLITH-MATRIX-HOTFIX-0001

status: `WARP_CANDIDATE`  
owner: `MECHANICUS`  
mode: `MATRIX_CANONICAL_BLOCKER_HOTFIX`

## Purpose

Fix `MECHANICUS-UI-WORKSHOP-AND-NO-MONOLITH-LAW-0001`.

## Diagnosis

The matrix weights were actually 100, but the validator expected the exact canonical blocker:

```text
backend_multi_domain_monolith
```

The matrix had the same meaning as:

```text
backend_command_file_contains_unrelated_policy_domains
```

That was not enough for strict validation.

## Fix

- Adds `backend_multi_domain_monolith` to `blocking_findings`.
- Preserves the existing more descriptive backend blocker.
- Reruns the original Mechanicus UI workshop/no-monolith validator.
- Requires the original receipt to become PASS.

## Expected verdicts

```text
PASS_MECHANICUS_UI_WORKSHOP_AND_NO_MONOLITH_LAW_READY
PASS_MECHANICUS_UI_WORKSHOP_NO_MONOLITH_MATRIX_HOTFIX_READY
```
