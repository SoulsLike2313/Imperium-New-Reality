# Acceptance Gates

## Gate 1: PC contour admission

- Task must be performed on PC contour, not VM3.
- Repo root must be verified.
- Expected start HEAD must be verified or safely fast-forwarded.
- Worktree must be clean before modifications.

## Gate 2: Scope lock

The task is limited to raw external review bundle attachment, verification, cap adjudication, and next-task candidate recording.

Forbidden claims:

- No IDE runtime.
- No WARP runtime.
- No browser/API runtime.
- No freelance readiness.
- No trading readiness.
- No global clean PASS.
- No implementation of the future Astronomicon launcher.
- No implementation of the future Administratum continuity launcher.

## Gate 3: Raw evidence verification

Every raw external review bundle copied into the repo must have:

- filename
- source classification
- target head
- reviewer
- sha256
- size
- verification status
- final repo path

## Gate 4: External finalization decision

`CAP_EXTERNAL_FINALIZATION_RECEIPT_MISSING_OR_NEEDS_FOLLOWUP` may be set to CLOSED only if raw external review bundles or equivalent signed external references are present, hash-checked, readable, and mapped to the correct target heads.

If the evidence is partial or ambiguous, the cap must remain NARROWED or CARRIED.

## Gate 5: Positive-control preservation

The following cases must be preserved as reusable regression fixtures or learning evidence:

- BAD_ZIP_MISSING_MANIFEST
- BAD_ZIP_MISSING_LANGUAGE_POLICY
- BAD_ZIP_MISSING_8_ORGAN_ROUTE
- UNREGISTERED_TASK_ID_RESOLVE
- VALID_8_ORGAN_TASKPACK

## Gate 6: Launcher decisions recorded

The task must record both future launcher candidates:

- Astronomicon-owned VM3 taskpack launcher and IDE handoff bridge.
- Administratum-owned continuity pack launcher and Logos-Prime handoff bridge.

Do not implement either in this task.

## Gate 7: Final closure

Before final report:

- Required outputs exist.
- JSON outputs are valid.
- Claim ledger includes supported and rejected claims.
- Hard red-team verdict is not fake clean.
- Git status is clean after commit.
- origin/master equals HEAD after push, unless push is blocked and explicitly reported.
