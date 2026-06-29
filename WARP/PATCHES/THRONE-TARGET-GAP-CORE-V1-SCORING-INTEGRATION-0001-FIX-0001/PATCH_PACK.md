# PATCH PACK — THRONE-TARGET-GAP-CORE-V1-SCORING-INTEGRATION-0001-FIX-0001

status: `WARP_FIX_CANDIDATE`  
mode: `MEASURE_ONLY`  
primary_organ: `THRONE`

## Purpose

Fix the semantic scoring bug in `THRONE-TARGET-GAP-CORE-V1-SCORING-INTEGRATION-0001`.

The previous version correctly proved that Core v1 target anatomy is described, but it mixed target-definition completeness with real operational readiness. That produced misleading numbers:

```text
core_v1_anatomy_readiness_score: 100
core_readiness_score: 84.91
```

This fix separates:

```text
core_v1_target_definition_score
core_v1_operational_evidence_score
core_v1_workflow_readiness_score
core_v1_trust_readiness_score
core_v1_human_visibility_score
core_v1_no_core_mutation_evidence_score
```

## Core rule

```text
Target described != Core operationally ready.
```

## What this patch changes

```text
ORGANS/THRONE/MATRICES/
  THRONE_TARGET_GAP_CORE_V1_SCORING_FIX_0001_MATRIX_V0_1.json

ORGANS/THRONE/SCHEMAS/
  throne_core_v1_operational_breakdown.schema.json

ORGANS/THRONE/VALIDATORS/
  validate_throne_target_gap.py
```

Generated after run:

```text
ORGANS/THRONE/REPORTS/THRONE_CORE_V1_OPERATIONAL_BREAKDOWN_V0_1.json
ORGANS/THRONE/REPORTS/THRONE_CORE_V1_OPERATIONAL_BREAKDOWN_V0_1.csv
```

## Expected effect

`PASS_MEASURED`, but with a more cautious `core_readiness_score`.

The score should now say:

```text
target definition: high / complete
operational evidence: partial / low
workflow readiness: partial / low
trust readiness: low until Custodes/Inquisition are deeper
human visibility: target exists but implementation weak
```

## Land policy

Land only if:

- validator returns `PASS_MEASURED`;
- `errors: []`;
- report clearly separates target definition from operational evidence;
- core score no longer implies near-v1 readiness.
