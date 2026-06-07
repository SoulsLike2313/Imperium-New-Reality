# TASK SPEC

## Task ID

TASK-NEWREALITY-ASTRONOMICON-HARDENING-GOVERNANCE-DOCS-AND-CORE-CLEANUP-STAGING-PC-V0_1

## Mode

CONTROLLED_WRITE_WITH_VALIDATED_PUSH.

This task is PC only.

This task must repair local Astronomicon bootstrap behavior, create governance document candidates, patch AGENTS.md, produce core cleanup staging artifacts, validate outputs, commit, and push validated task outputs.

This task must not touch VM2 or VM3.

## Mission

Use the latest New Reality self-analysis report and the Owner-provided grand sterilization planning pack as planning input.

Perform a single large but bounded PC task:

1. Repair Astronomicon local bootstrap and path discovery enough for normal PC task registration and operator use.
2. Create the current-root governance document structure.
3. Write Emperor Passport candidate files in canonical English and Owner-facing Russian mirror.
4. Write Constitution candidate files in canonical English and Owner-facing Russian mirror.
5. Patch AGENTS.md with current-root, task-entry, no-fake-green, and validated-push policy.
6. Produce a core cleanup staging plan, not destructive cleanup.
7. Produce Mechanicus next-step readiness and tool-registry seed if safe.
8. Commit and push validated outputs, then write a push receipt.

## Evidence boundary

Active truth is the current PC repository root.

The following prior report is input evidence, not automatic authority:

- REPORTS/TASK-NEWREALITY-IMPERIUM-SELF-ANALYSIS-LIVE-GIT-PICTURE-PC-V0_3/

The Operator-provided grand sterilization draft pack is planning input, not canon by itself.

Ancient repository material is read-only historical context only. Do not copy Ancient files into active New Reality.

## Phase A: preflight

Required:

- Resolve git root.
- Record git status short.
- Record HEAD and origin/master.
- Record whether HEAD equals origin/master.
- Detect untracked local configs such as contour_route_config.json.
- Ensure local route config or secrets are not staged.
- If local contour_route_config.json exists, either keep it untracked and local-only or add it to .gitignore if that is the chosen safe repo policy.

Do not start mutating until preflight evidence is written to command receipts.

## Phase B: Astronomicon hardening

Fix the Astronomicon defects observed in the previous task:

- interactive repo-root discovery bug;
- current-root versus legacy-compatible path drift;
- route-config discovery drift;
- route manifest template discovery drift;
- misleading admission diagnostics that say manifest_found=false when an earlier gate blocked extraction.

Required repair behavior:

- Current-root ORGANS paths are primary.
- Legacy IMPERIUM_NEW_GENERATION paths may be compatibility fallback only and must emit a warning.
- Interactive launch must discover git root from a deterministic chain:
  explicit --repo-root, current git root, script file location walk-up, then fail with searched paths.
- Route config discovery must prefer a safe current-root operator config path or explicit --route-config.
- Local contour_route_config.json must not be committed unless it is a safe example file.
- Existing contour_route_config.example.json may remain trackable as an example.
- Admission blockers must print exact searched paths.

Required smoke:

- Run local PC registration or a dry-run/intake smoke without remote route.
- Record the command and result.
- If smoke cannot be safely completed, write a precise blocker report instead of fake-green.

## Phase C: governance ignition

Create or update these files:

- ORGANS/_CORE_GOVERNANCE/README.md
- ORGANS/_CORE_GOVERNANCE/GOVERNANCE_INDEX.json
- ORGANS/_CORE_GOVERNANCE/EMPEROR/PASSPORT_OF_THE_EMPEROR.md
- ORGANS/_CORE_GOVERNANCE/EMPEROR/PASSPORT_OF_THE_EMPEROR_RU.md
- ORGANS/_CORE_GOVERNANCE/CONSTITUTION/CONSTITUTION_OF_THE_IMPERIUM.md
- ORGANS/_CORE_GOVERNANCE/CONSTITUTION/CONSTITUTION_OF_THE_IMPERIUM_RU.md

Status of these files:

- CANON_CANDIDATE unless Owner explicitly upgrades them later.
- Authority-bearing candidates, not final canon by self-claim.
- Russian mirrors are allowed through Officio Agentis.

### Emperor Passport content requirements

The Passport must include:

- supreme Owner sovereignty;
- Imperium mission as script-first, local-first, evidence-bound AI orchestration kernel;
- product orientation: requests become finished products;
- manual Owner assistance is valid only when marked;
- fake-green is forbidden;
- definition of done;
- validated push policy;
- Owner communication contract;
- relationship to Constitution, AGENTS.md, organ contracts, and taskpacks.

The Passport must not claim all capabilities already exist. It must distinguish target form from proven capability.

### Constitution content requirements

The Constitution must include:

- authority hierarchy;
- required baseline organs;
- task lifecycle;
- evidence levels;
- Astronomicon duties;
- Mechanicus duties;
- Inquisition anti-fake-green duties;
- Administratum continuity duties;
- cleanup and quarantine law;
- validated push and remote closure law;
- language law;
- security law;
- product orientation law.

The Constitution must not self-admit quarantined artifacts, Ancient files, or candidate tools as canon.

## Phase D: AGENTS.md patch

Patch root AGENTS.md in a concise way.

Required concepts:

- active PC truth is current repo root;
- do not treat IMPERIUM_NEW_GENERATION, VM2, VM3, Ancient, report archives, or quarantine as active truth by default;
- read governance index, Passport, Constitution when present;
- Astronomicon task registry is the task entry source;
- Mechanicus tools require cards or candidate status;
- every PASS claim requires receipts;
- validated task outputs may be committed and pushed;
- push is forbidden only for out-of-scope, dirty, secret, failed-validation, or destructive changes;
- PC tasks do not require remote contours unless manifest says so.

AGENTS.md must remain short and operational. It must not become a full constitution.

## Phase E: core cleanup staging only

Produce staging reports but do not perform mass cleanup.

Use these zone classes from the Owner planning input:

- CORE;
- ORGAN_RUNTIME;
- ORGAN_RECEIPT;
- SUPPORT;
- GOVERNANCE;
- LEGACY;
- QUARANTINE;
- REPORT;
- FIXTURE;
- UNKNOWN.

Required outputs:

- cleanup_staging_plan.md;
- cleanup_allowlist.json;
- cleanup_denylist.json;
- duplicate_and_legacy_map.json;
- unknown_zone_report.json;
- move_batches_plan.json.

Rules:

- No delete in this task.
- No mass move in this task.
- UNKNOWN blocks automation.
- Move-before-delete is mandatory for future tasks.
- Delete requires a future Owner batch approval gate.

## Phase F: Mechanicus seed

Create a report or candidate registry seed for script-first local control.

Required concepts:

- tool_id;
- owner_organ;
- path_current_root;
- entrypoint;
- dependencies;
- dependency_class;
- risk_class;
- default_mode;
- last_replay_timestamp;
- replay_receipt_path;
- status;
- allowlisted.

This phase may write under ORGANS/MECHANICUS only if the change is clearly a candidate or registry seed and validation passes.

## Phase G: validation

Required checks:

- git status before and after;
- JSON parse for all created JSON;
- no staged local contour_route_config.json unless it is intentionally safe and documented;
- no secrets;
- no VM2 or VM3 files touched;
- required governance files exist;
- AGENTS.md remains present;
- Astronomicon smoke result exists;
- cleanup reports exist;
- final summary exists.

## Phase H: commit and validated push

Commit and push are required for success.

Do not block push categorically.

Commit message must include:

TASK-NEWREALITY-ASTRONOMICON-HARDENING-GOVERNANCE-DOCS-AND-CORE-CLEANUP-STAGING-PC-V0_1

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
- destructive cleanup becomes necessary;
- secrets or local configs would be staged;
- JSON validation fails and cannot be repaired;
- Astronomicon repair requires unsafe rewrite;
- push is rejected and cannot be safely resolved.
