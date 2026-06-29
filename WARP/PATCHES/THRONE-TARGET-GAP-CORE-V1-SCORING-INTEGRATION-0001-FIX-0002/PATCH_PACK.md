# PATCH PACK — THRONE-TARGET-GAP-CORE-V1-SCORING-INTEGRATION-0001-FIX-0002

status: `WARP_FIX_CANDIDATE`
mode: `MEASURE_ONLY`
primary_organ: `THRONE`

## Purpose

Fix semantic over-scoring from FIX-0001.

FIX-0001 correctly separated target definition from operational evidence, but the evidence detector was too loose:

```text
trust_readiness_score: 100
human_visibility_score: 100
workflow_readiness_score: 85.71
core_readiness_score: 84.45
```

That happened because generic path words like `inquisition`, `custodes`, `receipt`, `report`, `tui`, `warp` were counted as proof.

This is wrong.

## New rule

```text
Target documents and directory names are not operational proof.
Operational proof requires specific evidence artifacts:
  task pack / task registry / intake receipt / context pack /
  servitor execution receipt / fix-loop receipt / trust receipt /
  no-core-mutation receipt / TUI implementation artifact.
```

## What this patch changes

```text
ORGANS/THRONE/MATRICES/
  THRONE_TARGET_GAP_CORE_V1_SCORING_FIX_0002_MATRIX_V0_1.json

ORGANS/THRONE/SCHEMAS/
  throne_core_v1_strict_operational_breakdown.schema.json

ORGANS/THRONE/VALIDATORS/
  validate_throne_target_gap.py
```

## Expected effect

Expected verdict remains:

```text
PASS_MEASURED
```

But scores should become more honest:

```text
core_v1_target_definition_score: high
core_v1_operational_evidence_score: low/partial
core_v1_workflow_readiness_score: low/partial
core_v1_trust_readiness_score: low until Custodes/Inquisition trust receipts exist
core_v1_human_visibility_score: partial until actual TUI/dashboard implementation exists
core_v1_no_core_mutation_evidence_score: low until before/after and allowed-return receipts exist
core_readiness_score: cautious, not near-v1
```

## Land policy

Land only if:

- `PASS_MEASURED`;
- `errors: []`;
- generic path names no longer inflate trust/human/workflow;
- core score no longer implies v1 readiness while proof artifacts are missing.
