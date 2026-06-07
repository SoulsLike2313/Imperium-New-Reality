# TASK SPEC

## Task ID

TASK-NEWREALITY-IMPERIAL-IDE-OPERATIONAL-STATION-UX-HARDENING-AGENT-ROSTER-DIRTY-CLASSIFIER-PC-V0_1

## Mode

CONTROLLED_WRITE_WITH_VALIDATED_PUSH.

This task is PC only.

This task hardens the current Operational Station MVP into a practical daily-use operator interface.

The Owner already verified a smoke flow through the Workbench TUI: Task Console, Build Taskpack, Dry-run Register Taskpack, Launch Card, Agents and Servitors, Safety, Git Closure, Reports, and Receipts.

The flow works, but daily-use UX is not yet good enough. The station still shows truncated JSON, legacy Alpha/Beta/Gamma capsules, weak reports and receipts browsing, and unclassified dirty files.

Do not enable real servitor execution. Do not enable live LLM backend. Do not enable unsafe shell. Do not enable remote VM2 or VM3 routing.

## Mission

Deliver quality operationality.

The Owner must be able to operate from inside Imperial IDE without manually hunting for paths, JSON fragments, taskpack ZIPs, or receipt files.

The station must show human summaries first, raw JSON on demand, full paths on demand, copy and open actions, the real 12-servitor agent roster, generated taskpack manager, launch and handoff cards, dirty state classifier, safety center 2.0, lifecycle tracker UI, and live registration promotion flow.

## Phase A: preflight and current-state capture

Required:

- Resolve current git root.
- Record git status.
- Record HEAD and origin/master.
- Confirm HEAD equals origin/master or record exact state.
- Confirm Workbench TUI exists.
- Confirm Workbench GUI exists.
- Confirm Station layer exists.
- Confirm OPS exists.
- Confirm agent registry exists and currently has 12 agents or record exact blocker.
- Confirm generated taskpacks folder exists.
- Confirm station runtime receipts folder exists.
- Locate current smoke taskpack from STATION-SMOKE-FIRST-OWNER-FLOW if present.
- Record current dirty files and classify the two known untracked ZIPs.
- Confirm VM2 and VM3 are out of scope.

Stop if Workbench TUI cannot be found.

## Phase B: human summary renderer and full JSON viewer

Create or update:

- ORGANS/IMPERIAL_IDE/STATION/summary_renderer.py
- ORGANS/IMPERIAL_IDE/STATION/json_viewer.py
- ORGANS/IMPERIAL_IDE/STATION/path_actions.py

Required behavior:

- Every TUI/GUI station screen shows a human summary before raw JSON.
- Raw JSON can be opened in a full viewer.
- Large JSON is not truncated as the only output.
- TUI can show truncated preview plus a clear action to open full JSON.
- CLI can print full JSON.
- Paths can be copied or opened through safe platform commands or printed as copy-ready commands if direct open is unsafe.
- No arbitrary shell is enabled.

Required shell commands or aliases:

- show-json
- open-path
- copy-path
- show-summary

If clipboard/open actions are not safe or not available, provide copy-ready commands instead of silently failing.

## Phase C: real agent roster primary view

Replace the legacy Alpha/Beta/Gamma primary display with the real agent registry.

Do not delete the legacy candidate capsule state unless it is clearly deprecated and preserved as legacy.

Required TUI view:

Agents and Servitors must show all required servitors from MANIFEST.required_servitor_roster.

Each row must show:

- servitor name;
- owner organ;
- status;
- execution mode;
- handoff mode;
- current task;
- allowed actions summary;
- blocked actions summary;
- last receipt if available.

Required GUI view:

Workbench GUI must show the same roster as an Agent Roster or Servitor Matrix panel.

Required CLI:

- agents;
- agent-status;
- agent-detail <agent_id> or equivalent.

Required receipts:

- agent_roster_primary_view_receipt.json;
- legacy_capsule_deprecation_receipt.json.

## Phase D: Taskpack Manager

Create or update:

- ORGANS/IMPERIAL_IDE/STATION/taskpack_manager.py
- ORGANS/IMPERIAL_IDE/STATION/taskpack_manager.schema.json

Taskpack Manager must manage generated taskpacks under:

ORGANS/IMPERIAL_IDE/STATION/generated_taskpacks/

Required functions:

- list generated taskpacks;
- inspect one generated taskpack;
- show TASKPACK.zip path;
- show extracted root files;
- show SHA256;
- validate taskpack;
- show admission dry-run status if receipt exists;
- dry-run register taskpack;
- prepare live registration promotion;
- open folder or print copy-ready open command;
- copy ZIP path or print copy-ready path;
- archive old generated taskpacks through safe non-destructive move only if owner-approved in a future task.

Do not delete generated taskpacks in this task.

Required CLI commands or aliases:

- taskpacks;
- taskpack-list;
- taskpack-inspect;
- taskpack-validate;
- taskpack-open;
- taskpack-copy-path.

## Phase E: Launch Card and Handoff Card viewer

Create or update:

- ORGANS/IMPERIAL_IDE/STATION/launch_card_viewer.py
- ORGANS/IMPERIAL_IDE/STATION/handoff_card_viewer.py

Required view:

- task_id;
- title;
- status;
- dry-run or live status;
- candidate or canon status;
- taskpack path;
- SHA256;
- registered path;
- admission status;
- launch text;
- Servitor Prime handoff text;
- start message;
- copy-ready block.

Do not claim execution done when only handoff is ready.

## Phase F: Reports and Receipts Browser

Create or update:

- ORGANS/IMPERIAL_IDE/STATION/reports_browser.py
- ORGANS/IMPERIAL_IDE/STATION/receipts_browser.py

Reports Browser must list latest reports, list by task, list by inferred status, show latest owner summaries, open or print report folder path, and show human report summary.

Receipts Browser must list latest receipts, filter by safety, validation, git, admission, resolver, launch, and lifecycle, show raw JSON through full JSON viewer, show human summary first, and provide copy/open path actions.

TUI and GUI must expose these browsers.

## Phase G: Dirty State Classifier

Create:

- ORGANS/IMPERIAL_IDE/STATION/dirty_classifier.py
- ORGANS/IMPERIAL_IDE/STATION/dirty_classifier.schema.json

Classify git dirty paths into categories:

- CANONICAL_REPORT_ARTIFACT;
- FRESH_TASK_OUTPUT_CANDIDATE;
- OLD_UNRELATED_ARTIFACT;
- RUNTIME_ARTIFACT;
- GENERATED_TASKPACK_RUNTIME;
- LOCAL_CONFIG;
- SECRET_RISK;
- STAGE_CANDIDATE;
- IGNORE_CANDIDATE;
- QUARANTINE_CANDIDATE;
- DELETE_REQUIRES_OWNER_APPROVAL;
- UNKNOWN_REVIEW_REQUIRED.

Required behavior:

- detect current dirty paths;
- classify the two known untracked ZIPs;
- never delete files;
- recommend action;
- show whether push is blocked, warning, or allowed after stage;
- write dirty_classifier_receipt.json.

Known paths to classify:

- REPORTS/TASK-NEWREALITY-IMPERIAL-IDE-OPERATIONAL-USABILITY-STATION-AGENTIC-WORKFLOW-PC-V0_2/agent_registry_receipt.zip
- REPORTS/TASK-NEWREALITY-MECHANICUS-IMPERIAL-IDE-CONTROL-SHELL-TUI-PC-V0_1/astronomicon_dashboard_integration_receipt.zip

Expected rough classification:

- fresh report ZIP from latest task: CANONICAL_REPORT_ARTIFACT or FRESH_TASK_OUTPUT_CANDIDATE;
- older unrelated ZIP: OLD_UNRELATED_ARTIFACT or QUARANTINE_CANDIDATE.

Do not stage or delete either without clear validation and receipt.

## Phase H: Safety Center 2.0

Create or update:

- ORGANS/IMPERIAL_IDE/STATION/safety_center.py
- ORGANS/IMPERIAL_IDE/STATION/safety_center_2.schema.json

Required summary fields:

- real_servitor_execution;
- live_llm_backend;
- unsafe_shell;
- arbitrary_shell;
- dry_run_default;
- live_registration;
- live_registration_scope;
- push_gate;
- dirty_state;
- secrets_state;
- runtime_state;
- remote_contours;
- destructive_cleanup;
- result.

The Safety Center must show what is allowed now, what is blocked, why it is blocked, and which future gate can open it.

## Phase I: Live Registration Promotion Flow

Create or update:

- ORGANS/IMPERIAL_IDE/STATION/live_registration_promoter.py
- ORGANS/IMPERIAL_IDE/STATION/live_registration_promotion.schema.json

Required flow:

Dry-run admitted
-> show current candidate task
-> show current Astronomicon expected task
-> show what will change
-> show safety checks
-> show scope checks
-> require explicit Owner confirmation
-> run local PC registration only
-> capture launch card
-> write promotion receipt.

Do not auto-promote any task during smoke.
Do not run live promotion unless the Owner explicitly confirms inside the UI.

Required TUI text must clearly say:

LIVE registration will replace or update current expected task.

Required states:

- PROMOTION_AVAILABLE;
- PROMOTION_BLOCKED;
- PROMOTION_CONFIRMED;
- LIVE_REGISTERED;
- LIVE_FAILED.

## Phase J: Lifecycle Tracker UI

Upgrade lifecycle presentation.

Required stages:

- INTENT_CAPTURED;
- CLASSIFIED;
- ROUTE_PREVIEWED;
- POLICY_CHECKED;
- TASKPACK_BUILT;
- TASKPACK_VALIDATED;
- DRY_RUN_REGISTERED;
- LIVE_REGISTERED;
- LAUNCH_CARD_READY;
- HANDOFF_READY;
- EXECUTION_STARTED;
- REPORT_DETECTED;
- VALIDATION_DETECTED;
- BUNDLE_GATE_CHECKED;
- GIT_CLOSURE_CHECKED;
- CLOSED_OR_BLOCKED.

Required display:

- checkmark or status per stage;
- distinguish dry-run from live;
- distinguish handoff ready from execution done;
- show next recommended action.

## Phase K: Git Closure UI with dirty classification

Update Git Closure screen.

Required:

- show branch;
- show HEAD;
- show origin/master;
- show head_equals_origin_master;
- show dirty_count;
- show classified dirty table;
- show push_allowed_state;
- show recommended action;
- show whether dirty files are old unrelated, report artifacts, runtime, secrets, or unknown.

Do not claim repository clean if untracked files remain.

## Phase L: TUI integration

Upgrade the existing Workbench TUI.

Required:

- preserve visual style;
- preserve current command menu;
- add Taskpack Manager screen or integrate actions into task screens;
- real agent roster primary view;
- full JSON viewer action;
- copy/open path actions or copy-ready commands;
- reports and receipts browser with summaries;
- dirty classifier screen;
- safety center 2.0 screen;
- live registration promotion screen;
- lifecycle UI screen.

TUI must never silently swallow errors.

## Phase M: GUI integration

Upgrade Workbench GUI.

Required panels or sections:

- Operational Dashboard summary;
- Agent Roster real registry;
- Taskpack Manager;
- Launch Card and Handoff Card;
- Reports Browser;
- Receipts Browser;
- Dirty State Classifier;
- Safety Center 2.0;
- Lifecycle Tracker;
- Git Closure with classified dirty state.

GUI structural smoke is enough if full Windows interaction cannot be automated.

## Phase N: CLI integration

Required shell aliases or commands:

- station-ux-smoke;
- taskpack-manager;
- taskpack-list;
- taskpack-inspect;
- show-json;
- show-summary;
- launch-card;
- handoff-card;
- reports-latest;
- receipts-latest;
- dirty-classifier;
- safety;
- live-registration-promote;
- agents;
- agent-status;
- lifecycle;
- git-closure.

Every command must work or return a structured BLOCKED status with reason.

## Phase O: documentation

Required docs:

- ORGANS/IMPERIAL_IDE/DOCS/OPERATIONAL_STATION_UX_GUIDE_RU.md
- ORGANS/IMPERIAL_IDE/DOCS/TASKPACK_MANAGER_RUNBOOK.md
- ORGANS/IMPERIAL_IDE/DOCS/AGENT_ROSTER_OPERATOR_GUIDE_RU.md
- ORGANS/IMPERIAL_IDE/DOCS/DIRTY_CLASSIFIER_POLICY.md
- ORGANS/IMPERIAL_IDE/DOCS/LIVE_REGISTRATION_PROMOTION_RUNBOOK.md
- ORGANS/IMPERIAL_IDE/DOCS/SAFETY_CENTER_2_RUNBOOK.md

Owner-facing Russian docs are allowed through Officio authority.

## Phase P: validation and smoke

Required smoke tests:

- Python compile for created or modified Python files;
- JSON parse for created or modified JSON files;
- Workbench TUI smoke;
- Workbench GUI structural smoke;
- agent roster real-view smoke;
- taskpack manager list and inspect smoke;
- generated taskpack validation smoke;
- launch card viewer smoke;
- handoff card viewer smoke;
- reports browser smoke;
- receipts browser smoke;
- dirty classifier smoke with current dirty files;
- safety center 2.0 smoke;
- live registration promotion availability smoke without automatic live promotion;
- lifecycle UI smoke;
- git closure classification smoke.

## Phase Q: reports

Create reports under:

REPORTS/TASK-NEWREALITY-IMPERIAL-IDE-OPERATIONAL-STATION-UX-HARDENING-AGENT-ROSTER-DIRTY-CLASSIFIER-PC-V0_1/

Required reports:

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

## Phase R: validation and push

Required:

- all JSON parses;
- all Python compiles;
- no unsafe execution enabled;
- no live LLM enabled;
- no VM2 or VM3 action;
- no destructive cleanup;
- no secrets or local configs staged;
- runtime artifacts not staged;
- git diff inside allowed_write_scope;
- commit includes task ID;
- push completes;
- post-push HEAD equals origin/master.

## Stop conditions

Stop with BLOCK if:

- Workbench TUI cannot be found;
- updating TUI would destroy the existing liked interface;
- agent registry cannot be parsed and cannot be repaired;
- taskpack manager cannot find generated taskpacks and cannot provide a structured blocker;
- dirty classifier cannot safely classify current dirty state;
- live registration promotion would require unsafe execution;
- unsafe shell or real servitor execution is required;
- live LLM secrets are required;
- secrets or local configs would be staged;
- runtime directory would be staged;
- JSON validation fails and cannot be repaired;
- Python validation fails and cannot be repaired;
- push is rejected and cannot be safely resolved.
