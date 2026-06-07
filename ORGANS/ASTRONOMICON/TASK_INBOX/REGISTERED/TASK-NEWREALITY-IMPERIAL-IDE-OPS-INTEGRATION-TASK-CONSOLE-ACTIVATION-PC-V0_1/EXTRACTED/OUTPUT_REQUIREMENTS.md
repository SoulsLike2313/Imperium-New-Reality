# OUTPUT REQUIREMENTS

## Output root

REPORTS/TASK-NEWREALITY-IMPERIAL-IDE-OPS-INTEGRATION-TASK-CONSOLE-ACTIVATION-PC-V0_1/

## Bundled input archive

Taskpack must include:

- SOURCE_BUNDLES/IMPERIUM_IDE_OPERATIONAL_V0_1.zip

## Required repository outputs

OPS destination:

- ORGANS/IMPERIAL_IDE/OPS/

Required OPS structure:

- ORGANS/IMPERIAL_IDE/OPS/ENGINE/imperium_ops/
- ORGANS/IMPERIAL_IDE/OPS/CLI/
- ORGANS/IMPERIAL_IDE/OPS/TUI/
- ORGANS/IMPERIAL_IDE/OPS/TESTS/
- ORGANS/IMPERIAL_IDE/OPS/TEMPLATES/task_templates.json

Required docs:

- ORGANS/IMPERIAL_IDE/OPS/README.md
- ORGANS/IMPERIAL_IDE/OPS/RUN_FIRST_RU.md
- ORGANS/IMPERIAL_IDE/DOCS/OPS_TASK_CONSOLE_USER_GUIDE_RU.md
- ORGANS/IMPERIAL_IDE/DOCS/OPS_TASKPACK_BUILDER_CONTRACT.md
- ORGANS/IMPERIAL_IDE/DOCS/OPS_ASTRONOMICON_LIVE_REGISTRATION_GATE.md

Required shell or integration updates:

- ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py updated or adapter file added;
- Workbench panel registry updated or panel files added;
- TUI task console path added or documented blocker.

## Required report outputs

Report files under REPORTS/TASK-NEWREALITY-IMPERIAL-IDE-OPS-INTEGRATION-TASK-CONSOLE-ACTIVATION-PC-V0_1/:

- ops_source_inventory.json
- ops_candidate_import_receipt.json
- ops_known_bugfix_receipt.json
- ops_astronomicon_taskpack_builder_receipt.json
- ops_cli_wiring_receipt.json
- ops_workbench_wiring_receipt.json
- ops_tui_wiring_receipt.json
- ops_template_library_receipt.json
- ops_lifecycle_smoke_receipt.json
- ops_safety_gate_receipt.json
- ops_generated_taskpack_smoke_receipt.json
- validation_receipt.json
- git_diff_scope_receipt.json
- git_commit_push_receipt.json
- continuity_pack.json
- FINAL_OWNER_SUMMARY_RU.md

## Required ops_source_inventory.json fields

Must include:

- task_id;
- source_zip_path;
- source_sha256;
- source_size_bytes;
- source_file_count;
- python_file_count;
- top_level_entries;
- timestamp.

## Required ops_known_bugfix_receipt.json fields

Must include:

- task_id;
- validate_intent_contract_fixed;
- cli_classify_smoke_status;
- path_discovery_status;
- push_policy_wording_status;
- live_registration_mode_status;
- changed_files;
- timestamp.

## Required ops_generated_taskpack_smoke_receipt.json fields

Must include:

- task_id;
- generated_taskpack_path;
- generated_taskpack_sha256;
- root_files_present;
- manifest_schema_version;
- cyrillic_in_taskpack_field_present;
- required_organs_present;
- organ_route_present;
- json_parse_status;
- admission_precheck_status;
- timestamp.

## Required ops_safety_gate_receipt.json fields

Must include:

- real_servitor_execution_enabled;
- live_llm_backend_enabled;
- unsafe_shell_available;
- arbitrary_shell_allowed;
- dry_run_default;
- unknown_tool_blocked;
- secrets_staged;
- runtime_paths_staged;
- vm2_action;
- vm3_action;
- result.

## Required git_commit_push_receipt.json fields

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

- where OPS was integrated;
- which bugs were fixed;
- how to open OPS CLI;
- how to open OPS TUI;
- how to build a taskpack;
- how to run lifecycle dry-run;
- what remains blocked for safety;
- whether push completed;
- next recommended task.

It must not claim full IDE completion.
It must not claim real servitor execution.
It must not claim unrestricted tool execution.
It must not claim live LLM backend is enabled.
