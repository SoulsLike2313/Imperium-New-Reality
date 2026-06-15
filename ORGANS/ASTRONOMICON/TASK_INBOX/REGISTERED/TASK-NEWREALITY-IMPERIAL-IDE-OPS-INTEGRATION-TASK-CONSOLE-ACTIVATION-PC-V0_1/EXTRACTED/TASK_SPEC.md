# TASK SPEC

## Task ID

TASK-NEWREALITY-IMPERIAL-IDE-OPS-INTEGRATION-TASK-CONSOLE-ACTIVATION-PC-V0_1

## Mode

CONTROLLED_WRITE_WITH_VALIDATED_PUSH.

This task is PC only.

This task integrates the bundled IMPERIUM_IDE_OPERATIONAL_V0_1 candidate engine into the current Imperial IDE and activates the operational Task Console path.

The Servitor must fix known bugs found during Logos Prime review.

Do not enable real servitor execution.
Do not enable unrestricted shell execution.
Do not enable a live LLM backend.
Do not claim that the whole IDE is finished.

## Bundled source archive

This taskpack includes:

SOURCE_BUNDLES/IMPERIUM_IDE_OPERATIONAL_V0_1.zip

Expected SHA256:

d156a009e39dbf91fe9eedc23c298e527683cf066234b618c72ef9fb29961d01

The Servitor must verify this archive on PC after Astronomicon extraction.

If the hash differs, stop with BLOCK unless the mismatch is fully explained and accepted by the Owner.

## Mission

Perform a careful operational integration:

1. Import OPS under ORGANS/IMPERIAL_IDE/OPS while preserving its internal ENGINE structure.
2. Patch known OPS example bugs.
3. Add Astronomicon-compatible taskpack generation mode.
4. Wire OPS into the existing Imperial IDE CLI.
5. Wire OPS into the existing Workbench and TUI as Task Console, Taskpack Builder, Registration, Launch Card, Lifecycle, and Git Closure panels.
6. Keep real execution blocked by default.
7. Validate all outputs.
8. Commit and push validated outputs.

## Phase A: preflight

Required:

- Resolve current git root.
- Record git status.
- Record HEAD and origin/master.
- Confirm HEAD equals origin/master or record exact state.
- Confirm Governance is CANON_ACTIVE.
- Confirm Imperial IDE shell exists.
- Confirm Workbench, WARP, and MetaOS integration exists.
- Confirm Mechanicus foundation exists.
- Locate bundled OPS source archive inside registered taskpack extraction.
- Record OPS archive path, size, SHA256, and inventory.
- Confirm no local route config, runtime directory, secret, or deleted old artifact is staged.
- Confirm VM2 and VM3 are out of scope.

Stop if the source archive cannot be located or verified.

## Phase B: import OPS candidate

Import source archive under:

ORGANS/IMPERIAL_IDE/OPS/

Preserve this internal structure:

- ORGANS/IMPERIAL_IDE/OPS/ENGINE/imperium_ops/
- ORGANS/IMPERIAL_IDE/OPS/CLI/
- ORGANS/IMPERIAL_IDE/OPS/TUI/
- ORGANS/IMPERIAL_IDE/OPS/TESTS/
- ORGANS/IMPERIAL_IDE/OPS/DOCS/ if present
- ORGANS/IMPERIAL_IDE/OPS/VALIDATION/ if present

Do not flatten ENGINE.

Do not place imperium_ops directly under OPS root unless imports are patched and validated.

If the source archive already has a top-level wrapper directory, strip or preserve it only in a way that produces the required OPS/ENGINE, OPS/CLI, OPS/TUI, OPS/TESTS layout.

Required receipt:

REPORTS/TASK-NEWREALITY-IMPERIAL-IDE-OPS-INTEGRATION-TASK-CONSOLE-ACTIVATION-PC-V0_1/ops_candidate_import_receipt.json

## Phase C: required bug fixes

The Servitor must inspect and patch the source.

Known required fix 1:

task_console.validate_intent currently returns only problems in the reviewed candidate, while CLI expects:

ok, problems = validate_intent(intent)

Required contract:

validate_intent(intent) returns tuple[bool, list[str]].

Expected implementation pattern:

def validate_intent(intent):
    problems = []
    ...
    return (len(problems) == 0), problems

After this fix, the CLI classify command must not crash with ValueError.

Known required fix 2:

CLI and TUI path discovery must work after repository integration.

The package must either preserve:

OPS/ENGINE/imperium_ops

or patch CLI/TUI imports so they reliably find the engine from the installed OPS root.

Required behavior:

- python ORGANS/IMPERIAL_IDE/OPS/CLI/imperial_ide_ops_cli.py smoke
- python ORGANS/IMPERIAL_IDE/OPS/TUI/imperial_ide_ops_tui.py --smoke

or equivalent commands must work, or exact blockers must be recorded.

Known required fix 3:

Taskpack builder must support current Astronomicon-compatible output.

Add or patch a mode that writes root files:

- MANIFEST.json
- TASK_SPEC.md
- ACCEPTANCE_GATES.md
- OUTPUT_REQUIREMENTS.md
- TASK_ROUTE_MANIFEST_TEMPLATE.json
- TASK_START_ACK_TEMPLATE.json

Astronomicon-compatible MANIFEST.json must include:

- schema_version: astronomicon.taskpack.v0_1
- task_id
- taskpack_id
- required_organs
- organ_route
- route_manifest_template
- task_start_ack_template
- language_and_encoding_policy.cyrillic_in_taskpack
- git_push_policy
- allowed_write_scope
- forbidden_actions

Known required fix 4:

Push policy wording must match current Imperium law.

Do not write "push forbidden" as a categorical policy.

Use:

validated push is allowed and expected after validation, scope check, secret check, and task policy.

Known required fix 5:

Dry-run registration must remain available, but live registration path must be designed.

Dry-run may write under OPS/STAGING.

Live registration must target:

ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/

only through a controlled mode and receipt.

For this task, live registration may remain gated if unsafe, but the builder and registration panel must clearly expose both modes.

## Phase D: OPS CLI activation

Add or update Imperial IDE shell commands.

Existing shell:

ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py

Required commands or aliases:

- ops
- ops-smoke
- task-console
- classify-task
- build-taskpack
- register-taskpack
- launch-card
- lifecycle
- lifecycle-smoke
- git-closure
- task-templates

Each command must either work or return structured BLOCKED status.

Required minimum command behavior:

- ops-smoke runs OPS smoke or equivalent.
- classify-task validates a TaskIntent without crashing.
- build-taskpack creates an Astronomicon-compatible taskpack in a safe staging or output directory.
- launch-card prints or writes a launch card for a built or registered task.
- lifecycle runs dry-run lifecycle only.
- git-closure shows blocked or ready state; it must not push without validation.

## Phase E: Workbench GUI wiring

Add Workbench panels or panel registry entries for OPS.

Required panels:

- Task Console
- Taskpack Builder
- Astronomicon Registration
- Launch Card
- Lifecycle
- Git Closure

If full GUI widget implementation is too risky in this task, add panel registry entries and safe action buttons that call CLI/TUI or show structured status.

Do not break existing Workbench panels.

Required outputs may include:

- ORGANS/IMPERIAL_IDE/WORKBENCH/PANELS/task_console_panel.py
- ORGANS/IMPERIAL_IDE/WORKBENCH/PANELS/taskpack_builder_panel.py
- ORGANS/IMPERIAL_IDE/WORKBENCH/PANELS/ops_lifecycle_panel.py
- ORGANS/IMPERIAL_IDE/WORKBENCH/PANELS/git_closure_panel.py

or equivalent current architecture files.

## Phase F: TUI operational activation

Update the TUI so the Owner can create a task from inside the system.

Required TUI menu entries:

- Task Console
- Task Templates
- Build Taskpack
- Register Taskpack
- Launch Card
- Lifecycle Dry Run
- Reports
- Receipts
- Git Closure
- Safety

The TUI should be usable even if GUI is not.

Required smoke:

- TUI smoke or non-interactive menu validation.

## Phase G: Task template library

Create a reusable task template library.

Required output:

ORGANS/IMPERIAL_IDE/OPS/TEMPLATES/task_templates.json

Minimum templates:

- audit
- repair
- build
- integration
- cleanup_staging
- mechanicus_tool
- ide_extension
- warp_experiment
- metaos_orchestration
- governance_update
- report_generation

Each template must include:

- template_id
- title
- default_scope
- default_risk
- default_organs
- default_allowed_write_scope
- default_forbidden_actions
- default_outputs
- push_policy

## Phase H: Astronomicon-compatible generation smoke

Required smoke:

Use OPS to generate one minimal test taskpack in a safe staging directory.

The generated taskpack must:

- contain the six required Astronomicon root files;
- parse JSON;
- include language_and_encoding_policy.cyrillic_in_taskpack;
- include required_organs;
- include organ_route;
- include validated push policy;
- have no Cyrillic in taskpack root text files;
- be zipped;
- have SHA256 recorded.

If the current Astronomicon admission skill can safely dry-run or precheck it, run precheck and record result.

Do not register a fake production task unless the task is explicitly marked smoke and placed in safe staging.

## Phase I: lifecycle dry-run

Run or implement the full dry-run lifecycle:

Owner intent
-> classification
-> MetaOS route preview
-> Mechanicus policy check
-> taskpack generation
-> Astronomicon dry-run registration
-> launch card
-> servitor handoff dry-run
-> validation
-> Administratum bundle gate
-> Inquisition fake-green check
-> owner summary
-> git closure status

Required:

- real servitor execution remains blocked;
- live LLM backend remains disabled;
- unsafe shell remains blocked;
- fake-green bare PASS is caught;
- incomplete bundle is HELD;
- complete bundle is RELEASED if safe in smoke.

## Phase J: Mechanicus and safety integration

OPS must call or respect Mechanicus command policy.

Required:

- load current command_policy.json if present;
- block unknown tools;
- mark dry-run as default;
- write receipts for command attempts;
- do not bypass Mechanicus with direct arbitrary shell.

Required safety receipt fields:

- real_servitor_execution_enabled;
- live_llm_backend_enabled;
- unsafe_shell_available;
- arbitrary_shell_allowed;
- dry_run_default;
- unknown_tool_blocked;
- secrets_staged;
- runtime_paths_staged;
- result.

## Phase K: documentation

Required docs:

- ORGANS/IMPERIAL_IDE/OPS/README.md
- ORGANS/IMPERIAL_IDE/OPS/RUN_FIRST_RU.md
- ORGANS/IMPERIAL_IDE/DOCS/OPS_TASK_CONSOLE_USER_GUIDE_RU.md
- ORGANS/IMPERIAL_IDE/DOCS/OPS_TASKPACK_BUILDER_CONTRACT.md
- ORGANS/IMPERIAL_IDE/DOCS/OPS_ASTRONOMICON_LIVE_REGISTRATION_GATE.md

Owner-facing docs may be Russian through Officio.

Docs must include exact commands for:

- opening OPS CLI;
- opening OPS TUI;
- running smoke;
- building a taskpack;
- registering a taskpack dry-run;
- viewing launch card;
- running lifecycle dry-run.

## Phase L: reports

Create reports under:

REPORTS/TASK-NEWREALITY-IMPERIAL-IDE-OPS-INTEGRATION-TASK-CONSOLE-ACTIVATION-PC-V0_1/

Required reports:

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

## Phase M: validation

Required validation:

- all created or modified JSON files parse;
- all created or modified Python files compile;
- OPS smoke passes or exact blocker recorded;
- CLI classify bug is fixed;
- OPS TUI smoke passes or exact blocker recorded;
- generated Astronomicon-compatible taskpack smoke passes;
- lifecycle dry-run smoke passes;
- fake-green trap catches bare PASS;
- bundle gate HELD/RELEASED behavior tested if safe;
- real execution blocked;
- live LLM disabled;
- unsafe shell blocked;
- no VM2 or VM3 actions;
- no runtime directories staged;
- no local route configs or secrets staged;
- git diff inside allowed_write_scope.

## Phase N: commit and validated push

Commit and push are required for PASS.

Commit message must include:

TASK-NEWREALITY-IMPERIAL-IDE-OPS-INTEGRATION-TASK-CONSOLE-ACTIVATION-PC-V0_1

After push, record:

- commit SHA;
- origin/master SHA;
- git status;
- pushed files summary;
- post-push equality of HEAD and origin/master.

## Stop conditions

Stop with BLOCK if:

- bundled OPS source cannot be located;
- source archive hash cannot be recorded;
- OPS import would overwrite active IDE files without safe conflict handling;
- known validate_intent bug cannot be fixed;
- taskpack builder cannot create valid Astronomicon-compatible root files;
- unsafe shell or real execution is required to pass;
- live LLM secrets are required;
- secrets or local configs would be staged;
- runtime directory would be staged;
- JSON validation fails and cannot be repaired;
- Python validation fails and cannot be repaired;
- push is rejected and cannot be safely resolved.
