# TASK SPEC

TASK_ID: TASK-20260605-PC-TRUTH-HEAD-CORRIDOR-SAVE-OFFICIO-RU-V0_1

## Mission

Execute a bounded PC task inside `E:/IMPERIUM_NEW_GENERATION_NEW_REALITY`.

The Servitor must repair and preserve the bootstrap fixes needed for the Astronomicon taskpack registration corridor, correct the current truth HEAD/card drift, and save the work with a normal commit and push.

## Mandatory entry sequence

1. Start in the New Reality root only: `E:/IMPERIUM_NEW_GENERATION_NEW_REALITY`.
2. Inspect `git status`, `git rev-parse HEAD`, `git branch --show-current`, and the canonical remote.
3. Enter Servitor role through `OFFICIO_AGENTIS` before any mutation:
   - inspect the available Officio role pack or contract in the repo;
   - record an Officio role-entry receipt;
   - after that meeting, owner-facing runtime responses and final owner summary must be Russian;
   - internal machine artifacts, code, JSON, manifests, schemas, and task receipts remain English UTF8 NO_BOM.
4. Read Astronomicon, Administratum, and root contracts relevant to task registration, current truth, scope, and remote closure.
5. Do not touch Ancient Empire or parent/private paths.

## Work package

### A. Preserve the Astronomicon entry corridor repair

Ensure these files exist, are valid JSON, are UTF8 without BOM, and are tracked by git:

- `ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_ROUTE_MANIFEST_TEMPLATE.json`
- `ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_START_ACK_TEMPLATE.json`

The route manifest template must include all eight required organs:

- DOCTRINARIUM
- OFFICIO_AGENTIS
- ASTRONOMICON
- ADMINISTRATUM
- MECHANICUS
- INQUISITION
- STRATEGIUM
- SCHOLA_IMPERIALIS

If the files already exist from the operator bootstrap, inspect and normalize them instead of blindly rewriting them.

### B. Make taskpack form readable to future agents

Create or update a canonical Astronomicon taskpack form note/contract under the Astronomicon area, for example:

- `ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASKPACK_FORM_CONTRACT_V0_1.md`

It must document the exact root taskpack names accepted by the current intake gate:

- `MANIFEST.json`
- `TASK_SPEC.md`
- `ACCEPTANCE_GATES.md`
- `OUTPUT_REQUIREMENTS.md`

It must also document the root language rule: English UTF8 NO_BOM, no Cyrillic in root taskpack files, and owner-facing Russian only through Officio authority.

### C. Correct Administratum current truth HEAD drift

Inspect the actual HEAD and the current truth card. If `ADMINISTRATUM/CURRENT_TRUTH/current_head_card_v0_1.json` is stale, update it to match the actual local HEAD at the time of execution and include a receipt explaining the correction.

### D. Validate and save

Run the available validation commands that fit this repo without inventing fake pass:

- JSON validation for changed JSON files.
- Astronomicon intake/registration or resolver checks if available and safe.
- Administratum current truth/card checker if available.
- `git status --porcelain` before and after.

Commit and push all accepted changes with a normal non-force push. Prove remote closure by showing that local `git rev-parse HEAD` equals `git ls-remote origin refs/heads/master` after push.

## Out of scope

- No large organ ring implementation in this task.
- No old Imperium runtime use.
- No broad refactor.
- No destructive cleanup.
- No fake green.

## Final owner response

The final owner response must be in Russian after the Officio role entry and must include:

- what was changed;
- what was validated;
- commit hash;
- push/remote closure proof;
- any warnings or UNKNOWN_WITH_REASON items.
