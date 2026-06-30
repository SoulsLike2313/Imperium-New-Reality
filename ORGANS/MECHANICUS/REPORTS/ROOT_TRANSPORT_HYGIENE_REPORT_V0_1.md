# ROOT TRANSPORT HYGIENE REPORT V0.1

task_id: `ROOT-TRANSPORT-CLUTTER-RELOCATION-0001`  
validator_id: `root_transport_hygiene_validator.v0_1`  
verdict: `PASS_ROOT_TRANSPORT_HYGIENE`  
generated_at_utc: `2026-06-30T09:23:05Z`

## Meaning

This report proves root-level transport clutter has been relocated without losing SHA256 provenance.

## Summary

- total_relocated_entries: `32`
- apply_scripts: `16`
- file_manifests: `16`
- sha256_all_match: `True`

## Checks

- `PASS` — root_transport_candidates_collected
- `PASS` — root_has_no_apply_scripts
- `PASS` — root_has_no_file_manifests
- `PASS` — all_relocated_destinations_exist
- `PASS` — all_relocated_sha256_match
- `PASS` — support_transport_dirs_exist
- `PASS` — warp_patches_still_exists
- `PASS` — matrix_exists

## Warnings

- none

## Errors

- none

## Outputs

- `SUPPORT/TRANSPORT/ROOT_TRANSPORT_INDEX_V0_1.json`
- `SUPPORT/TRANSPORT/ROOT_TRANSPORT_INDEX_V0_1.md`
- `ORGANS/ADMINISTRATUM/REGISTRY/ROOT_TRANSPORT_RELOCATION_REGISTRY_V0_1.json`
- `ORGANS/MECHANICUS/RECEIPTS/root_transport_hygiene_receipt.json`
