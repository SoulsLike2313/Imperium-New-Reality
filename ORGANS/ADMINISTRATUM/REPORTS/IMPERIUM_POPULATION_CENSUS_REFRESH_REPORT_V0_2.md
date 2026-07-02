# IMPERIUM POPULATION CENSUS REFRESH REPORT V0.2

task_id: `IMPERIUM-POPULATION-CENSUS-REFRESH-0001`  
validator_id: `imperium_population_census_refresh_validator.v0_2`  
verdict: `PASS_CENSUS_REFRESHED`  
generated_at_utc: `2026-07-02T12:05:30Z`

## Meaning

This report refreshes the current Imperium population census after root transport relocation.

The current census now lives as a first-class Administratum registry artifact.

Legacy WARP census artifacts remain historical unless explicitly refreshed.

## Summary

- population_total: `6732`
- tracked_file_count: `6581`
- repo_head: `20efa57ccd52c2c968c395f15e4bad73afe3de31`
- owner_coverage_score: `100.0`
- classification_coverage_score: `90.61`
- status_coverage_score: `100.0`
- unknown_owner_count: `0`
- unknown_class_count: `632`
- unknown_status_count: `0`

## Root zones

- `ORGANS`: `3122`
- `SUPPORT`: `2633`
- `WARP`: `939`
- `_HARNESS`: `34`
- `.editorconfig`: `1`
- `.gitattributes`: `1`
- `.gitignore`: `1`
- `AGENTS.md`: `1`

## Transport hygiene state

- root_apply_scripts: `[]`
- root_file_manifests: `[]`
- support_transport_index_exists: `True`

## Legacy comparison

- legacy_census_exists: `True`
- legacy_population_total: `6001`
- population_delta_vs_legacy: `731`

## Checks

- `PASS` — git_ls_files_available
- `PASS` — root_transport_clutter_absent
- `PASS` — support_transport_index_exists
- `PASS` — census_matrix_exists
- `PASS` — staleness_guard_matrix_exists
- `PASS` — root_zones_registered
- `PASS` — canonical_census_built
- `PASS` — coverage_measured
- `PASS` — legacy_comparison_built

## Warnings

- none

## Errors

- none

## Outputs

- `ORGANS/ADMINISTRATUM/REGISTRY/IMPERIUM_POPULATION_CENSUS_CURRENT_V0_2.json`
- `ORGANS/ADMINISTRATUM/REGISTRY/IMPERIUM_POPULATION_SUMMARY_CURRENT_V0_2.json`
- `ORGANS/ADMINISTRATUM/REGISTRY/IMPERIUM_ROOT_ZONE_REGISTRY_V0_2.json`
- `ORGANS/ADMINISTRATUM/RECEIPTS/population_census_refresh_receipt.json`
