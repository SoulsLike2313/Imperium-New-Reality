# OUTPUT REQUIREMENTS

## Output root

REPORTS/TASK-NEWREALITY-IMPERIAL-IDE-OPERATIONAL-STATION-UX-HARDENING-AGENT-ROSTER-DIRTY-CLASSIFIER-PC-V0_1/

## Required repository outputs

Station modules:

- ORGANS/IMPERIAL_IDE/STATION/summary_renderer.py
- ORGANS/IMPERIAL_IDE/STATION/json_viewer.py
- ORGANS/IMPERIAL_IDE/STATION/path_actions.py
- ORGANS/IMPERIAL_IDE/STATION/taskpack_manager.py
- ORGANS/IMPERIAL_IDE/STATION/taskpack_manager.schema.json
- ORGANS/IMPERIAL_IDE/STATION/launch_card_viewer.py
- ORGANS/IMPERIAL_IDE/STATION/handoff_card_viewer.py
- ORGANS/IMPERIAL_IDE/STATION/reports_browser.py
- ORGANS/IMPERIAL_IDE/STATION/receipts_browser.py
- ORGANS/IMPERIAL_IDE/STATION/dirty_classifier.py
- ORGANS/IMPERIAL_IDE/STATION/dirty_classifier.schema.json
- ORGANS/IMPERIAL_IDE/STATION/safety_center.py
- ORGANS/IMPERIAL_IDE/STATION/safety_center_2.schema.json
- ORGANS/IMPERIAL_IDE/STATION/live_registration_promoter.py
- ORGANS/IMPERIAL_IDE/STATION/live_registration_promotion.schema.json

UI updates:

- ORGANS/IMPERIAL_IDE/WORKBENCH/TUI/imperial_tui.py
- ORGANS/IMPERIAL_IDE/WORKBENCH/GUI/imperial_gui_workbench.py or equivalent GUI panel files
- ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py or safe command adapters

Docs:

- ORGANS/IMPERIAL_IDE/DOCS/OPERATIONAL_STATION_UX_GUIDE_RU.md
- ORGANS/IMPERIAL_IDE/DOCS/TASKPACK_MANAGER_RUNBOOK.md
- ORGANS/IMPERIAL_IDE/DOCS/AGENT_ROSTER_OPERATOR_GUIDE_RU.md
- ORGANS/IMPERIAL_IDE/DOCS/DIRTY_CLASSIFIER_POLICY.md
- ORGANS/IMPERIAL_IDE/DOCS/LIVE_REGISTRATION_PROMOTION_RUNBOOK.md
- ORGANS/IMPERIAL_IDE/DOCS/SAFETY_CENTER_2_RUNBOOK.md

## Required report outputs

- preflight_current_state_receipt.json
- ux_summary_json_viewer_receipt.json
- agent_roster_primary_view_receipt.json
- legacy_capsule_deprecation_receipt.json
- taskpack_manager_receipt.json
- launch_handoff_card_viewer_receipt.json
- reports_browser_receipt.json
- receipts_browser_receipt.json
- dirty_classifier_receipt.json
- safety_center_2_receipt.json
- live_registration_promotion_receipt.json
- lifecycle_ui_receipt.json
- git_closure_dirty_classification_receipt.json
- tui_ux_hardening_receipt.json
- gui_ux_hardening_receipt.json
- cli_aliases_receipt.json
- station_ux_smoke_receipt.json
- validation_receipt.json
- git_diff_scope_receipt.json
- git_commit_push_receipt.json
- continuity_pack.json
- FINAL_OWNER_SUMMARY_RU.md

## Required key receipt fields

dirty_classifier_receipt.json must include task_id, dirty_count, classified_items, known_zip_1_classification, known_zip_2_classification, secrets_detected, runtime_artifacts_detected, stage_candidates, quarantine_candidates, push_allowed_state, recommended_action, timestamp.

taskpack_manager_receipt.json must include task_id, generated_taskpacks_found, latest_taskpack_path, latest_taskpack_sha256, extracted_root_files_found, validation_status, dry_run_registration_status, open_or_copy_actions_available, timestamp.

agent_roster_primary_view_receipt.json must include task_id, agent_count, servitor_prime_present, required_servitors_present, legacy_alpha_beta_gamma_primary_view_removed, tui_roster_status, gui_roster_status, cli_roster_status, timestamp.

safety_center_2_receipt.json must include task_id, real_servitor_execution_enabled, live_llm_backend_enabled, unsafe_shell_available, arbitrary_shell_allowed, dry_run_default, live_registration_scope, push_gate_state, dirty_state, remote_contours_enabled, destructive_cleanup_enabled, result, timestamp.

live_registration_promotion_receipt.json must include task_id, dry_run_default, promotion_screen_available, explicit_owner_confirmation_required, current_expected_task_impact_visible, automatic_live_promotion_run, blockers, result, timestamp.

## Final owner summary

FINAL_OWNER_SUMMARY_RU.md is Russian owner-facing output and must be short.

It must state what was improved in TUI and GUI, whether real 12-agent roster is visible, how to use Taskpack Manager, how to open full JSON, how to copy/open paths, how to use Launch Card and Handoff Card, how dirty files are classified, what remains gated, whether push completed, and next recommended task.

It must not claim full IDE completion, real servitor execution, unrestricted tool execution, or live LLM backend enabled.
