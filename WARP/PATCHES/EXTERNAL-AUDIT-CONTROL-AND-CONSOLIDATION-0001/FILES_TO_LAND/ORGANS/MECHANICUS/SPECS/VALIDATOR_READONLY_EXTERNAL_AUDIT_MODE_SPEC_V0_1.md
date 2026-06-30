# VALIDATOR READONLY EXTERNAL AUDIT MODE SPEC V0.1

owner: `MECHANICUS`  
status: `WARP_CANDIDATE`  
related_patch: `EXTERNAL-AUDIT-CONTROL-AND-CONSOLIDATION-0001`

## Purpose

External auditors must be able to evaluate Imperium without mutating `Reality`.

Current validators often write receipts/reports as part of normal execution. That is acceptable for internal patch execution, but unsafe for independent external audit.

## Required future validator modes

Every validator that writes outputs SHOULD support:

```text
--dry-run
--read-only
--external-audit
--output-dir <outside_repo_path>
```

## Behavior

### Normal internal mode

Allowed to write canonical receipts/reports under `ORGANS/...` or `WARP/...` when executed as part of a registered patch/task flow.

### External audit mode

Must not write to original repo.

Allowed outputs:

```text
E:\IMPERIUM_EXTERNAL_AUDITS\<AUDIT_ID>\validator_replay\...
```

### Dry run

Should perform checks and print/emit JSON result without writing any canonical receipt.

## Violation

A validator that writes canonical receipts while an external auditor is in read-only mode creates:

```text
AUDITOR_SCOPE_VIOLATION
```

or

```text
VALIDATOR_EXTERNAL_AUDIT_MODE_MISSING
```

depending on whether the auditor or validator caused the mutation.

## Future patch

`VALIDATOR-READONLY-EXTERNAL-AUDIT-MODE-0001` must convert the most important validators first:

- `ORGANS/THRONE/VALIDATORS/validate_throne_target_gap.py`
- Great Nine profile validators
- population census validator
- owner docs validator
- future Custodes/Inquisition validators
