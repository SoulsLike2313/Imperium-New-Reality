# PATCH PACK — THRONE-TARGET-GAP-VALIDATOR-0001

status: `WARP_CANDIDATE`  
mode: `MEASURE_ONLY`  
visual_policy: `NO_VISUAL_REFIT`  
primary_organ: `THRONE`

## Purpose

Create the first Throne-wide target gap validator.

The validator compares:

```text
TARGET V1 FORM
  vs
CURRENT REALITY / POPULATION CENSUS
  =
GAP MAP + SCORES + NEXT ATTENTION AREAS
```

This patch does not fix organs, delete files, move files, or block land.  
It measures the distance from current Reality to declared Imperium v1 form.

## Why this exists

The Throne must not validate current chaos as normal.  
It must validate the current system against the ideal target form and show the gap.

Core law:

```text
Gap is not failure.
Failure is inability to measure the gap.
```

## Scope

The first gap validator covers broadly, not deeply:

1. Global core evidence.
2. Throne self-form.
3. Great Nine physical presence.
4. Required organ slots.
5. README / ORGAN_CARD / MANIFEST / FUNCTIONS.
6. Schema / validator / receipt / report coverage.
7. Boundary signals: WARP, rogue, archive, quarantine, negative examples.
8. Observability signals: TUI / dashboards / Eyes data slots.
9. Trust/action readiness hints.
10. Recommended next attention areas.

Deep organ validation is later:
Astra → Admin → Doctrinarium → Mechanicus → Inquisition → Custodes → Strategium → Schola → Officio.

## What this patch adds

```text
WARP/PATCHES/THRONE-TARGET-GAP-VALIDATOR-0001/
  PATCH_PACK.md
  RUN_THRONE_TARGET_GAP_VALIDATION.ps1
  FILES_TO_LAND/
    ORGANS/THRONE/
      MATRICES/
        THRONE_TARGET_GAP_SCORING_MATRIX_V0_1.json
      SCHEMAS/
        throne_target_gap_receipt.schema.json
      VALIDATORS/
        validate_throne_target_gap.py
  REPORTS/.gitkeep
  RECEIPTS/.gitkeep
  TESTS/README.md
```

Generated after run:

```text
ORGANS/THRONE/RECEIPTS/throne_target_gap_receipt.json
ORGANS/THRONE/REPORTS/THRONE_TARGET_GAP_REPORT_V0_1.md
ORGANS/THRONE/REPORTS/THRONE_ORGAN_READINESS_TABLE_V0_1.csv
ORGANS/THRONE/REPORTS/THRONE_NEXT_ATTENTION_AREAS_V0_1.json
```

## Inputs

Required:

```text
ORGANS/THRONE/MATRICES/THRONE_TARGET_V1_MATRIX_V0_1.json
WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/OUTPUTS/IMPERIUM_POPULATION_CENSUS_V0_1.json
```

Optional but used if present:

```text
WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/OUTPUTS/IMPERIUM_POPULATION_SUMMARY_V0_1.json
WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/OUTPUTS/IMPERIUM_POPULATION_GAP_MAP_V0_1.json
```

## Verdicts

```text
PASS_MEASURED
  gap measured successfully; scores and reports generated.

WARN_PARTIAL_EVIDENCE
  gap measured, but evidence is partial.

FAIL_UNMEASURABLE
  missing census, missing target matrix, malformed JSON, or impossible output.

FAIL_FALSE_CLAIM
  future mode: declared full form contradicts evidence.
```

Expected first verdict:

```text
PASS_MEASURED
```

Low scores are expected. They are the map.

## How to run

From repository root:

```powershell
pwsh WARP/PATCHES/THRONE-TARGET-GAP-VALIDATOR-0001/RUN_THRONE_TARGET_GAP_VALIDATION.ps1
```

## Land policy

Land after:

1. Validator returns `PASS_MEASURED`.
2. Receipt/report/table/next attention files are generated.
3. Owner reviews scores.
4. Runtime garbage is removed.
