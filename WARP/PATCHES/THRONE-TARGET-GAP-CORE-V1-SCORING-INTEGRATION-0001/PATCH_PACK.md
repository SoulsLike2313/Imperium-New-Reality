# PATCH PACK — THRONE-TARGET-GAP-CORE-V1-SCORING-INTEGRATION-0001

status: `WARP_CANDIDATE`  
mode: `MEASURE_ONLY`  
primary_organ: `THRONE`  
visual_policy: `NO_VISUAL_REFIT`

## Purpose

Upgrade the Throne target-gap validator so the Core readiness score includes Core v1 meta-kernel anatomy, not only organ slots and file evidence.

Before this patch, `THRONE-TARGET-GAP-VALIDATOR-0001` measured Throne readiness, Great Nine readiness, required slots, and schema/validator/receipt/report evidence.

After `THRONE-KERNEL-ANATOMY-AND-CORE-V1-TARGET-0001`, the Throne also knows deeper Core v1 target zones:

- kernel anatomy;
- Core v1 definition;
- kernel boundary;
- request packets;
- object registry;
- organ service stack;
- servitor boundary;
- evidence chain;
- trust boundary;
- integration kernel;
- human readability;
- no-core-mutation.

This patch integrates those target zones into the target-gap radar.

## Core law

```text
The score is not final.
The score is a progressively sharper measurement of the gap to Core v1.
```

## What this patch changes

```text
ORGANS/THRONE/MATRICES/
  THRONE_TARGET_GAP_CORE_V1_SCORING_INTEGRATION_MATRIX_V0_1.json

ORGANS/THRONE/SCHEMAS/
  throne_core_v1_readiness_breakdown.schema.json

ORGANS/THRONE/VALIDATORS/
  validate_throne_target_gap.py
```

The validator still emits the original outputs:

```text
ORGANS/THRONE/RECEIPTS/throne_target_gap_receipt.json
ORGANS/THRONE/REPORTS/THRONE_TARGET_GAP_REPORT_V0_1.md
ORGANS/THRONE/REPORTS/THRONE_ORGAN_READINESS_TABLE_V0_1.csv
ORGANS/THRONE/REPORTS/THRONE_NEXT_ATTENTION_AREAS_V0_1.json
```

And adds:

```text
ORGANS/THRONE/REPORTS/THRONE_CORE_V1_READINESS_BREAKDOWN_V0_1.json
ORGANS/THRONE/REPORTS/THRONE_CORE_V1_READINESS_BREAKDOWN_V0_1.csv
```

## New scoring zones

```text
kernel_anatomy_score
core_v1_definition_score
kernel_boundary_score
request_packet_score
object_registry_score
organ_service_stack_score
servitor_boundary_score
evidence_chain_score
trust_boundary_score
integration_kernel_score
human_readability_score
no_core_mutation_score
```

## Expected verdict

`PASS_MEASURED`

It means the target gap was measured with Core v1 scoring integration. It does not mean Core v1 is achieved.
