# ACCEPTANCE GATES

## Gate 1: Astronomicon admission

Required:

- taskpack is admitted through Astronomicon on PC, or an admission blocker is fully reported;
- TASK_ROUTE_MANIFEST_TEMPLATE.json is present in the taskpack root;
- TASK_START_ACK_TEMPLATE.json is present in the taskpack root;
- current expected task is updated if admission succeeds;
- no success is claimed without registry evidence.

PASS_WITH_WARNINGS is acceptable.
Clean PASS is forbidden unless every gate is fully proven.

## Gate 2: governance canonization

Required:

- Governance Index exists;
- Emperor Passport English file exists;
- Emperor Passport Russian mirror exists;
- Constitution English file exists;
- Constitution Russian mirror exists;
- status is CANON_ACTIVE after Owner-approved transition;
- canonization task ID is recorded;
- authority order is recorded;
- no claim is made that target capabilities already fully exist.

## Gate 3: AGENTS boot-law

Required:

- AGENTS.md states current-root truth;
- AGENTS.md identifies old-prefix residue as compatibility only;
- AGENTS.md states Mechanicus tool authority;
- AGENTS.md states custom IDE strategic target;
- AGENTS.md states validated push policy;
- AGENTS.md remains concise.

## Gate 4: Astronomicon local hardening

Required:

- local PC launch path is documented or repaired;
- current-root discovery is primary;
- legacy path is fallback only or remaining blocker is recorded;
- smoke or dry-run result exists;
- local route config is not staged.

## Gate 5: Mechanicus ultra foundation

Required:

- Mechanicus registry directory exists;
- tool registry exists and parses;
- capability registry exists and parses;
- command policy exists and parses;
- tool card schema exists and parses;
- command receipt schema exists and parses;
- at least one Mechanicus CLI or doctor entrypoint exists;
- tool invocation remains dry-run or allowlisted;
- no arbitrary unsafe shell gateway is enabled.

## Gate 6: custom IDE foundation

Required:

- ORGANS/IMPERIAL_IDE exists;
- IDE kernel contract exists;
- IDE extension API contract exists;
- IDE tool invocation contract exists;
- extension manifest schema exists and parses;
- workspace state schema exists and parses;
- extension registry exists and parses;
- Mechanicus bridge contract exists;
- IDE build ladder exists;
- no false claim of full GUI implementation.

## Gate 7: validation

Required:

- all created or modified JSON files parse;
- created Python files compile if Python files are created;
- command receipts exist;
- validation receipt exists;
- git diff is inside allowed_write_scope;
- no VM2 or VM3 action;
- no secrets or local configs staged.

## Gate 8: validated push

Required for PASS:

- commit created with task ID;
- push to origin/master completed;
- post-push HEAD equals origin/master;
- git_commit_push_receipt.json exists;
- no failed validation is hidden.

Push is allowed for validated task outputs.
Push is required for success.
Push is forbidden only for dirty, secret, destructive, out-of-scope, or failed-validation changes.

## Final verdicts allowed

- PASS_WITH_WARNINGS_PUSHED_READY_FOR_MECHANICUS_IDE_NEXT_BUILD
- PASS_WITH_WARNINGS_PUSHED_READY_FOR_OWNER_REVIEW
- BLOCKED_UNTIL_GOVERNANCE_CANONIZATION_DECISION
- BLOCKED_UNTIL_MECHANICUS_SAFETY_DECISION
- BLOCKED_UNTIL_GIT_STATE_CLARITY
- BLOCKED_UNTIL_OWNER_DECISION
