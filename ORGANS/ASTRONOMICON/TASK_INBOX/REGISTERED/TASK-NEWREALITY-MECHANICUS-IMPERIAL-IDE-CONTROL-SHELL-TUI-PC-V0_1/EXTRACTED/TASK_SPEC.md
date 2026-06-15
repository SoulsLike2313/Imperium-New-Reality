# TASK SPEC

## Task ID

TASK-NEWREALITY-MECHANICUS-IMPERIAL-IDE-CONTROL-SHELL-TUI-PC-V0_1

## Mode

CONTROLLED_WRITE_WITH_VALIDATED_PUSH.

This task is PC only.

This task builds the first managed control shell for Imperium New Reality.

The shell must be Mechanicus-backed, governance-aware, taskpack-aware, receipt-aware, and ready to evolve into the custom Imperial IDE.

This task must not claim a full GUI IDE.

This task must not enable unrestricted shell execution.

## Strategic direction

Imperium New Reality is the kernel.

Imperial IDE is the future local development and control surface built over that kernel.

Mechanicus is the first ultra-form organ because it must guard, validate, route, and receipt every tool the IDE can call.

This task should make the system usable from a controlled local shell before GUI work begins.

## Mission

Perform a large PC build:

1. Build a local Imperial IDE control shell.
2. Build a menu-style TUI foundation.
3. Integrate the shell with Mechanicus registry, capabilities, command policy, validators, and dry-run gateway.
4. Integrate the shell with Astronomicon task registry and reports.
5. Add report and receipt browsing.
6. Add workspace state and extension registry support.
7. Add safe launchers and operator documentation.
8. Validate all outputs.
9. Commit and push validated outputs.

## Phase A: preflight

Required:

- Resolve git root.
- Record git status short.
- Record HEAD and origin/master.
- Confirm HEAD equals origin/master or record why not.
- Confirm governance is CANON_ACTIVE.
- Confirm Mechanicus foundation exists.
- Confirm Imperial IDE foundation exists.
- Confirm no local contour route config or secret is staged.
- Confirm no VM2 or VM3 work is needed.

Stop if current root cannot be established safely.

## Phase B: shell architecture

Create or update the Imperial IDE shell architecture.

Required repository outputs may include:

- ORGANS/IMPERIAL_IDE/SHELL/
- ORGANS/IMPERIAL_IDE/SHELL/README.md
- ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py
- ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_tui.py
- ORGANS/IMPERIAL_IDE/SHELL/shell_router.py
- ORGANS/IMPERIAL_IDE/SHELL/shell_state.py
- ORGANS/IMPERIAL_IDE/SHELL/shell_receipts.py
- ORGANS/IMPERIAL_IDE/SHELL/panel_registry.json
- ORGANS/IMPERIAL_IDE/SHELL/command_palette.json
- ORGANS/IMPERIAL_IDE/SHELL/run_imperial_ide.ps1

The shell must be stdlib-first Python unless an existing dependency is already proven.

The shell must support non-interactive commands for smoke tests.

Required CLI commands:

- doctor;
- status;
- dashboard;
- tasks;
- current-task;
- reports;
- latest-report;
- receipts;
- tools;
- capabilities;
- policy;
- extensions;
- workspace;
- validate;
- dry-run-tool;
- help.

The TUI may be a simple menu loop and does not need curses.

The TUI must not block non-interactive validation. Provide a smoke flag or command.

## Phase C: dashboard panels

Create first panel model for the future IDE.

Required panels:

- Overview panel;
- Governance panel;
- Astronomicon tasks panel;
- Reports panel;
- Receipts panel;
- Mechanicus tools panel;
- Capabilities panel;
- Command policy panel;
- Extensions panel;
- Workspace panel;
- Validation panel.

Each panel must have:

- panel_id;
- title;
- owner_organ;
- data_sources;
- commands;
- risk_class;
- current_status.

Panel registry must parse as JSON.

## Phase D: Mechanicus bridge upgrade

Upgrade or create a bridge that makes the shell call Mechanicus safely.

Required outputs may include:

- ORGANS/IMPERIAL_IDE/BRIDGES/mechanicus_shell_bridge.py
- ORGANS/IMPERIAL_IDE/BRIDGES/mechanicus_bridge_contract.md
- ORGANS/MECHANICUS/IDE_BRIDGE/mechanicus_ide_bridge.py
- ORGANS/MECHANICUS/IDE_BRIDGE/README.md

Required behavior:

- load tool_registry.json;
- load capability_registry.json;
- load command_policy.json;
- list tools;
- list capabilities;
- run doctor;
- validate JSON;
- create dry-run invocation receipt;
- refuse unrestricted real execution;
- record every invocation attempt.

Do not enable real arbitrary shell execution.

## Phase E: Astronomicon dashboard integration

The shell must show task-entry state.

Required behavior:

- locate ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED;
- list registered tasks;
- show current expected task if file exists;
- show latest task reports;
- show taskpack admission receipts;
- show resolver receipts;
- avoid mutation unless a specific future task enables it.

Required outputs may include:

- ORGANS/IMPERIAL_IDE/PANELS/astronomicon_tasks_panel.py
- ORGANS/IMPERIAL_IDE/PANELS/reports_panel.py
- ORGANS/IMPERIAL_IDE/PANELS/receipts_panel.py

## Phase F: workspace and extensions

Create or update workspace and extension foundations.

Required outputs may include:

- ORGANS/IMPERIAL_IDE/WORKSPACE/workspace_state.json
- ORGANS/IMPERIAL_IDE/WORKSPACE/workspace_state_manager.py
- ORGANS/IMPERIAL_IDE/EXTENSIONS/extension_registry.json
- ORGANS/IMPERIAL_IDE/EXTENSIONS/example_mechanicus_extension.json
- ORGANS/IMPERIAL_IDE/EXTENSIONS/extension_loader.py

Extension manifest records must include:

- extension_id;
- name;
- status;
- owner_organ;
- panels;
- commands;
- tool_permissions;
- risk_class;
- receipts_required;
- validation_required.

No extension may gain unrestricted execution authority in this task.

## Phase G: receipts and command history

The shell must emit receipts.

Required outputs may include:

- ORGANS/IMPERIAL_IDE/RECEIPTS/.gitkeep
- ORGANS/IMPERIAL_IDE/SHELL/shell_command_receipt.schema.json
- ORGANS/IMPERIAL_IDE/SHELL/shell_command_history.json

Command receipt fields:

- timestamp_utc;
- command;
- args;
- repo_root;
- status;
- risk_class;
- data_sources;
- tools_invoked;
- dry_run;
- output_summary;
- receipt_path.

Receipts may be written to report output during this task and to IDE receipt directory for smoke tests if safe.

## Phase H: launchers and docs

Required docs:

- ORGANS/IMPERIAL_IDE/DOCS/CONTROL_SHELL_USER_GUIDE.md
- ORGANS/IMPERIAL_IDE/DOCS/CONTROL_SHELL_COMMANDS.md
- ORGANS/IMPERIAL_IDE/DOCS/NEXT_GUI_BUILD_PLAN.md
- ORGANS/IMPERIAL_IDE/DOCS/SAFETY_MODEL.md

Required launcher:

- ORGANS/IMPERIAL_IDE/run_imperial_ide.ps1

Optional root launcher may be proposed but should not be added unless safe.

Document example commands:

- python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py doctor
- python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py dashboard
- python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py tools
- python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py dry-run-tool mechanicus.doctor
- powershell -ExecutionPolicy Bypass -File ORGANS/IMPERIAL_IDE/run_imperial_ide.ps1

## Phase I: validation

Required validation:

- all created JSON parses;
- all created Python files compile with py_compile;
- shell doctor command runs;
- shell dashboard command runs;
- shell tasks command runs;
- shell reports command runs;
- shell receipts command runs;
- shell tools command runs;
- shell capabilities command runs;
- shell policy command runs;
- shell extensions command runs;
- shell workspace command runs;
- shell validate command runs;
- dry-run-tool refuses unsafe tools and receipts its decision;
- no real arbitrary shell execution is enabled;
- no VM2 or VM3 command is run;
- git diff is inside allowed_write_scope.

If a command cannot be implemented safely, mark it BLOCKED and provide a stub that returns a structured blocker.

## Phase J: reports

Create report outputs under:

REPORTS/TASK-NEWREALITY-MECHANICUS-IMPERIAL-IDE-CONTROL-SHELL-TUI-PC-V0_1/

Required reports:

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

## Phase K: commit and validated push

Commit and push are required for success.

Commit message must include:

TASK-NEWREALITY-MECHANICUS-IMPERIAL-IDE-CONTROL-SHELL-TUI-PC-V0_1

After push, record:

- commit SHA;
- origin/master SHA;
- git status;
- pushed files summary;
- post-push equality of HEAD and origin/master.

## Stop conditions

Stop with BLOCK if:

- repo root cannot be resolved;
- git status cannot be read;
- task would require VM2 or VM3;
- unsafe arbitrary command execution is required;
- real execution cannot remain gated;
- secrets or local configs would be staged;
- JSON validation fails and cannot be repaired;
- Python validation fails and cannot be repaired;
- push is rejected and cannot be safely resolved.
