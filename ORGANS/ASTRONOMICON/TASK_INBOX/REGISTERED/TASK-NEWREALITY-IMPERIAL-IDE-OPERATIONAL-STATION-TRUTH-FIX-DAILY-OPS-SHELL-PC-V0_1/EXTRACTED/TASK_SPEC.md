# TASK SPEC

## Task ID

TASK-NEWREALITY-IMPERIAL-IDE-OPERATIONAL-STATION-TRUTH-FIX-DAILY-OPS-SHELL-PC-V0_1

## Mode

CONTROLLED_WRITE_WITH_VALIDATED_PUSH.

PC only.

This task combines a truth fix with a large advance toward a daily operational form.

## Situation

The Operational Station now exists and has useful components:

- expanded Workbench TUI;
- CLI command palette;
- 12-agent registry backend;
- taskpack manager;
- launch card and handoff card;
- lifecycle;
- safety center;
- dirty classifier;
- live registration promotion availability.

However, the latest smoke revealed critical operator-truth problems:

- TUI still visually displays legacy Alpha/Beta/Gamma while claiming the real 12-servitor roster is primary;
- read-only inspection commands modify tracked report receipt files and increase dirty_count;
- command palette output must be verified for structural integrity around taskpack-copy-path and handoff-card;
- several TUI screens still rely on truncated JSON as the primary output;
- Git Closure classifies dirt but does not yet provide enough exact action guidance for daily use.

## Mission

Fix truth and cleanliness first, then advance the station into a daily operations shell.

The Owner should be able to open Imperial IDE and perform the normal operating loop:

Open station
-> see truthful dashboard
-> see real 12-servitor roster
-> create or select task
-> inspect generated taskpacks
-> validate taskpack
-> dry-run register
-> review live registration promotion
-> view launch card
-> view handoff card
-> monitor lifecycle
-> browse reports and receipts
-> inspect dirty state and git closure
-> know the next recommended action.

Do not enable real servitor execution.
Do not enable live LLM backend.
Do not enable unsafe shell.
Do not enable remote VM2 or VM3.
Do not run automatic live registration promotion.

## Phase A: preflight and repro

Required:

- Resolve repo root.
- Record git status, HEAD, origin/master.
- Record current dirty paths.
- Run or inspect help command and validate command_palette.json.
- Reproduce or inspect read-only dirty behavior for safe read-only commands.
- Confirm whether agents, taskpack-manager, safety, git-closure, station, show-summary, and full-json write to tracked files.
- Confirm TUI Agents panel still shows Alpha/Beta/Gamma or record if already fixed.
- Confirm the real agent registry has 12 agents.
- Confirm generated taskpacks are present.
- Confirm runtime receipt and report receipt paths.
- Confirm VM2 and VM3 are out of scope.

Stop with BLOCK if the TUI cannot be found.

## Phase B: read-only no-dirty discipline

Create or update station policy:

- ORGANS/IMPERIAL_IDE/STATION/read_only_policy.py
- ORGANS/IMPERIAL_IDE/STATION/runtime_receipt_policy.py
- ORGANS/IMPERIAL_IDE/STATION/no_dirty_guard.py
- ORGANS/IMPERIAL_IDE/STATION/read_only_policy.schema.json

Required rules:

- read-only commands must not modify tracked repository files;
- read-only commands may print receipts to stdout;
- read-only commands may write optional runtime receipts only under ignored runtime paths;
- local smoke commands may write report receipts only when explicitly invoked as smoke or validation;
- post-push inspection must not rewrite committed report receipts;
- command receipts must include mutates_repo true or false;
- commands that mutate tracked reports must not be labelled LOW_READ_ONLY.

Commands that must be no-dirty:

- help;
- station;
- agents;
- agent-status;
- taskpack-manager;
- dirty-classifier;
- safety;
- git-closure;
- reports-latest;
- receipts-latest;
- show-summary;
- full-json;
- launch-card view;
- handoff-card view.

Allowed mutation:

- explicit smoke commands;
- explicit validation commands;
- explicit task build commands;
- explicit registration commands;
- explicit report finalization commands.

Required test:

- capture git status before;
- run the read-only command set;
- capture git status after;
- prove no new tracked modifications appear.

## Phase C: command palette integrity fix

Validate and repair if needed:

- ORGANS/IMPERIAL_IDE/SHELL/command_palette.json
- ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py

Required:

- command_palette.json parses;
- all command entries have command, description, risk_class, argument_required, real_execution;
- help output is valid JSON;
- no missing delimiter around taskpack-copy-path and handoff-card;
- each declared command maps to a handler or structured BLOCKED response;
- command names are stable;
- risk classes match mutation behavior.

Required receipt:

- command_palette_integrity_receipt.json.

## Phase D: TUI real roster truth fix

Upgrade Workbench TUI:

- ORGANS/IMPERIAL_IDE/WORKBENCH/TUI/imperial_tui.py

Required:

- Agents and Servitors screen uses the real 12-agent registry as the primary view;
- legacy Alpha/Beta/Gamma is removed from primary view;
- legacy capsule state may exist only under a clearly labelled Legacy Capsule Debug screen;
- screen shows status, owner organ, execution mode, handoff mode, current task, allowed actions, blocked actions;
- Servitor Prime is shown as EXTERNAL_HANDOFF_ONLY or equivalent;
- real execution remains gated.

Required proof:

- TUI smoke output or screenshot-equivalent receipt lists all 12 servitors;
- no primary roster screen shows only Alpha/Beta/Gamma.

## Phase E: summary-first TUI and full view

Improve summary display for core screens.

Required screens:

- Dashboard;
- Taskpack Manager;
- Taskpack Inspect;
- Launch Card;
- Handoff Card;
- Agents and Servitors;
- Reports;
- Receipts;
- Dirty Classifier;
- Safety Center;
- Lifecycle;
- Git Closure.

Each screen must provide:

- human summary;
- key fields;
- next action;
- raw JSON available through Full JSON or CLI command;
- path actions where relevant;
- no truncated JSON as the only useful output.

Truncated JSON may remain as a secondary preview only if it points to a working full view.

## Phase F: daily operations shell

Create or update:

- ORGANS/IMPERIAL_IDE/STATION/daily_ops_shell.py
- ORGANS/IMPERIAL_IDE/STATION/daily_ops_state.py
- ORGANS/IMPERIAL_IDE/STATION/operator_next_action.py
- ORGANS/IMPERIAL_IDE/STATION/daily_ops.schema.json

Daily Operations shell must show:

- system truth;
- current task;
- current expected task;
- real agent roster summary;
- latest generated taskpack;
- latest launch card;
- latest handoff card;
- lifecycle state;
- safety state;
- dirty state;
- git closure;
- next recommended action.

Daily Operations workflow must include:

- start day;
- inspect system;
- create task;
- build taskpack;
- validate;
- dry-run register;
- review promotion;
- copy launch or handoff card;
- watch lifecycle;
- inspect reports and receipts;
- close task;
- prepare next task.

TUI should expose this as Dashboard or Daily Ops.

CLI commands:

- daily-ops;
- next-action;
- operator-board;
- task-flow;
- task-flow-smoke.

## Phase G: Taskpack Manager advancement

Improve Taskpack Manager.

Required:

- list generated taskpacks with status;
- show latest by default;
- inspect selected taskpack;
- validate selected taskpack;
- show ZIP path;
- show SHA256;
- show extracted root files;
- show dry-run receipt;
- show live promotion availability;
- show open folder command;
- show copy path command;
- show handoff link to Launch Card.

If TUI cannot support selection yet, provide index numbers and copy-ready CLI commands.

## Phase H: Live Registration Promotion review only

Improve live registration promotion without auto-running it.

Required:

- show dry-run admitted state;
- show candidate versus canon state;
- show current expected task impact;
- show taskpack path;
- show safety checks;
- show dirty state checks;
- require explicit Owner confirmation;
- default to cancel;
- no automatic live promotion in smoke;
- produce review receipt.

States:

- REVIEW_AVAILABLE;
- REVIEW_BLOCKED;
- CONFIRMATION_REQUIRED;
- LIVE_NOT_RUN;
- LIVE_REGISTERED only if Owner explicitly typed LIVE in manual run.

## Phase I: Git Closure and Dirty Classifier v2

Improve:

- ORGANS/IMPERIAL_IDE/STATION/dirty_classifier.py
- ORGANS/IMPERIAL_IDE/STATION/git_closure.py or equivalent

Required classifications:

- current task report artifact;
- current task post-push inspection artifact;
- old unrelated report ZIP;
- runtime receipt;
- generated taskpack runtime;
- local config;
- secret risk;
- safe stage candidate;
- keep unstaged;
- quarantine candidate;
- owner-decision-needed.

Required Git Closure output:

- exact dirty_count;
- table of classified dirty paths;
- push_allowed_state;
- exact recommended commands;
- what not to stage;
- what can be staged after validation;
- whether read-only commands caused new dirt.

Do not delete or quarantine files in this task unless the Owner explicitly provided a batch approval.

## Phase J: operator documentation

Create docs:

- ORGANS/IMPERIAL_IDE/DOCS/DAILY_OPERATIONS_SHELL_GUIDE_RU.md
- ORGANS/IMPERIAL_IDE/DOCS/READ_ONLY_NO_DIRTY_POLICY.md
- ORGANS/IMPERIAL_IDE/DOCS/REAL_SERVITOR_ROSTER_TUI_GUIDE_RU.md
- ORGANS/IMPERIAL_IDE/DOCS/LIVE_PROMOTION_REVIEW_GUIDE_RU.md
- ORGANS/IMPERIAL_IDE/DOCS/GIT_DIRTY_ACTIONS_GUIDE_RU.md

Owner-facing Russian docs are allowed through Officio Agentis.

## Phase K: validation and smoke

Required smoke:

- Python compile for created or modified Python files;
- JSON parse for created or modified JSON files;
- command palette integrity smoke;
- help output valid JSON smoke;
- read-only no-dirty smoke;
- TUI real roster smoke;
- daily ops shell smoke;
- taskpack manager smoke;
- launch and handoff card smoke;
- live registration promotion review smoke without auto-live;
- dirty classifier v2 smoke;
- git closure action planner smoke;
- safety center smoke;
- GUI structural smoke;
- final station smoke.

## Phase L: reports

Create under:

REPORTS/TASK-NEWREALITY-IMPERIAL-IDE-OPERATIONAL-STATION-TRUTH-FIX-DAILY-OPS-SHELL-PC-V0_1/

Required reports:

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

## Phase M: commit and push

Commit and validated push are required for success.

Required:

- commit includes task ID;
- push to origin/master;
- post-push HEAD equals origin/master;
- final git status recorded;
- any remaining dirty files classified;
- no unclassified dirty files;
- no read-only command dirty after final smoke.

## Stop conditions

Stop with BLOCK if:

- Workbench TUI cannot be found;
- no-dirty read-only discipline cannot be enforced;
- command palette is invalid and cannot be repaired;
- real agent registry cannot be parsed and cannot be repaired;
- TUI roster cannot be fixed without replacing the liked TUI;
- unsafe shell or real servitor execution is required;
- live registration must be auto-run to pass;
- secrets or local configs would be staged;
- runtime artifacts would be staged;
- JSON validation fails and cannot be repaired;
- Python validation fails and cannot be repaired;
- push is rejected and cannot be safely resolved.
