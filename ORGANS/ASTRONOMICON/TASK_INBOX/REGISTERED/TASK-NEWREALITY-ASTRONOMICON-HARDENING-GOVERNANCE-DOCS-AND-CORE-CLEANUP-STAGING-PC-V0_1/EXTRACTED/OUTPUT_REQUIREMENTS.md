# OUTPUT REQUIREMENTS

## Output root

REPORTS/TASK-NEWREALITY-ASTRONOMICON-HARDENING-GOVERNANCE-DOCS-AND-CORE-CLEANUP-STAGING-PC-V0_1/

## Required governance outputs

- ORGANS/_CORE_GOVERNANCE/README.md
- ORGANS/_CORE_GOVERNANCE/GOVERNANCE_INDEX.json
- ORGANS/_CORE_GOVERNANCE/EMPEROR/PASSPORT_OF_THE_EMPEROR.md
- ORGANS/_CORE_GOVERNANCE/EMPEROR/PASSPORT_OF_THE_EMPEROR_RU.md
- ORGANS/_CORE_GOVERNANCE/CONSTITUTION/CONSTITUTION_OF_THE_IMPERIUM.md
- ORGANS/_CORE_GOVERNANCE/CONSTITUTION/CONSTITUTION_OF_THE_IMPERIUM_RU.md

## Required Astronomicon outputs

Under REPORTS/TASK-NEWREALITY-ASTRONOMICON-HARDENING-GOVERNANCE-DOCS-AND-CORE-CLEANUP-STAGING-PC-V0_1/:

- astronomicon_bootstrap_repair_report.md
- route_discovery_receipt.json
- route_config_discovery_receipt.json
- route_manifest_template_discovery_receipt.json
- astronomicon_smoke_receipt.json
- old_prefix_residue_scan.json

## Required cleanup staging outputs

Under REPORTS/TASK-NEWREALITY-ASTRONOMICON-HARDENING-GOVERNANCE-DOCS-AND-CORE-CLEANUP-STAGING-PC-V0_1/:

- cleanup_staging_plan.md
- cleanup_allowlist.json
- cleanup_denylist.json
- duplicate_and_legacy_map.json
- unknown_zone_report.json
- move_batches_plan.json
- zone_classification_rules_effective.json

## Required governance and AGENTS outputs

Under REPORTS/TASK-NEWREALITY-ASTRONOMICON-HARDENING-GOVERNANCE-DOCS-AND-CORE-CLEANUP-STAGING-PC-V0_1/:

- governance_paths_receipt.json
- agents_patch_receipt.json
- governance_candidate_review.md
- passport_constitution_summary.md

## Required Mechanicus outputs

Under REPORTS/TASK-NEWREALITY-ASTRONOMICON-HARDENING-GOVERNANCE-DOCS-AND-CORE-CLEANUP-STAGING-PC-V0_1/:

- mechanicus_tool_registry_seed.json
- mechanicus_next_interface_requirements.md
- mechanicus_validation_receipt.json

## Required validation and closure outputs

Under REPORTS/TASK-NEWREALITY-ASTRONOMICON-HARDENING-GOVERNANCE-DOCS-AND-CORE-CLEANUP-STAGING-PC-V0_1/:

- command_receipt.json
- validation_receipt.json
- fake_green_scan_receipt.json
- git_diff_scope_receipt.json
- git_commit_push_receipt.json
- continuity_pack.json
- FINAL_OWNER_SUMMARY_RU.md

## Required machine readable structures

### GOVERNANCE_INDEX.json

Must include:

- governance_version;
- status;
- authority_order;
- documents;
- russian_mirrors;
- owner_decisions_required_for_final_canon;
- last_task_id.

### cleanup_allowlist.json

Must include:

- safe_to_stage_later;
- reason;
- evidence_path;
- needs_owner_approval_before_move.

### cleanup_denylist.json

Must include:

- never_delete;
- do_not_move_in_this_task;
- local_configs;
- secrets_patterns;
- remote_contour_paths.

### git_commit_push_receipt.json

Must include:

- task_id;
- commit_sha;
- origin_master_sha;
- head_equals_origin_master_after_push;
- git_status_after_push;
- pushed_files_summary;
- validation_summary;
- timestamp.

## Final owner summary

FINAL_OWNER_SUMMARY_RU.md is Russian owner-facing output and must be short.

It must state:

- what was fixed;
- what governance documents were created;
- what cleanup staging was produced;
- whether push completed;
- what next task is recommended.

It must not claim clean PASS if warnings remain.
