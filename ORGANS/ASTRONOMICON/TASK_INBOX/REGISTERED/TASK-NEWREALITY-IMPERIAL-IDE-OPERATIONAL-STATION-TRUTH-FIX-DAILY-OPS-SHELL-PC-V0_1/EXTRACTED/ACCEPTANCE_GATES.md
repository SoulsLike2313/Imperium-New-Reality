# ACCEPTANCE GATES

## Gate 1: Astronomicon admission

Required:

- taskpack is admitted through Astronomicon on PC, or admission blocker is fully reported;
- TASK_ROUTE_MANIFEST_TEMPLATE.json is present;
- TASK_START_ACK_TEMPLATE.json is present;
- task_id is resolvable after admission;
- no success is claimed without evidence.

PASS_WITH_WARNINGS is acceptable.
Clean PASS is forbidden unless every gate is fully proven.

## Gate 2: preflight truth capture

Required:

- git status captured;
- HEAD and origin/master captured;
- TUI, GUI, CLI, station, agents, and taskpack manager state captured;
- current dirty state captured;
- known issues are either reproduced or explicitly marked no longer reproducible.

## Gate 3: command palette integrity

Required:

- command_palette.json parses;
- help output is valid JSON;
- no malformed command entry around taskpack-copy-path and handoff-card;
- all commands map to handlers or structured BLOCKED responses;
- risk classes reflect mutating versus read-only behavior.

## Gate 4: read-only no-dirty discipline

Required:

- read-only command set does not modify tracked files;
- inspection receipts are not written to tracked report files;
- optional inspection receipts use ignored runtime paths;
- read-only commands are not falsely labelled if they mutate;
- no-dirty smoke proves before and after status.

## Gate 5: TUI real roster truth

Required:

- Agents and Servitors primary TUI view lists the 12 real servitors;
- Alpha/Beta/Gamma is not the primary roster;
- legacy capsule display is debug-only if still present;
- Servitor Prime, Astronomicon, Mechanicus, Administratum, Inquisition, Strategium, Doctrinarium, Officio Agentis, Schola Imperialis, WARP, MetaOS, and Imperial IDE are visible.

## Gate 6: summary-first UI

Required:

- core TUI screens show human summary, key fields, and next action;
- raw JSON is available through full viewer or CLI;
- truncated JSON is not the only usable output;
- path actions are available where relevant.

## Gate 7: daily operations shell

Required:

- daily ops board exists;
- daily ops board shows system truth, current task, agents, taskpack, lifecycle, safety, dirty state, git closure, and next action;
- daily ops smoke passes.

## Gate 8: taskpack manager v2

Required:

- list generated taskpacks;
- inspect selected/latest taskpack;
- validate taskpack;
- show ZIP path and SHA256;
- show extracted root files;
- show dry-run registration receipt;
- show live promotion review availability;
- show copy/open commands.

## Gate 9: live registration promotion review

Required:

- review screen exists;
- dry-run remains default;
- current expected task impact is shown;
- candidate versus canon state is shown;
- explicit Owner confirmation is required;
- automatic live promotion is not run during smoke.

## Gate 10: dirty classifier and git closure action planner

Required:

- dirty paths are classified;
- current task report artifacts are separated from old unrelated artifacts;
- runtime artifacts and generated taskpack runtime are separated;
- secrets and local config are blockers;
- exact recommended actions are printed;
- no files are deleted;
- final state has no unclassified dirt.

## Gate 11: safety

Required:

- real servitor execution remains disabled;
- live LLM backend remains disabled;
- unsafe shell remains blocked;
- arbitrary shell remains blocked;
- VM2 and VM3 remain out of scope;
- destructive cleanup remains disabled;
- no fake-green claim.

## Gate 12: validation

Required:

- all created or modified JSON files parse;
- all created or modified Python files compile;
- TUI smoke passes or exact blocker recorded;
- GUI structural smoke passes or exact blocker recorded;
- station final smoke passes;
- git diff is inside allowed_write_scope.

## Gate 13: validated push

Required for PASS:

- commit created with task ID;
- push to origin/master completed;
- post-push HEAD equals origin/master;
- git_commit_push_receipt.json exists;
- final git status and remaining dirty classification are recorded;
- no failed validation is hidden.

Push is allowed for validated task outputs.
Push is required for success.
Push is forbidden only for dirty, secret, destructive, out-of-scope, unsafe, or failed-validation changes.

## Final verdicts allowed

- PASS_WITH_WARNINGS_PUSHED_READY_FOR_DAILY_OPERATIONAL_USE
- PASS_WITH_WARNINGS_PUSHED_READY_FOR_OWNER_LIVE_PROMOTION_REVIEW
- PASS_WITH_WARNINGS_PUSHED_READY_FOR_NEXT_REAL_SERVITOR_GATE
- BLOCKED_UNTIL_READONLY_NO_DIRTY_FIXED
- BLOCKED_UNTIL_TUI_ROSTER_TRUTH_FIXED
- BLOCKED_UNTIL_COMMAND_PALETTE_FIXED
- BLOCKED_UNTIL_GIT_STATE_CLARITY
- BLOCKED_UNTIL_OWNER_DECISION
