# OUTPUT REQUIREMENTS

## Output root

REPORTS/TASK-NEWREALITY-IMPERIAL-IDE-OPERATIONAL-USABILITY-STATION-AGENTIC-WORKFLOW-PC-V0_2/

## Required station outputs

Repository files:

- ORGANS/IMPERIAL_IDE/STATION/README.md
- ORGANS/IMPERIAL_IDE/STATION/station_state.py
- ORGANS/IMPERIAL_IDE/STATION/station_router.py
- ORGANS/IMPERIAL_IDE/STATION/station_receipts.py
- ORGANS/IMPERIAL_IDE/STATION/station_workflow.py
- ORGANS/IMPERIAL_IDE/STATION/station_panels.json
- ORGANS/IMPERIAL_IDE/STATION/operational_state.schema.json
- ORGANS/IMPERIAL_IDE/STATION/lifecycle_tracker.py
- ORGANS/IMPERIAL_IDE/STATION/lifecycle_stage.schema.json
- ORGANS/IMPERIAL_IDE/STATION/lifecycle_state.json
- ORGANS/IMPERIAL_IDE/STATION/RUN_FIRST_RU.md

## Required agent outputs

Repository files:

- ORGANS/IMPERIAL_IDE/AGENTS/README.md
- ORGANS/IMPERIAL_IDE/AGENTS/agent_registry.json
- ORGANS/IMPERIAL_IDE/AGENTS/servitor_roster.json
- ORGANS/IMPERIAL_IDE/AGENTS/agent_card.schema.json
- ORGANS/IMPERIAL_IDE/AGENTS/agent_status.schema.json
- ORGANS/IMPERIAL_IDE/AGENTS/agent_runtime_state.json

## Required UI outputs

Repository updates:

- ORGANS/IMPERIAL_IDE/WORKBENCH/TUI/imperial_tui.py updated safely;
- ORGANS/IMPERIAL_IDE/WORKBENCH/GUI/imperial_gui_workbench.py updated safely or equivalent panel files added;
- ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py updated or adapters added.

Required shell commands or aliases:

- station;
- station-tui;
- station-gui;
- station-smoke;
- agents;
- agent-status;
- task-console;
- new-task;
- build-taskpack;
- validate-taskpack;
- register-taskpack;
- launch-card;
- handoff-card;
- lifecycle;
- reports-latest;
- receipts-latest;
- safety;
- git-closure.

## Required documentation outputs

Repository files:

- ORGANS/IMPERIAL_IDE/DOCS/OPERATIONAL_STATION_USER_GUIDE_RU.md
- ORGANS/IMPERIAL_IDE/DOCS/OPERATIONAL_STATION_WORKFLOW.md
- ORGANS/IMPERIAL_IDE/DOCS/AGENTS_AND_SERVITORS_MODEL.md
- ORGANS/IMPERIAL_IDE/DOCS/LIVE_REGISTRATION_GATE_RUNBOOK.md
- ORGANS/IMPERIAL_IDE/DOCS/NEXT_REAL_EXECUTION_GATE_PLAN.md

## Required report outputs

Report files under REPORTS/TASK-NEWREALITY-IMPERIAL-IDE-OPERATIONAL-USABILITY-STATION-AGENTIC-WORKFLOW-PC-V0_2/:

- station_architecture_receipt.json
- workbench_tui_upgrade_receipt.json
- workbench_gui_upgrade_receipt.json
- agent_registry_receipt.json
- task_console_usability_receipt.json
- taskpack_builder_usability_receipt.json
- live_registration_gate_receipt.json
- launch_card_handoff_receipt.json
- lifecycle_tracker_receipt.json
- reports_receipts_browser_receipt.json
- safety_center_receipt.json
- git_closure_ui_receipt.json
- station_smoke_receipt.json
- validation_receipt.json
- git_diff_scope_receipt.json
- git_commit_push_receipt.json
- continuity_pack.json
- FINAL_OWNER_SUMMARY_RU.md

## Required receipt fields

agent_registry_receipt.json must include task_id, agent_count, servitor_count, servitor_prime_present, organ_servitors_present, warp_servitor_present, metaos_servitor_present, schema_validation_status, timestamp.

task_console_usability_receipt.json must include task_id, templates_visible, task_intent_smoke_created, classification_status, route_preview_status, taskpack_build_status, taskpack_validation_status, timestamp.

live_registration_gate_receipt.json must include task_id, dry_run_default, live_registration_action_present, registration_scope, smoke_task_registered, launch_card_captured, remote_registration_enabled, blockers, timestamp.

safety_center_receipt.json must include real_servitor_execution_enabled, live_llm_backend_enabled, unsafe_shell_available, arbitrary_shell_allowed, dry_run_default, live_registration_enabled, unknown_tool_blocked, secrets_staged, runtime_paths_staged, vm2_action, vm3_action, destructive_cleanup, result.

git_commit_push_receipt.json must include task_id, commit_sha, origin_master_sha, head_equals_origin_master_after_push, git_status_after_push, pushed_files_summary, validation_summary, timestamp.

## Final owner summary

FINAL_OWNER_SUMMARY_RU.md is Russian owner-facing output and must be short.

It must state:

- what changed in Workbench GUI;
- what changed in Workbench TUI;
- how to create a task inside IDE;
- how to build a taskpack inside IDE;
- how to register it;
- where agents and servitors are visible;
- what is live and what is gated;
- whether push completed;
- next recommended task.

It must not claim full IDE completion.
It must not claim real servitor execution.
It must not claim unrestricted tool execution.
It must not claim live LLM backend is enabled.
