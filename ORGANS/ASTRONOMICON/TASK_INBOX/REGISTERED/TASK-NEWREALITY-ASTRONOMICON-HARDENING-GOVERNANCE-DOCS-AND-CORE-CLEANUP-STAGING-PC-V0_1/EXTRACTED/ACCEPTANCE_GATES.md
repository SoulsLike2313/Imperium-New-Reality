# ACCEPTANCE GATES

## Gate 1: Astronomicon local admission

Required:

- taskpack is admitted through Astronomicon on PC, or an admission blocker is fully reported;
- TASK_ROUTE_MANIFEST_TEMPLATE.json is present in the taskpack root;
- TASK_START_ACK_TEMPLATE.json is present in the taskpack root;
- current expected task is updated if admission succeeds;
- no success is claimed without registry evidence.

PASS_WITH_WARNINGS is acceptable.
Clean PASS is forbidden unless every gate is fully proven.

## Gate 2: route and organ compatibility

Required:

- MANIFEST.organs includes all eight current required organs;
- MANIFEST.required_organs mirrors the same organs;
- MANIFEST.expanded_organ_circle_candidate may include CUSTODES as candidate;
- MANIFEST.organ_route explains each organ responsibility;
- TASK_ROUTE_MANIFEST_TEMPLATE.organs includes all eight current required organs.

## Gate 3: language gate

Required:

- taskpack internal files are English UTF-8 no BOM;
- MANIFEST.language_and_encoding_policy is an object;
- owner-facing Russian runtime files are routed through OFFICIO_AGENTIS;
- Cyrillic is forbidden inside taskpack internal files;
- Russian governance mirrors may be created as runtime output files, not as taskpack internal root text.

## Gate 4: PC preflight

Required:

- git root recorded;
- git status recorded;
- HEAD recorded;
- origin/master recorded;
- dirty state classified;
- local route config handling recorded.

BLOCK if local secrets or unsafe configs are staged.

## Gate 5: Astronomicon hardening

Required:

- repo-root discovery chain implemented or a precise blocker is recorded;
- current-root ORGANS paths are primary;
- legacy IMPERIUM_NEW_GENERATION path is fallback only;
- route manifest template discovery is deterministic;
- route config discovery is deterministic;
- interactive or dry-run smoke result exists;
- misleading admission diagnostics are improved or recorded as remaining blocker.

## Gate 6: governance files

Required files:

- ORGANS/_CORE_GOVERNANCE/README.md
- ORGANS/_CORE_GOVERNANCE/GOVERNANCE_INDEX.json
- ORGANS/_CORE_GOVERNANCE/EMPEROR/PASSPORT_OF_THE_EMPEROR.md
- ORGANS/_CORE_GOVERNANCE/EMPEROR/PASSPORT_OF_THE_EMPEROR_RU.md
- ORGANS/_CORE_GOVERNANCE/CONSTITUTION/CONSTITUTION_OF_THE_IMPERIUM.md
- ORGANS/_CORE_GOVERNANCE/CONSTITUTION/CONSTITUTION_OF_THE_IMPERIUM_RU.md

Required:

- English canonical candidates are UTF-8;
- Russian mirrors are owner-facing and routed through Officio;
- documents are marked CANON_CANDIDATE unless Owner final admission is recorded;
- no false claim that all capabilities already exist.

## Gate 7: AGENTS.md patch

Required:

- AGENTS.md remains concise;
- current-root truth is stated;
- remote contours are out of scope unless manifest says otherwise;
- fake-green rule is stated;
- validated push policy is stated;
- no local secrets or route configs are introduced.

## Gate 8: cleanup staging only

Required reports:

- cleanup_staging_plan.md;
- cleanup_allowlist.json;
- cleanup_denylist.json;
- duplicate_and_legacy_map.json;
- unknown_zone_report.json;
- move_batches_plan.json.

Forbidden:

- mass move;
- delete;
- quarantine admission to canon;
- Ancient import into active core.

## Gate 9: Mechanicus seed

Required:

- Mechanicus readiness or tool registry seed exists;
- every new Mechanicus item is PROVEN, CANDIDATE, MISSING, or BLOCKED;
- no uncarded permanent tool is claimed as canon.

## Gate 10: validation

Required:

- all created JSON parses;
- required Markdown files exist;
- command receipts exist;
- validation receipt exists;
- no staged file outside allowed_write_scope;
- no VM2 or VM3 action.

## Gate 11: validated push

Required for PASS:

- commit created with task ID;
- push to origin/master completed;
- post-push HEAD equals origin/master;
- git_commit_push_receipt.json exists;
- no failed validation is hidden.

Push is allowed for validated task outputs.
Push is forbidden only for dirty, secret, destructive, out-of-scope, or failed-validation changes.

## Final verdicts allowed

- PASS_WITH_WARNINGS_PUSHED_READY_FOR_CLEANUP_EXECUTION_TASK
- PASS_WITH_WARNINGS_PUSHED_READY_FOR_OWNER_REVIEW
- BLOCKED_UNTIL_ASTRONOMICON_REPAIR_DECISION
- BLOCKED_UNTIL_GIT_STATE_CLARITY
- BLOCKED_UNTIL_OWNER_DECISION
