# ACCEPTANCE GATES

TASK_ID: TASK-20260605-PC-TRUTH-HEAD-CORRIDOR-SAVE-OFFICIO-RU-V0_1

## Gate 1: Root and scope

PASS only if:

- Working root is `E:/IMPERIUM_NEW_GENERATION_NEW_REALITY`.
- Branch is `master` unless an existing contract explicitly says otherwise.
- No Ancient Empire or parent/private path is used as runtime.

BLOCK if:

- Any mutation is attempted outside the New Reality root.
- The task attempts to use old `Imperium-` or Ancient as active execution body.

## Gate 2: Officio role entry and language switch

PASS only if:

- Servitor entered role through OFFICIO_AGENTIS before mutation.
- A role-entry receipt or explicit final report section exists.
- Owner-facing runtime/final response after Officio is Russian.
- Internal artifacts remain English UTF8 NO_BOM unless an Officio exception receipt exists.

BLOCK if:

- Servitor starts editing without Officio role-entry evidence.
- Final owner-facing response remains English without explaining an Officio blocker.
- Cyrillic appears in root taskpack/internal machine files where the Astronomicon language gate forbids it.

## Gate 3: Astronomicon entry corridor patch preservation

PASS only if:

- `TASK_ROUTE_MANIFEST_TEMPLATE.json` exists, parses as JSON, has no UTF8 BOM, and includes all eight required organs.
- `TASK_START_ACK_TEMPLATE.json` exists, parses as JSON, and has no UTF8 BOM.
- The taskpack form contract/note exists and explains canonical root files and language/encoding policy.

BLOCK if:

- Route template is missing, invalid JSON, BOM-prefixed, or missing required organs.
- Start ACK template is missing or invalid.
- The taskpack form remains hidden only in Python code with no agent-readable contract.

## Gate 4: Administratum current truth correction

PASS only if:

- Actual `git rev-parse HEAD` is compared against `ADMINISTRATUM/CURRENT_TRUTH/current_head_card_v0_1.json`.
- Any stale HEAD/card drift is corrected or a precise blocker is reported.
- A receipt records the before/after truth state.

BLOCK if:

- HEAD drift is ignored.
- Current truth is updated to a guessed hash instead of measured local HEAD.

## Gate 5: Validation

PASS only if:

- Changed JSON files are parsed successfully.
- Available repo checkers relevant to the changed files are run, or their absence is recorded as UNKNOWN_WITH_REASON.
- No fake green is claimed.

BLOCK if:

- Validation failures are hidden.
- Missing tools or missing metrics are reported as pass.

## Gate 6: Commit, push, and remote closure

PASS only if:

- All intended changes are committed.
- Push is normal non-force push.
- Final proof shows local HEAD equals remote `origin/master` HEAD.

BLOCK if:

- Work remains only local without explicit blocker.
- Push is skipped without reason.
- Remote closure is not proven.
