# OUTPUT REQUIREMENTS

## Output root

REPORTS/TASK-NEWREALITY-IMPERIAL-IDE-OPERATIONAL-STATION-TRUTH-FIX-DAILY-OPS-SHELL-PC-V0_1/

## Required repository outputs

Station policy and guard modules:

- ORGANS/IMPERIAL_IDE/STATION/read_only_policy.py
- ORGANS/IMPERIAL_IDE/STATION/runtime_receipt_policy.py
- ORGANS/IMPERIAL_IDE/STATION/no_dirty_guard.py
- ORGANS/IMPERIAL_IDE/STATION/read_only_policy.schema.json

Daily operations modules:

- ORGANS/IMPERIAL_IDE/STATION/daily_ops_shell.py
- ORGANS/IMPERIAL_IDE/STATION/daily_ops_state.py
- ORGANS/IMPERIAL_IDE/STATION/operator_next_action.py
- ORGANS/IMPERIAL_IDE/STATION/daily_ops.schema.json

Updated modules:

- ORGANS/IMPERIAL_IDE/WORKBENCH/TUI/imperial_tui.py
- ORGANS/IMPERIAL_IDE/WORKBENCH/GUI/imperial_gui_workbench.py or equivalent GUI panel file
- ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py
- ORGANS/IMPERIAL_IDE/SHELL/command_palette.json
- ORGANS/IMPERIAL_IDE/STATION/dirty_classifier.py
- ORGANS/IMPERIAL_IDE/STATION/taskpack_manager.py
- ORGANS/IMPERIAL_IDE/STATION/live_registration_promoter.py
- ORGANS/IMPERIAL_IDE/STATION/git_closure.py or equivalent

Docs:

- ORGANS/IMPERIAL_IDE/DOCS/DAILY_OPERATIONS_SHELL_GUIDE_RU.md
- ORGANS/IMPERIAL_IDE/DOCS/READ_ONLY_NO_DIRTY_POLICY.md
- ORGANS/IMPERIAL_IDE/DOCS/REAL_SERVITOR_ROSTER_TUI_GUIDE_RU.md
- ORGANS/IMPERIAL_IDE/DOCS/LIVE_PROMOTION_REVIEW_GUIDE_RU.md
- ORGANS/IMPERIAL_IDE/DOCS/GIT_DIRTY_ACTIONS_GUIDE_RU.md

## Required report outputs

Report files under REPORTS/TASK-NEWREALITY-IMPERIAL-IDE-OPERATIONAL-STATION-TRUTH-FIX-DAILY-OPS-SHELL-PC-V0_1/:

- preflight_truth_state_receipt.json
- command_palette_integrity_receipt.json
- readonly_no_dirty_policy_receipt.json
- readonly_no_dirty_smoke_receipt.json
- runtime_receipt_policy_receipt.json
- tui_real_roster_truth_receipt.json
- summary_first_tui_receipt.json
- daily_ops_shell_receipt.json
- daily_ops_shell_smoke_receipt.json
- taskpack_manager_v2_receipt.json
- live_promotion_review_receipt.json
- dirty_classifier_v2_receipt.json
- git_closure_action_planner_receipt.json
- safety_center_truth_receipt.json
- gui_structural_smoke_receipt.json
- validation_receipt.json
- git_diff_scope_receipt.json
- git_commit_push_receipt.json
- continuity_pack.json
- FINAL_OWNER_SUMMARY_RU.md

## Required readonly_no_dirty_smoke_receipt.json fields

- task_id;
- commands_tested;
- git_status_before;
- git_status_after;
- tracked_files_modified_by_readonly_commands;
- runtime_receipts_written;
- report_receipts_written;
- pass;
- blockers;
- timestamp.

## Required tui_real_roster_truth_receipt.json fields

- task_id;
- real_servitor_count_visible;
- required_servitors_visible;
- alpha_beta_gamma_primary_view_present;
- legacy_debug_view_present;
- prime_status_visible;
- execution_gated_visible;
- pass;
- timestamp.

## Required command_palette_integrity_receipt.json fields

- task_id;
- palette_path;
- palette_json_parse;
- command_count;
- required_commands_present;
- malformed_entries;
- handler_coverage;
- help_output_valid_json;
- pass;
- timestamp.

## Required daily_ops_shell_receipt.json fields

- task_id;
- board_available;
- surfaces;
- shows_current_task;
- shows_agent_roster;
- shows_taskpack_state;
- shows_lifecycle;
- shows_safety;
- shows_dirty_state;
- shows_git_closure;
- shows_next_action;
- pass;
- timestamp.

## Required dirty_classifier_v2_receipt.json fields

- task_id;
- dirty_count;
- classified_count;
- unclassified_count;
- current_task_report_artifacts;
- old_unrelated_artifacts;
- runtime_artifacts;
- generated_taskpack_runtime;
- secret_risks;
- local_configs;
- stage_candidates;
- keep_unstaged;
- owner_decision_needed;
- recommended_commands;
- push_allowed_state;
- timestamp.

## Final owner summary

FINAL_OWNER_SUMMARY_RU.md is Russian owner-facing output and must be short.

It must state:

- whether read-only commands are now no-dirty;
- whether TUI shows the real 12-servitor roster;
- whether command palette was valid or repaired;
- how to open daily operations shell;
- how to use next-action board;
- how to inspect taskpacks;
- how to review live registration promotion;
- how dirty state is now handled;
- what remains gated;
- whether push completed;
- next recommended task.

It must not claim full IDE completion.
It must not claim real servitor execution.
It must not claim unrestricted tool execution.
It must not claim live LLM backend is enabled.
