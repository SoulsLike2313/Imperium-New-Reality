# PATCH PACK — VALIDATOR-READONLY-EXTERNAL-AUDIT-MODE-0001

status: `WARP_CANDIDATE`  
mode: `CONTROL_HARDENING`  
primary_organ: `MECHANICUS`  
supporting_organs: `THRONE`, `CUSTODES`, `INQUISITION`

## Purpose

Give the first high-risk validators a safe external-audit execution mode.

This is patch 2/6 of the hygiene/control series.

## Converted validators

```text
ORGANS/THRONE/VALIDATORS/validate_throne_target_gap.py
ORGANS/THRONE/VALIDATORS/validate_external_audit_consolidation.py
```

## Required flags

```text
--dry-run
--read-only
--external-audit
--output-dir <path>
```

## Added Mechanicus proof validator

```text
ORGANS/MECHANICUS/VALIDATORS/validate_validator_readonly_modes.py
```

It checks:

```text
source flags present
--help exposes required flags
--read-only run succeeds
--read-only does not change git status
--external-audit run succeeds
--external-audit writes outside repo
--external-audit does not change git status
```

## Expected verdict

```text
PASS_READONLY_MODE_BASELINE
```

## Important limitation

This patch does not convert every validator.
It converts the first two highest-risk Throne validators and creates the standard for the rest.
