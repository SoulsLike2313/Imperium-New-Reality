# OUTPUT REQUIREMENTS

## Output root

REPORTS/TASK-NEWREALITY-MECHANICUS-IMPERIAL-IDE-CONTROL-SHELL-TUI-PC-V0_1/

## Required Imperial IDE shell outputs

Repository files:

- ORGANS/IMPERIAL_IDE/SHELL/README.md
- ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py
- ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_tui.py
- ORGANS/IMPERIAL_IDE/SHELL/shell_router.py
- ORGANS/IMPERIAL_IDE/SHELL/shell_state.py
- ORGANS/IMPERIAL_IDE/SHELL/shell_receipts.py
- ORGANS/IMPERIAL_IDE/SHELL/panel_registry.json
- ORGANS/IMPERIAL_IDE/SHELL/command_palette.json
- ORGANS/IMPERIAL_IDE/SHELL/shell_command_receipt.schema.json
- ORGANS/IMPERIAL_IDE/SHELL/shell_command_history.json
- ORGANS/IMPERIAL_IDE/run_imperial_ide.ps1

## Required panel outputs

Repository files may include:

- ORGANS/IMPERIAL_IDE/PANELS/overview_panel.py
- ORGANS/IMPERIAL_IDE/PANELS/governance_panel.py
- ORGANS/IMPERIAL_IDE/PANELS/astronomicon_tasks_panel.py
- ORGANS/IMPERIAL_IDE/PANELS/reports_panel.py
- ORGANS/IMPERIAL_IDE/PANELS/receipts_panel.py
- ORGANS/IMPERIAL_IDE/PANELS/mechanicus_tools_panel.py
- ORGANS/IMPERIAL_IDE/PANELS/capabilities_panel.py
- ORGANS/IMPERIAL_IDE/PANELS/command_policy_panel.py
- ORGANS/IMPERIAL_IDE/PANELS/extensions_panel.py
- ORGANS/IMPERIAL_IDE/PANELS/workspace_panel.py
- ORGANS/IMPERIAL_IDE/PANELS/validation_panel.py

If panel modules are not created, panel registry must still define the panels and the blocker must be reported.

## Required Mechanicus bridge outputs

Repository files:

- ORGANS/IMPERIAL_IDE/BRIDGES/mechanicus_shell_bridge.py
- ORGANS/MECHANICUS/IDE_BRIDGE/mechanicus_ide_bridge.py
- ORGANS/MECHANICUS/IDE_BRIDGE/README.md

## Required workspace and extension outputs

Repository files:

- ORGANS/IMPERIAL_IDE/WORKSPACE/workspace_state.json
- ORGANS/IMPERIAL_IDE/WORKSPACE/workspace_state_manager.py
- ORGANS/IMPERIAL_IDE/EXTENSIONS/extension_registry.json
- ORGANS/IMPERIAL_IDE/EXTENSIONS/example_mechanicus_extension.json
- ORGANS/IMPERIAL_IDE/EXTENSIONS/extension_loader.py

## Required documentation outputs

Repository files:

- ORGANS/IMPERIAL_IDE/DOCS/CONTROL_SHELL_USER_GUIDE.md
- ORGANS/IMPERIAL_IDE/DOCS/CONTROL_SHELL_COMMANDS.md
- ORGANS/IMPERIAL_IDE/DOCS/NEXT_GUI_BUILD_PLAN.md
- ORGANS/IMPERIAL_IDE/DOCS/SAFETY_MODEL.md

## Required report outputs

Report files under REPORTS/TASK-NEWREALITY-MECHANICUS-IMPERIAL-IDE-CONTROL-SHELL-TUI-PC-V0_1/:

- imperial_ide_control_shell_summary.md
- shell_command_smoke_receipt.json
- shell_panel_registry_receipt.json
- mechanicus_bridge_upgrade_receipt.json
- astronomicon_dashboard_integration_receipt.json
- extension_loader_receipt.json
- workspace_state_receipt.json
- safety_gate_receipt.json
- validation_receipt.json
- git_diff_scope_receipt.json
- git_commit_push_receipt.json
- continuity_pack.json
- FINAL_OWNER_SUMMARY_RU.md

## Required receipt fields

### shell_command_smoke_receipt.json

Must include:

- task_id;
- commands_tested;
- pass_count;
- warning_count;
- block_count;
- receipt_paths;
- timestamp.

### mechanicus_bridge_upgrade_receipt.json

Must include:

- task_id;
- tool_registry_loaded;
- capability_registry_loaded;
- command_policy_loaded;
- dry_run_receipt_created;
- real_execution_blocked;
- unsafe_shell_available;
- timestamp.

### astronomicon_dashboard_integration_receipt.json

Must include:

- task_id;
- task_inbox_found;
- registered_task_count;
- current_expected_task_found;
- latest_reports_count;
- receipt_view_status;
- timestamp.

### extension_loader_receipt.json

Must include:

- task_id;
- extension_registry_loaded;
- example_extension_loaded;
- unrestricted_execution_permissions_found;
- validation_status;
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

- what shell was created;
- what commands are available;
- what Mechanicus bridge can do;
- what remains blocked for safety;
- whether push completed;
- next recommended task.

It must not claim full GUI IDE implementation.
It must not claim unrestricted real tool execution.
