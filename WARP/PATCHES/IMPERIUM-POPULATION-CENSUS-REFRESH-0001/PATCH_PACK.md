# PATCH PACK — IMPERIUM-POPULATION-CENSUS-REFRESH-0001

status: `WARP_CANDIDATE`  
mode: `CENSUS_REFRESH`  
primary_organ: `ADMINISTRATUM`  
supporting_organs: `THRONE`, `MECHANICUS`

## Purpose

Refresh the current Imperium population census after root transport cleanup.

This is patch 4/6 of the hygiene/control series.

## Why

After `ROOT-TRANSPORT-CLUTTER-RELOCATION-0001`, Reality physically changed:

```text
root transport files moved into SUPPORT/TRANSPORT
root became cleaner
new transport index/registry/receipts appeared
```

The old population census cannot be treated as current truth without refresh.

## Important packaging law

This patch does NOT place root-level transport files in repo root.

No root-level:

```text
APPLY_*.ps1
*_FILE_MANIFEST_SHA256.json
```

Patch provenance lives inside:

```text
WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-REFRESH-0001/
```

## Canonical current outputs

```text
ORGANS/ADMINISTRATUM/REGISTRY/IMPERIUM_POPULATION_CENSUS_CURRENT_V0_2.json
ORGANS/ADMINISTRATUM/REGISTRY/IMPERIUM_POPULATION_SUMMARY_CURRENT_V0_2.json
ORGANS/ADMINISTRATUM/REGISTRY/IMPERIUM_ROOT_ZONE_REGISTRY_V0_2.json
ORGANS/ADMINISTRATUM/RECEIPTS/population_census_refresh_receipt.json
ORGANS/ADMINISTRATUM/REPORTS/IMPERIUM_POPULATION_CENSUS_REFRESH_REPORT_V0_2.md
```

## Staleness guard

```text
ORGANS/THRONE/MATRICES/CENSUS_STALENESS_GUARD_MATRIX_V0_1.json
```

Legacy census remains historical:

```text
WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/OUTPUTS/IMPERIUM_POPULATION_CENSUS_V0_1.json
```

## Validator

```text
ORGANS/ADMINISTRATUM/VALIDATORS/validate_population_census_refresh.py
```

It measures:

```text
population_total
tracked_file_count
working_tree_visible_file_count
root zones
owner coverage
classification coverage
status coverage
root transport hygiene state
legacy census delta
```

## Expected verdict

```text
PASS_CENSUS_REFRESHED
```
