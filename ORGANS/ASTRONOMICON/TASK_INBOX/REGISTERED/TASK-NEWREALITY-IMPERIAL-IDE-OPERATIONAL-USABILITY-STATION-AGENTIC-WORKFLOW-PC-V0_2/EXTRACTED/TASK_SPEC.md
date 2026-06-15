# TASK SPEC

## Task ID

TASK-NEWREALITY-IMPERIAL-IDE-OPERATIONAL-USABILITY-STATION-AGENTIC-WORKFLOW-PC-V0_2

## Mode

CONTROLLED_WRITE_WITH_VALIDATED_PUSH.

This task is PC only.

This task must move Imperial IDE from working parts into an operational UI/UX-friendly station.

The Owner wants to use the system from inside the system.

The existing Workbench TUI that the Owner liked must be preserved and upgraded. Do not replace it with a weaker disconnected TUI.

The station must make task creation, taskpack generation, Astronomicon registration, launch cards, agent visibility, lifecycle tracking, receipts, reports, safety state, and git closure visible and usable.

Real servitor execution, live LLM backend, and unrestricted shell remain gated unless a future task explicitly opens them.

## Strategic target

Create an operational station based on the script-first AI MetaOS kernel:

Owner intent
-> Task Console
-> MetaOS route preview
-> Mechanicus policy check
-> Taskpack Builder
-> Astronomicon local registration gate
-> Launch Card
-> Servitor Prime handoff or future execution gate
-> WARP session if needed
-> Administratum bundle gate
-> Inquisition validation
-> Reports and receipts
-> Git closure
-> Next task recommendation

## Phase A: preflight

Required:

- Resolve current git root.
- Record git status.
- Record HEAD and origin/master.
- Confirm HEAD equals origin/master or record exact state.
- Confirm Governance is CANON_ACTIVE.
- Confirm Workbench GUI opens structurally or record exact blocker.
- Confirm Workbench TUI exists and identify its current command surface.
- Confirm OPS exists and can run smoke or record exact blocker.
- Confirm WARP and MetaOS integration statuses.
- Confirm Mechanicus command policy exists.
- Confirm Astronomicon task inbox and registration skill path if available.
- Confirm no local route config, runtime directory, secret, or deleted old artifact is staged.
- Confirm VM2 and VM3 are out of scope.

Stop if the current Workbench TUI cannot be found.

## Phase B: station architecture

Create or update a station layer:

ORGANS/IMPERIAL_IDE/STATION/

Required files:

- ORGANS/IMPERIAL_IDE/STATION/README.md
- ORGANS/IMPERIAL_IDE/STATION/station_state.py
- ORGANS/IMPERIAL_IDE/STATION/station_router.py
- ORGANS/IMPERIAL_IDE/STATION/station_receipts.py
- ORGANS/IMPERIAL_IDE/STATION/station_workflow.py
- ORGANS/IMPERIAL_IDE/STATION/station_panels.json
- ORGANS/IMPERIAL_IDE/STATION/operational_state.schema.json
- ORGANS/IMPERIAL_IDE/STATION/RUN_FIRST_RU.md

The station state model must represent repo state, task state, agent state, safety state, OPS state, WARP state, MetaOS state, Mechanicus state, Astronomicon state, report and receipt state, and git closure state.

All states must be honest and typed: LIVE, DRY_RUN, BLOCKED, CANDIDATE, ACTIVE, WARNING, FAILED, or UNKNOWN.

## Phase C: unified TUI upgrade

Upgrade the existing Workbench TUI as the primary operational TUI.

Target file:

ORGANS/IMPERIAL_IDE/WORKBENCH/TUI/imperial_tui.py

The upgraded TUI must keep the current visual style and add operational menus.

Required main menu:

- Dashboard;
- Task Console;
- Task Templates;
- Build Taskpack;
- Register Taskpack;
- Launch Card;
- Agents and Servitors;
- Astronomicon;
- Mechanicus;
- WARP;
- MetaOS;
- Reports;
- Receipts;
- Safety;
- Git Closure;
- Settings;
- Quit.

Required TUI actions:

- show system truth dashboard;
- create a task intent;
- classify task intent through OPS or structured fallback;
- build Astronomicon-compatible taskpack;
- run safe registration precheck;
- live register a safe generated taskpack if gates pass;
- show launch card;
- show Servitor Prime handoff message;
- show all organ servitors;
- show active and latest tasks;
- show latest reports and receipts;
- show safety state;
- show git closure state.

If a function remains blocked, the TUI must show BLOCKED with reason, not fail silently.

## Phase D: Workbench GUI operational panels

Upgrade the Workbench GUI as the visual operational station.

Target file:

ORGANS/IMPERIAL_IDE/WORKBENCH/GUI/imperial_gui_workbench.py

Required GUI panels or equivalent UI sections:

- Operational Dashboard;
- Task Console;
- Taskpack Builder;
- Live Registration Gate;
- Launch Card;
- Agent Roster;
- Servitor Matrix;
- Task Lifecycle;
- Reports Browser;
- Receipts Browser;
- Safety Center;
- Git Closure;
- WARP Workspace;
- MetaOS Router;
- Mechanicus Tools;
- Settings.

Required GUI behavior:

- preserve existing organ panels and style;
- display LIVE REPO state;
- display current HEAD and origin/master if available;
- display current task and latest report if available;
- allow task intent entry;
- allow template selection;
- allow build taskpack action;
- allow safe registration action or show blocker;
- show launch card text with copy-ready content;
- show Servitor Prime handoff text;
- show organ servitors and statuses;
- show task lifecycle progress stages.

If implementing all GUI buttons is too risky, create read-only panels with wired CLI commands and clear next action instructions, but do not fake interactive success.

## Phase E: agent and servitor registry

Create a first-class agent registry.

Required files:

- ORGANS/IMPERIAL_IDE/AGENTS/README.md
- ORGANS/IMPERIAL_IDE/AGENTS/agent_registry.json
- ORGANS/IMPERIAL_IDE/AGENTS/servitor_roster.json
- ORGANS/IMPERIAL_IDE/AGENTS/agent_card.schema.json
- ORGANS/IMPERIAL_IDE/AGENTS/agent_status.schema.json
- ORGANS/IMPERIAL_IDE/AGENTS/agent_runtime_state.json

Required agent concepts:

- Servitor Prime is the LLM servitor and external handoff target until live backend is opened.
- Servitor Mechanicus represents Mechanicus tool and validation work.
- Servitor Administratum represents receipts, bundle gates, continuity, and reports.
- Servitor Astronomicon represents task entry, registry, and launch cards.
- Servitor Inquisition represents safety, fake-green, and risk gates.
- Servitor Strategium represents planning and sequencing.
- Servitor Doctrinarium represents canon and doctrine.
- Servitor Officio Agentis represents owner-facing communication.
- Servitor Schola Imperialis represents lessons and training.
- Servitor WARP represents WARP sessions.
- Servitor MetaOS represents route preview and orchestration.

Each agent record must include agent_id, display_name, servitor_name, owner_organ, role, capabilities, allowed_actions, blocked_actions, status, current_task_id, last_receipt_path, risk_class, execution_mode, and handoff_mode.

## Phase F: task console and taskpack builder usability

Wire OPS into the station.

Required:

- OPS templates remain available.
- Task Console uses templates.
- Taskpack Builder generates Astronomicon-compatible taskpacks.
- Generated taskpacks include the six required root files.
- Generated taskpacks pass JSON and language gate.
- Generated taskpacks have SHA256 receipt.
- Generated taskpacks are stored under an ignored runtime or controlled output path unless registered.

Required station actions:

- new task;
- edit task intent;
- select template;
- preview route;
- preview scope;
- build taskpack;
- validate taskpack;
- register taskpack;
- show launch card;
- show handoff prompt.

## Phase G: live Astronomicon registration gate

Enable safe live local registration from inside the station for generated taskpacks only.

Conditions:

- generated taskpack validates;
- language gate passes;
- required root files present;
- source path is inside allowed generated taskpack output or selected by Owner;
- no secrets;
- no unsafe scope;
- Astronomicon registration skill path is found;
- registration command is local PC only;
- receipt is written.

Required behavior:

- dry-run registration remains default;
- live registration requires explicit station action;
- live registration emits receipt;
- launch card is captured and displayed;
- failure shows exact blocker.

Do not enable remote contour registration.

## Phase H: lifecycle tracker

Create task lifecycle tracking.

Required stages:

- INTENT_CAPTURED;
- CLASSIFIED;
- ROUTE_PREVIEWED;
- POLICY_CHECKED;
- TASKPACK_BUILT;
- TASKPACK_VALIDATED;
- REGISTERED;
- LAUNCH_CARD_READY;
- HANDOFF_READY;
- EXECUTION_PENDING;
- REPORT_DETECTED;
- VALIDATION_DETECTED;
- BUNDLE_GATE_CHECKED;
- GIT_CLOSURE_CHECKED;
- CLOSED_OR_BLOCKED.

Create files:

- ORGANS/IMPERIAL_IDE/STATION/lifecycle_tracker.py
- ORGANS/IMPERIAL_IDE/STATION/lifecycle_stage.schema.json
- ORGANS/IMPERIAL_IDE/STATION/lifecycle_state.json

The lifecycle tracker must not claim execution when only handoff is ready.

## Phase I: reports, receipts, and git closure

The station must show reports and receipts.

Required behavior:

- list latest reports;
- list latest owner summaries;
- list latest safety receipts;
- list latest git push receipts;
- show report folder for current task;
- detect PASS, PASS_WITH_WARNINGS, BLOCKED;
- show old unstaged unrelated files as warning only;
- show git status, HEAD, origin/master;
- show whether push is allowed;
- show closure receipts.

Add or update GUI/TUI panels and shell commands as needed.

## Phase J: shell command integration

Update Imperial IDE shell commands.

Required commands or aliases:

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

Every command must work or return structured BLOCKED status.

## Phase K: safety center

Create a clear Safety Center.

Required status fields:

- real_servitor_execution_enabled;
- live_llm_backend_enabled;
- unsafe_shell_available;
- arbitrary_shell_allowed;
- dry_run_default;
- live_registration_enabled;
- live_registration_scope;
- unknown_tool_blocked;
- secrets_staged;
- runtime_paths_staged;
- vm2_action;
- vm3_action;
- destructive_cleanup;
- push_allowed_state;
- result.

Safety Center must be visible from GUI and TUI.

## Phase L: documentation and owner workflow

Required docs:

- ORGANS/IMPERIAL_IDE/DOCS/OPERATIONAL_STATION_USER_GUIDE_RU.md
- ORGANS/IMPERIAL_IDE/DOCS/OPERATIONAL_STATION_WORKFLOW.md
- ORGANS/IMPERIAL_IDE/DOCS/AGENTS_AND_SERVITORS_MODEL.md
- ORGANS/IMPERIAL_IDE/DOCS/LIVE_REGISTRATION_GATE_RUNBOOK.md
- ORGANS/IMPERIAL_IDE/DOCS/NEXT_REAL_EXECUTION_GATE_PLAN.md

The guide must include exact commands to open GUI, open TUI, create task, build taskpack, register taskpack, copy launch card, view agents, view reports, view receipts, view safety, and view git closure.

## Phase M: smoke and validation

Required smoke:

- Python compile for created or modified Python files.
- JSON parse for created or modified JSON files.
- Workbench TUI station smoke.
- Workbench GUI structural smoke.
- Station CLI smoke.
- Agent registry validation.
- Generated taskpack smoke.
- Registration dry-run smoke.
- If safe, live local registration smoke with a clearly marked smoke task.
- Launch card capture smoke.
- Lifecycle tracker smoke.
- Report browser smoke.
- Receipt browser smoke.
- Safety center smoke.
- Git closure smoke.

The task may pass with warnings if GUI interaction requires manual Windows confirmation, but must record the blocker.

## Phase N: reports

Create reports under:

REPORTS/TASK-NEWREALITY-IMPERIAL-IDE-OPERATIONAL-USABILITY-STATION-AGENTIC-WORKFLOW-PC-V0_2/

Required reports:

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

## Phase O: validation

Required validation:

- all created or modified JSON files parse;
- all created or modified Python files compile;
- Workbench TUI still opens or exact blocker is recorded;
- Workbench TUI contains operational menus;
- Workbench GUI still opens structurally or exact blocker is recorded;
- agent registry validates against schema;
- taskpack builder creates a valid Astronomicon-compatible taskpack;
- registration gate writes receipt;
- real execution remains gated;
- live LLM remains disabled;
- unsafe shell remains blocked;
- no VM2 or VM3 actions;
- no runtime directories staged;
- no local route configs or secrets staged;
- git diff inside allowed_write_scope.

## Phase P: commit and validated push

Commit and push are required for PASS.

Commit message must include:

TASK-NEWREALITY-IMPERIAL-IDE-OPERATIONAL-USABILITY-STATION-AGENTIC-WORKFLOW-PC-V0_2

After push, record commit SHA, origin/master SHA, git status, pushed files summary, and post-push equality of HEAD and origin/master.

## Stop conditions

Stop with BLOCK if:

- Workbench TUI cannot be found;
- updating TUI would destroy the existing liked interface;
- OPS taskpack builder cannot be called or repaired;
- safe registration gate cannot be implemented without unsafe execution;
- unsafe shell or real servitor execution is required to pass;
- live LLM secrets are required;
- secrets or local configs would be staged;
- runtime directory would be staged;
- JSON validation fails and cannot be repaired;
- Python validation fails and cannot be repaired;
- push is rejected and cannot be safely resolved.
