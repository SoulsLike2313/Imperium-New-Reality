# VALIDATOR READONLY EXTERNAL AUDIT MODE SPEC V0.2

owner: `MECHANICUS`  
status: `ACTIVE_BASELINE`  
patch_id: `VALIDATOR-READONLY-EXTERNAL-AUDIT-MODE-0001`

## Purpose

Validators must support safe external audit execution.

Internal Imperium execution may write canonical receipts/reports into `Reality`.
External audit execution must not mutate `Reality`.

## Required CLI flags

Any validator that normally writes canonical outputs MUST accept:

```text
--dry-run
--read-only
--external-audit
--output-dir <path>
```

## Mode law

### Normal mode

Allowed to write canonical receipt/report into `ORGANS/...` or `WARP/...`.

### --dry-run

Reads repo, computes result, prints JSON summary, writes no canonical outputs.

### --read-only

Reads repo, computes result, prints JSON summary, writes no files under repo root.

### --external-audit

Requires `--output-dir <outside_repo_path>` and writes outputs only there.

## Safety invariant

```text
git status --porcelain before
run validator --read-only
git status --porcelain after
```

must remain identical.

## Converted validators

```text
ORGANS/THRONE/VALIDATORS/validate_throne_target_gap.py
ORGANS/THRONE/VALIDATORS/validate_external_audit_consolidation.py
```

## Enforcement validator

```text
ORGANS/MECHANICUS/VALIDATORS/validate_validator_readonly_modes.py
```

## Meaning

This patch does not make all validators safe yet.
It establishes the mode contract and converts the two highest-risk Throne validators first.
