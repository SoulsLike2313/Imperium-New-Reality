# REALITY ROOT GOVERNANCE REPORT V0.1 FIX 0001

task_id: `GOVERNANCE-ROOT-AND-GREAT-NINE-RECONCILIATION-0001`  
fix_id: `GOVERNANCE-ROOT-AND-GREAT-NINE-RECONCILIATION-0001-FIX-0001`  
validator_id: `reality_root_governance_validator.v0_1_fix_0001`  
verdict: `PASS_REALITY_ROOT_CANON_WITH_TRANSITIONAL_DEBT`  
generated_at_utc: `2026-06-30T09:59:18Z`

## Meaning

The first governance run failed correctly on `.imperium_patch_backups`.

This fix makes `.imperium_patch_backups` explicit root drift and moves it into quarantine:

```text
SUPPORT/QUARANTINE/ROOT_PATCH_BACKUPS_PENDING_BACKUP_POLICY/
```

Previous relocation evidence is preserved and merged into the final root drift registry.

## Root state

- dirs: `['_HARNESS', 'ORGANS', 'SUPPORT', 'WARP']`
- files: `['.editorconfig', '.gitattributes', '.gitignore', 'AGENTS.md']`

## Relocation evidence

Total relocation entries in registry: `2097`

- `DOCTRINARIUM/ANATOMY/IMPERIUM_ANATOMY_v0_2.md` -> `ORGANS/DOCTRINARIUM/LEGACY_ROOT_IMPORT/DOCTRINARIUM/ANATOMY/IMPERIUM_ANATOMY_v0_2.md` sha256_match=`True` action=`MOVE`
- `DOCTRINARIUM/CHARTERS/ADMINISTRATUM.en.md` -> `ORGANS/DOCTRINARIUM/LEGACY_ROOT_IMPORT/DOCTRINARIUM/CHARTERS/ADMINISTRATUM.en.md` sha256_match=`True` action=`MOVE`
- `DOCTRINARIUM/CHARTERS/ADMINISTRATUM.md` -> `ORGANS/DOCTRINARIUM/LEGACY_ROOT_IMPORT/DOCTRINARIUM/CHARTERS/ADMINISTRATUM.md` sha256_match=`True` action=`MOVE`
- `DOCTRINARIUM/CHARTERS/ASTRONOMICON.en.md` -> `ORGANS/DOCTRINARIUM/LEGACY_ROOT_IMPORT/DOCTRINARIUM/CHARTERS/ASTRONOMICON.en.md` sha256_match=`True` action=`MOVE`
- `DOCTRINARIUM/CHARTERS/ASTRONOMICON.md` -> `ORGANS/DOCTRINARIUM/LEGACY_ROOT_IMPORT/DOCTRINARIUM/CHARTERS/ASTRONOMICON.md` sha256_match=`True` action=`MOVE`
- `DOCTRINARIUM/CHARTERS/ASTRONOMICON_FORMS/PATCH_PACK_FORM.md` -> `ORGANS/DOCTRINARIUM/LEGACY_ROOT_IMPORT/DOCTRINARIUM/CHARTERS/ASTRONOMICON_FORMS/PATCH_PACK_FORM.md` sha256_match=`True` action=`MOVE`
- `DOCTRINARIUM/CHARTERS/ASTRONOMICON_FORMS/PATCH_PACK_FORM.template.json` -> `ORGANS/DOCTRINARIUM/LEGACY_ROOT_IMPORT/DOCTRINARIUM/CHARTERS/ASTRONOMICON_FORMS/PATCH_PACK_FORM.template.json` sha256_match=`True` action=`MOVE`
- `DOCTRINARIUM/CHARTERS/ASTRONOMICON_FORMS/TASK_PACK_FORM.md` -> `ORGANS/DOCTRINARIUM/LEGACY_ROOT_IMPORT/DOCTRINARIUM/CHARTERS/ASTRONOMICON_FORMS/TASK_PACK_FORM.md` sha256_match=`True` action=`MOVE`
- `DOCTRINARIUM/CHARTERS/ASTRONOMICON_FORMS/TASK_PACK_FORM.template.json` -> `ORGANS/DOCTRINARIUM/LEGACY_ROOT_IMPORT/DOCTRINARIUM/CHARTERS/ASTRONOMICON_FORMS/TASK_PACK_FORM.template.json` sha256_match=`True` action=`MOVE`
- `DOCTRINARIUM/CHARTERS/DOCTRINARIUM.en.md` -> `ORGANS/DOCTRINARIUM/LEGACY_ROOT_IMPORT/DOCTRINARIUM/CHARTERS/DOCTRINARIUM.en.md` sha256_match=`True` action=`MOVE`
- `DOCTRINARIUM/CHARTERS/DOCTRINARIUM.md` -> `ORGANS/DOCTRINARIUM/LEGACY_ROOT_IMPORT/DOCTRINARIUM/CHARTERS/DOCTRINARIUM.md` sha256_match=`True` action=`MOVE`
- `DOCTRINARIUM/CHARTERS/INQUISITION.en.md` -> `ORGANS/DOCTRINARIUM/LEGACY_ROOT_IMPORT/DOCTRINARIUM/CHARTERS/INQUISITION.en.md` sha256_match=`True` action=`MOVE`
- `DOCTRINARIUM/CHARTERS/INQUISITION.md` -> `ORGANS/DOCTRINARIUM/LEGACY_ROOT_IMPORT/DOCTRINARIUM/CHARTERS/INQUISITION.md` sha256_match=`True` action=`MOVE`
- `DOCTRINARIUM/CHARTERS/MECHANICUS.en.md` -> `ORGANS/DOCTRINARIUM/LEGACY_ROOT_IMPORT/DOCTRINARIUM/CHARTERS/MECHANICUS.en.md` sha256_match=`True` action=`MOVE`
- `DOCTRINARIUM/CHARTERS/MECHANICUS.md` -> `ORGANS/DOCTRINARIUM/LEGACY_ROOT_IMPORT/DOCTRINARIUM/CHARTERS/MECHANICUS.md` sha256_match=`True` action=`MOVE`
- `SCHEMAS/AUTHORED/T4/bundle_file_inventory.schema.json` -> `ORGANS/DOCTRINARIUM/SCHEMAS/AUTHORED/T4/bundle_file_inventory.schema.json` sha256_match=`True` action=`MOVE`
- `SCHEMAS/AUTHORED/T4/SCHEMA_INDEX.md` -> `ORGANS/DOCTRINARIUM/SCHEMAS/AUTHORED/T4/SCHEMA_INDEX.md` sha256_match=`True` action=`MOVE`
- `SCHEMAS/AUTHORED/T4/task_id_resolver_receipt.schema.json` -> `ORGANS/DOCTRINARIUM/SCHEMAS/AUTHORED/T4/task_id_resolver_receipt.schema.json` sha256_match=`True` action=`MOVE`
- `SCHEMAS/AUTHORED/T4/task_receipt.schema.json` -> `ORGANS/DOCTRINARIUM/SCHEMAS/AUTHORED/T4/task_receipt.schema.json` sha256_match=`True` action=`MOVE`
- `SCHEMAS/AUTHORED/T4/task_route_manifest.schema.json` -> `ORGANS/DOCTRINARIUM/SCHEMAS/AUTHORED/T4/task_route_manifest.schema.json` sha256_match=`True` action=`MOVE`
- `SCHEMAS/AUTHORED/T4/taskpack_admission_receipt.schema.json` -> `ORGANS/DOCTRINARIUM/SCHEMAS/AUTHORED/T4/taskpack_admission_receipt.schema.json` sha256_match=`True` action=`MOVE`
- `REPORTS/BRAIN_STATE_SNAPSHOT_V0_1.json` -> `SUPPORT/QUARANTINE/ROOT_REPORTS_PENDING_HARNESS_INTAKE/REPORTS/BRAIN_STATE_SNAPSHOT_V0_1.json` sha256_match=`True` action=`MOVE`
- `REPORTS/eight_organ_identity_rich_shell_run_report.json` -> `SUPPORT/QUARANTINE/ROOT_REPORTS_PENDING_HARNESS_INTAKE/REPORTS/eight_organ_identity_rich_shell_run_report.json` sha256_match=`True` action=`MOVE`
- `REPORTS/EIGHT_ORGAN_IDENTITY_RICH_SHELL_RUN_REPORT.md` -> `SUPPORT/QUARANTINE/ROOT_REPORTS_PENDING_HARNESS_INTAKE/REPORTS/EIGHT_ORGAN_IDENTITY_RICH_SHELL_RUN_REPORT.md` sha256_match=`True` action=`MOVE`
- `REPORTS/FIRST_THREE_AGENT_UNIT_BASELINE_V0_1.json` -> `SUPPORT/QUARANTINE/ROOT_REPORTS_PENDING_HARNESS_INTAKE/REPORTS/FIRST_THREE_AGENT_UNIT_BASELINE_V0_1.json` sha256_match=`True` action=`MOVE`
- ... 2072 more entries in registry

## Checks

- `PASS` — required_governance_files_exist
- `PASS` — no_root_transport_regression
- `PASS` — forbidden_root_drift_dirs_absent
- `PASS` — root_contains_only_allowed_or_transitional_entries
- `PASS` — transitional_warp_harness_debt_recorded
- `PASS` — relocated_sha256_match
- `PASS` — great_nine_canonical_homes_exist
- `PASS` — throne_crown_home_exists
- `PASS` — patch_backups_quarantine_exists
- `PASS` — previous_failed_run_relocations_preserved
- `PASS` — fix_0001_patch_backups_law_active
- `PASS` — external_pillar_policy_defined
- `PASS` — great_nine_alias_policy_defined

## Warnings

- WARP remains inside Reality as transitional debt; canonical external home is E:/IMPERIUM_WARP.
- _HARNESS remains inside Reality as transitional debt; canonical external home is E:/IMPERIUM_HARNESS.

## Errors

- none

## Outputs

- `ORGANS/ADMINISTRATUM/REGISTRY/ROOT_ZONE_GOVERNANCE_REGISTRY_V0_1.json`
- `ORGANS/ADMINISTRATUM/REGISTRY/ROOT_DRIFT_RELOCATION_REGISTRY_V0_1.json`
- `ORGANS/MECHANICUS/RECEIPTS/reality_root_governance_receipt.json`
