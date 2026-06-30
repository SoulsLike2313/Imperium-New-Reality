# PATCH PACK — EXTERNAL-AUDIT-CONTROL-AND-CONSOLIDATION-0001

status: `WARP_CANDIDATE`  
mode: `MEASURE_ONLY`  
primary_organ: `THRONE`  
supporting_organs: `CUSTODES`, `INQUISITION`, `MECHANICUS`

## Purpose

Stop after the first external audit round and consolidate what Codex/Servitor and Grok found.

This patch does not clean Reality yet.

It creates a control layer for:

- comparing independent external audit findings;
- separating confirmed findings from single-source claims;
- normalizing score meaning;
- detecting auditor scope violations;
- defining hard external executor containment law;
- producing the six-patch follow-up sequence.

## Why

External agents helped, but one of them behaved like an unsafe young executor: useful red-team signal, but not clean enough for trust.

Therefore Imperium needs a law:

```text
external audit output is evidence,
not canon,
until Throne consolidates it and Custodes/Inquisition can judge scope and trust.
```

## Six-patch sequence

1. `EXTERNAL-AUDIT-CONTROL-AND-CONSOLIDATION-0001`
2. `VALIDATOR-READONLY-EXTERNAL-AUDIT-MODE-0001`
3. `ROOT-TRANSPORT-CLUTTER-RELOCATION-0001`
4. `IMPERIUM-POPULATION-CENSUS-REFRESH-0001`
5. `GOVERNANCE-ROOT-AND-GREAT-NINE-RECONCILIATION-0001`
6. `THRONE-NO-CORE-MUTATION-PROOF-0001`

Then:

```text
INDEPENDENT-AUDIT-ROUND-2-0001
```

## New files

```text
ORGANS/THRONE/MATRICES/
  EXTERNAL_AUDIT_CONSOLIDATION_MATRIX_V0_1.json
  SCORE_CONTRACT_MATRIX_V0_1.json
  IMPERIUM_HYGIENE_AND_CONTROL_SERIES_PLAN_V0_1.json

ORGANS/CUSTODES/MATRICES/
  EXTERNAL_EXECUTOR_SCOPE_CONTRACT_MATRIX_V0_1.json

ORGANS/INQUISITION/MATRICES/
  AUDITOR_SCOPE_VIOLATION_MATRIX_V0_1.json

ORGANS/MECHANICUS/SPECS/
  VALIDATOR_READONLY_EXTERNAL_AUDIT_MODE_SPEC_V0_1.md

ORGANS/THRONE/SCHEMAS/
  external_audit_consolidation_receipt.schema.json

ORGANS/THRONE/VALIDATORS/
  validate_external_audit_consolidation.py
```

Generated after run:

```text
ORGANS/THRONE/RECEIPTS/external_audit_consolidation_receipt.json
ORGANS/THRONE/REPORTS/EXTERNAL_AUDIT_CONSOLIDATED_FINDINGS_V0_1.md
ORGANS/THRONE/REPORTS/EXTERNAL_AUDIT_CONFLICT_MATRIX_V0_1.csv
ORGANS/THRONE/REPORTS/EXTERNAL_AUDIT_SCORE_NORMALIZATION_V0_1.json
ORGANS/THRONE/REPORTS/EXTERNAL_AUDIT_RECOMMENDED_NEXT_PATCHES_V0_1.md
```

## External dependency

This validator reads external audit folders from:

```text
E:\IMPERIUM_EXTERNAL_AUDITS
```

or from environment variable:

```text
IMPERIUM_EXTERNAL_AUDITS
```

It requires at least two independent audit folders.

## Expected verdict

```text
PASS_CONSOLIDATED
```

## Land policy

Land only if:

- at least two external audits are found;
- score rows are normalized instead of blindly accepted;
- scope-violation detection is active;
- next patch backlog is generated;
- errors are empty.
