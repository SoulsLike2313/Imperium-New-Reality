# PATCH PACK — THRONE-TARGET-GAP-ORGAN-IMPLEMENTATION-SPLIT-0001

status: `WARP_CANDIDATE`  
mode: `MEASURE_ONLY`  
primary_organ: `THRONE`

## Purpose

Fix the next semantic optimism bug in Throne target-gap scoring.

After `GREAT-NINE-PROFILE-VALIDATORS-0001`, the Great Nine got baseline passports, machine cards, manifests, function declarations, profile validators, and profile receipts.

That is good.

But the target-gap validator started reporting:

```text
great_nine_readiness_score: 95.89
lowest_organ_readiness_score: 93.67
```

This is too optimistic.

A passported organ is not a fully implemented organ.

## New rule

```text
Organ profile baseline != organ operational implementation.
```

## What this patch adds

```text
ORGANS/THRONE/MATRICES/
  THRONE_ORGAN_IMPLEMENTATION_SPLIT_MATRIX_V0_1.json

ORGANS/THRONE/SCHEMAS/
  throne_organ_implementation_breakdown.schema.json

ORGANS/THRONE/VALIDATORS/
  validate_throne_target_gap.py
```

Generated after run:

```text
ORGANS/THRONE/REPORTS/THRONE_ORGAN_IMPLEMENTATION_BREAKDOWN_V0_1.json
ORGANS/THRONE/REPORTS/THRONE_ORGAN_IMPLEMENTATION_BREAKDOWN_V0_1.csv
```

## Per-organ score split

Each organ receives:

```text
organ_profile_baseline_score
organ_structural_score
organ_operational_score
organ_trust_score
organ_readiness_score
```

## Strictness

Profile receipts and baseline profile validators count toward profile baseline.

They do **not** count as full operational proof.

Operational proof requires organ-specific evidence artifacts, for example:

- Astronomicon intake receipts;
- Administratum task registry/context pack receipts;
- Mechanicus tool/validator harness receipts;
- Inquisition scan/finding receipts;
- Custodes trust receipts;
- Strategium priority/plan receipts;
- Schola lesson/negative-example processing receipts;
- Officio servitor authority receipts.

## Expected effect

`PASS_MEASURED`, but with Great Nine readiness becoming more honest.

The Great Nine should no longer look near-complete just because every organ has a passport.

## Land policy

Land only if:

- `PASS_MEASURED`;
- `errors: []`;
- `great_nine_profile_baseline_score` remains high;
- `great_nine_operational_score` is separate and lower if proof is missing;
- `great_nine_readiness_score` no longer implies full organ implementation.
