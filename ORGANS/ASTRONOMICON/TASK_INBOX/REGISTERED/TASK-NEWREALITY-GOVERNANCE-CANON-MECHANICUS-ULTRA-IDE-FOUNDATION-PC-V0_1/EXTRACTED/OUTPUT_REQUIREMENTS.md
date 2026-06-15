# OUTPUT REQUIREMENTS

## Output root

REPORTS/TASK-NEWREALITY-GOVERNANCE-CANON-MECHANICUS-ULTRA-IDE-FOUNDATION-PC-V0_1/

## Required governance outputs

Repository files:

- ORGANS/_CORE_GOVERNANCE/README.md
- ORGANS/_CORE_GOVERNANCE/GOVERNANCE_INDEX.json
- ORGANS/_CORE_GOVERNANCE/EMPEROR/PASSPORT_OF_THE_EMPEROR.md
- ORGANS/_CORE_GOVERNANCE/EMPEROR/PASSPORT_OF_THE_EMPEROR_RU.md
- ORGANS/_CORE_GOVERNANCE/CONSTITUTION/CONSTITUTION_OF_THE_IMPERIUM.md
- ORGANS/_CORE_GOVERNANCE/CONSTITUTION/CONSTITUTION_OF_THE_IMPERIUM_RU.md

Report files:

- governance_canonization_receipt.json
- governance_canonization_summary.md
- agents_boot_law_patch_receipt.json

## Required Astronomicon outputs

Report files:

- astronomicon_local_hardening_receipt.json
- astronomicon_local_hardening_summary.md
- route_root_discovery_receipt.json

Optional repository files if safe:

- ORGANS/ASTRONOMICON/run_astronomicon_pc.ps1
- ORGANS/ASTRONOMICON/README_PC_LAUNCH.md

## Required Mechanicus outputs

Repository files:

- ORGANS/MECHANICUS/README.md
- ORGANS/MECHANICUS/REGISTRY/tool_registry.json
- ORGANS/MECHANICUS/REGISTRY/capability_registry.json
- ORGANS/MECHANICUS/REGISTRY/command_policy.json
- ORGANS/MECHANICUS/SCHEMAS/tool_card.schema.json
- ORGANS/MECHANICUS/SCHEMAS/capability_record.schema.json
- ORGANS/MECHANICUS/SCHEMAS/command_receipt.schema.json
- ORGANS/MECHANICUS/SCHEMAS/tool_invocation.schema.json
- ORGANS/MECHANICUS/TOOLS/mechanicus_cli.py
- ORGANS/MECHANICUS/TOOLS/mechanicus_doctor.py
- ORGANS/MECHANICUS/TOOLS/mechanicus_inventory.py
- ORGANS/MECHANICUS/TOOLS/mechanicus_validate.py
- ORGANS/MECHANICUS/TOOLS/mechanicus_command_gateway.py

Report files:

- mechanicus_ultra_foundation_summary.md
- mechanicus_tool_registry_validation_receipt.json
- mechanicus_command_gateway_safety_receipt.json

## Required custom IDE foundation outputs

Repository files:

- ORGANS/IMPERIAL_IDE/README.md
- ORGANS/IMPERIAL_IDE/CONTRACTS/IDE_KERNEL_CONTRACT.md
- ORGANS/IMPERIAL_IDE/CONTRACTS/IDE_EXTENSION_API_CONTRACT.md
- ORGANS/IMPERIAL_IDE/CONTRACTS/IDE_TOOL_INVOCATION_CONTRACT.md
- ORGANS/IMPERIAL_IDE/SCHEMAS/ide_extension_manifest.schema.json
- ORGANS/IMPERIAL_IDE/SCHEMAS/ide_workspace_state.schema.json
- ORGANS/IMPERIAL_IDE/SCHEMAS/ide_tool_invocation.schema.json
- ORGANS/IMPERIAL_IDE/SCHEMAS/ide_panel_registry.schema.json
- ORGANS/IMPERIAL_IDE/EXTENSIONS/extension_registry.json
- ORGANS/IMPERIAL_IDE/WORKSPACE/workspace_model.json
- ORGANS/IMPERIAL_IDE/BRIDGES/mechanicus_bridge_contract.md
- ORGANS/IMPERIAL_IDE/DOCS/IDE_BUILD_LADDER.md

Report files:

- imperial_ide_foundation_summary.md
- ide_extension_model_receipt.json

## Required validation and closure outputs

Report files:

- command_receipt.json
- validation_receipt.json
- git_diff_scope_receipt.json
- git_commit_push_receipt.json
- continuity_pack.json
- FINAL_OWNER_SUMMARY_RU.md

## Required receipt fields

### governance_canonization_receipt.json

Must include:

- task_id;
- canonized_files;
- previous_status;
- new_status;
- owner_approval_reference;
- authority_order;
- timestamp.

### mechanicus_tool_registry_validation_receipt.json

Must include:

- task_id;
- registry_paths;
- schema_paths;
- parsed_json_count;
- python_compile_status;
- doctor_status;
- blocked_items;
- timestamp.

### ide_extension_model_receipt.json

Must include:

- task_id;
- ide_root;
- extension_schema_path;
- extension_registry_path;
- mechanicus_bridge_path;
- validation_status;
- next_build_task;
- timestamp.

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

- governance canonization result;
- Mechanicus ultra foundation result;
- custom IDE foundation result;
- Astronomicon local hardening result;
- whether push completed;
- next recommended task.

It must not claim full IDE implementation.
It must not claim all tools are proven.
