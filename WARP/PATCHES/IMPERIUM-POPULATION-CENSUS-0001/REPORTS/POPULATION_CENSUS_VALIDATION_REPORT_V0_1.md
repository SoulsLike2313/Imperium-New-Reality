# POPULATION CENSUS VALIDATION REPORT V0.1

task_id: `IMPERIUM-POPULATION-CENSUS-0001`  
validator_id: `population_census_validator.v0_1.fix_0001`  
verdict: `PASS`  
generated_at_utc: `2026-06-29T15:51:40Z`  
fix: `0001`

## Population

population_total: `5367`

## Checks

- `PASS` — required_outputs_exist
- `PASS` — json_outputs_parse
- `PASS` — fix_0001_marker_present
- `PASS` — residents_is_non_empty_list
- `PASS` — all_residents_have_required_fields
- `PASS` — imperium_ids_unique
- `PASS` — resident_paths_exist
- `PASS` — resident_sha256_matches_files
- `PASS` — resident_sha256_shape_valid
- `PASS` — root_level_files_have_root_zone_ROOT
- `PASS` — no_pycache_residents
- `PASS` — scan_scope_count_matches_residents
- `PASS` — summary_counts_match_residents
- `PASS` — csv_row_count_matches_residents
- `PASS` — gap_map_has_required_keys
- `PASS` — unknown_root_zones_no_root_files
- `PASS` — fake_green_guard_not_perfect_without_gaps

## Errors

- none

## Receipt

`WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/RECEIPTS/population_census_receipt.json`
