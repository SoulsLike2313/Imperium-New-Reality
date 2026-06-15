# TASK SPEC

## Task ID

TASK-NEWREALITY-GOVERNANCE-CANON-MECHANICUS-ULTRA-IDE-FOUNDATION-PC-V0_1

## Mode

CONTROLLED_WRITE_WITH_VALIDATED_PUSH.

This task is PC only.

This task canonizes approved governance documents and builds the first large foundation for Mechanicus ultra-form and the future custom Imperium IDE.

This task must not touch VM2 or VM3.

## Strategic direction

Imperium New Reality is not merely a repository to be used from an external IDE.

Imperium New Reality must become the kernel of a future custom IDE.

That IDE will be a development zone over the kernel and must support extensions, tool invocation, validation, receipts, taskpack execution, product workflows, and owner-facing control.

Mechanicus is prioritized first because it must be the guardian, registry, validator, and safe invocation authority for tools used by the future IDE.

## Mission

Perform a large but bounded PC task:

1. Canonize approved governance documents.
2. Update AGENTS.md as active boot-law for the current root.
3. Keep Astronomicon usable for local PC task entry and record remaining defects.
4. Build Mechanicus ultra-form foundation.
5. Build Imperial IDE foundation contracts and extension model.
6. Validate all outputs.
7. Commit and push validated outputs.

## Phase A: preflight

Required:

- Resolve git root.
- Record git status short.
- Record HEAD and origin/master.
- Record whether HEAD equals origin/master.
- Confirm latest governance staging task exists.
- Confirm governance candidate files exist.
- Confirm no local route config or secret is staged.
- If local contour_route_config.json exists, keep it local-only unless it is a safe example file.

Stop if preflight cannot establish a safe PC current-root state.

## Phase B: governance canonization

Canonize current governance candidates with Owner authority.

Update these files if present, or create them if absent:

- ORGANS/_CORE_GOVERNANCE/README.md
- ORGANS/_CORE_GOVERNANCE/GOVERNANCE_INDEX.json
- ORGANS/_CORE_GOVERNANCE/EMPEROR/PASSPORT_OF_THE_EMPEROR.md
- ORGANS/_CORE_GOVERNANCE/EMPEROR/PASSPORT_OF_THE_EMPEROR_RU.md
- ORGANS/_CORE_GOVERNANCE/CONSTITUTION/CONSTITUTION_OF_THE_IMPERIUM.md
- ORGANS/_CORE_GOVERNANCE/CONSTITUTION/CONSTITUTION_OF_THE_IMPERIUM_RU.md

Required status transition:

- from CANON_CANDIDATE to CANON_ACTIVE;
- record owner_canonization_approval as true;
- record canonization_task_id;
- record canonization_timestamp;
- record authority order.

The authority order must be:

1. Emperor Passport;
2. Constitution of the Imperium;
3. AGENTS.md;
4. Organ contracts and read-first files;
5. Astronomicon taskpacks;
6. Tool cards and validators;
7. Reports and receipts.

Do not claim that all target capabilities already exist.

## Phase C: AGENTS.md boot-law patch

Patch AGENTS.md so that any Servitor, Codex session, or local executor can enter the system correctly.

Required points:

- Resolve current repo root first.
- Current-root ORGANS is active truth.
- IMPERIUM_NEW_GENERATION old-prefix paths are compatibility residue, not primary truth.
- VM2 and VM3 are out of scope unless the task manifest explicitly routes to them.
- Read Governance Index, Passport, Constitution, Astronomicon current task, and taskpack.
- Mechanicus owns tool registry, validation, receipts, and safe tool invocation.
- Imperial IDE foundation is a current strategic target.
- No fake-green.
- Validated task outputs may and should be committed and pushed when policy permits.
- Do not push secrets, local configs, destructive changes, failed validation, or out-of-scope changes.

AGENTS.md must remain concise and operational.

## Phase D: Astronomicon local hardening

Do not over-expand this phase.

Required:

- Preserve working PC registration path.
- Ensure current-root path discovery remains primary.
- Record remaining old-prefix residue.
- Ensure taskpack admission failure diagnostics include searched paths when feasible.
- Provide a launcher or command note that prevents repo-root loss.

Allowed examples:

- ORGANS/ASTRONOMICON/run_astronomicon_pc.ps1
- ORGANS/ASTRONOMICON/README_PC_LAUNCH.md
- small patch to taskpack registration skill if safe.

Forbidden:

- remote route changes;
- VM2 or VM3 route activation;
- unsafe rewrite of task entry corridor.

## Phase E: Mechanicus ultra-form foundation

Create the first real Mechanicus spine.

Required directories may include:

- ORGANS/MECHANICUS/REGISTRY/
- ORGANS/MECHANICUS/SCHEMAS/
- ORGANS/MECHANICUS/TOOLS/
- ORGANS/MECHANICUS/RECEIPTS/
- ORGANS/MECHANICUS/IDE_BRIDGE/
- ORGANS/MECHANICUS/DOCS/

Required outputs:

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

Required CLI behavior, if implemented:

- doctor;
- inventory;
- validate-json;
- list-tools;
- list-capabilities;
- policy;
- emit-receipt;
- dry-run-tool.

The command gateway must be dry-run first and allowlisted.

No unsafe arbitrary shell execution may be enabled.

Each tool or capability must be classified as:

- PROVEN;
- CANDIDATE;
- MISSING;
- BLOCKED.

## Phase F: custom IDE foundation

Create the first foundation for the custom Imperium IDE.

This is not a full GUI implementation task.

The task should create contracts, schemas, registries, and architectural spine so future tasks can build the IDE safely.

Required directories may include:

- ORGANS/IMPERIAL_IDE/
- ORGANS/IMPERIAL_IDE/CONTRACTS/
- ORGANS/IMPERIAL_IDE/SCHEMAS/
- ORGANS/IMPERIAL_IDE/EXTENSIONS/
- ORGANS/IMPERIAL_IDE/WORKSPACE/
- ORGANS/IMPERIAL_IDE/BRIDGES/
- ORGANS/IMPERIAL_IDE/DOCS/

Required outputs:

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

IDE foundation requirements:

- The IDE must treat New Reality as the kernel.
- The IDE must invoke tools through Mechanicus, not by ungoverned shell calls.
- Extensions must declare permissions, tools, panels, commands, risks, receipts, and validation requirements.
- The IDE must support future taskpack control, report browsing, receipt inspection, tool execution, validation replay, and product workspaces.
- The IDE must not claim to be implemented as a full application in this task.

## Phase G: reports

Create report outputs under:

REPORTS/TASK-NEWREALITY-GOVERNANCE-CANON-MECHANICUS-ULTRA-IDE-FOUNDATION-PC-V0_1/

Required reports:

- governance_canonization_receipt.json
- governance_canonization_summary.md
- agents_boot_law_patch_receipt.json
- astronomicon_local_hardening_receipt.json
- mechanicus_ultra_foundation_summary.md
- mechanicus_tool_registry_validation_receipt.json
- imperial_ide_foundation_summary.md
- ide_extension_model_receipt.json
- command_receipt.json
- validation_receipt.json
- git_diff_scope_receipt.json
- git_commit_push_receipt.json
- FINAL_OWNER_SUMMARY_RU.md

## Phase H: validation

Required:

- all JSON files created or modified by this task parse successfully;
- Python files created by this task compile with py_compile;
- Mechanicus CLI doctor or equivalent smoke runs, even if PASS_WITH_WARNINGS;
- IDE schemas parse as JSON;
- AGENTS.md exists and remains concise;
- governance files are CANON_ACTIVE after Owner-approved transition;
- no VM2 or VM3 action occurred;
- no local route config or secrets are staged;
- git diff is inside allowed_write_scope.

## Phase I: commit and validated push

Commit and push are required for success.

Commit message must include:

TASK-NEWREALITY-GOVERNANCE-CANON-MECHANICUS-ULTRA-IDE-FOUNDATION-PC-V0_1

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
- governance files cannot be safely canonized;
- task would require VM2 or VM3;
- unsafe arbitrary command execution is required;
- secrets or local configs would be staged;
- JSON validation fails and cannot be repaired;
- Python validation fails and cannot be repaired;
- push is rejected and cannot be safely resolved.
