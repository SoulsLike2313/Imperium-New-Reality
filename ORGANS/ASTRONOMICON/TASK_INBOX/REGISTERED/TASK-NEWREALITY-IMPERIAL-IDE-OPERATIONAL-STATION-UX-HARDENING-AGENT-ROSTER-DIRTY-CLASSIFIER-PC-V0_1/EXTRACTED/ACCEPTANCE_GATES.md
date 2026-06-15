# ACCEPTANCE GATES

## Gate 1: Astronomicon admission

Required:

- taskpack is admitted through Astronomicon on PC, or admission blocker is fully reported;
- route manifest and start ack templates are present;
- task_id is resolvable after admission;
- no success is claimed without evidence.

PASS_WITH_WARNINGS is acceptable. Clean PASS is forbidden unless every gate is fully proven.

## Gate 2: MVP state preserved

Required:

- Workbench TUI still opens or exact blocker is recorded;
- Workbench GUI still opens structurally or exact blocker is recorded;
- OPS and Station layers remain available;
- generated taskpack workflow is not broken;
- reports and receipts are still visible.

## Gate 3: summary and full JSON viewer

Required:

- human summary renderer exists;
- full JSON viewer exists;
- TUI no longer relies only on truncated JSON;
- CLI can print full JSON;
- copy/open path actions or copy-ready commands exist.

## Gate 4: real agent roster

Required:

- real 12-servitor roster is primary view;
- Servitor Prime is present;
- organ servitors are present;
- WARP, MetaOS, and Imperial IDE servitors are present;
- legacy Alpha/Beta/Gamma is not the primary agent view;
- agent detail view exists or structured blocker recorded.

## Gate 5: Taskpack Manager

Required:

- generated taskpack list works;
- inspect works;
- validate works;
- ZIP path and SHA256 are visible;
- extracted root files are visible;
- dry-run registration status is visible;
- live promotion availability is visible but not auto-triggered.

## Gate 6: launch and handoff card viewer

Required:

- Launch Card view exists;
- Handoff Card view exists;
- copy-ready Servitor Prime block exists;
- dry-run versus live status is visible;
- candidate versus canon status is visible;
- handoff-ready is not shown as execution-done.

## Gate 7: reports and receipts browser

Required:

- latest reports listed with summaries;
- latest receipts listed with summaries;
- raw JSON available through full viewer;
- open/copy path action or copy-ready command exists;
- filters or typed categories exist for safety, validation, git, admission, resolver, launch, and lifecycle.

## Gate 8: dirty classifier

Required:

- dirty classifier exists;
- current dirty paths are classified;
- the two known ZIP artifacts are classified;
- action recommendation exists;
- no file is deleted;
- push state reflects classification.

## Gate 9: Safety Center 2.0

Required:

- real execution disabled;
- live LLM disabled;
- unsafe shell blocked;
- arbitrary shell blocked;
- remote contours disabled;
- live registration scope shown;
- push gate shown;
- dirty state shown;
- future gate explanation shown.

## Gate 10: live registration promotion flow

Required:

- dry-run remains default;
- promotion screen exists;
- promotion requires explicit owner confirmation;
- promotion shows current expected task impact;
- no automatic live promotion is run during smoke;
- promotion receipt exists.

## Gate 11: Lifecycle UI

Required:

- lifecycle stages are visible;
- dry-run registration and live registration are separate;
- handoff-ready and execution-done are separate;
- next recommended action is shown.

## Gate 12: Git Closure UI

Required:

- branch, HEAD, origin/master visible;
- head_equals_origin_master visible;
- dirty_count visible;
- classified dirty table visible;
- push_allowed_state visible;
- recommended action visible.

## Gate 13: validation

Required:

- all created or modified JSON files parse;
- all created or modified Python files compile;
- TUI smoke passes or exact blocker recorded;
- GUI structural smoke passes or exact blocker recorded;
- station UX smoke passes;
- dirty classifier smoke passes;
- safety smoke passes;
- git diff inside allowed_write_scope.

## Gate 14: validated push

Required for PASS:

- commit created with task ID;
- push to origin/master completed;
- post-push HEAD equals origin/master;
- git_commit_push_receipt.json exists;
- no failed validation is hidden.

Push is allowed for validated task outputs. Push is required for success. Push is forbidden only for dirty, secret, destructive, out-of-scope, unsafe, or failed-validation changes.

## Final verdicts allowed

- PASS_WITH_WARNINGS_PUSHED_READY_FOR_DAILY_OPERATIONAL_USE
- PASS_WITH_WARNINGS_PUSHED_READY_FOR_LIVE_REGISTRATION_PROMOTION_REVIEW
- PASS_WITH_WARNINGS_PUSHED_READY_FOR_OWNER_REVIEW
- BLOCKED_UNTIL_TUI_UX_DECISION
- BLOCKED_UNTIL_DIRTY_CLASSIFIER_DECISION
- BLOCKED_UNTIL_AGENT_ROSTER_FIX
- BLOCKED_UNTIL_SAFETY_DECISION
- BLOCKED_UNTIL_GIT_STATE_CLARITY
- BLOCKED_UNTIL_OWNER_DECISION
