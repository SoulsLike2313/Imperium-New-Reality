# TASK-NEWGEN-COMMIT-36DF325-CLEANUP-HARDENING-PC-V0_1

## Mission

Clean and harden the NewGen Dashboard L2 footprint introduced by commit `36df325e6cdfbf5cfe10a22ec969b97faa0853a8`, after the Doctrinarium doctrine commit `09215e78899dd735cc67905b3f55991915edac8d`.

The purpose is to get IMPERIUM out of dirt before continuing with the next tasks.

## Required doctrine

Servitor must read the Doctrinarium cockpit rethink synthesis before work. The doctrine says:

- do not blind-revert `36df325`;
- preserve reusable backend seed;
- quarantine/delete runtime/generated dirt;
- converge future actions with verification spine;
- smoke must be read-only by default;
- schemas and unified verdict semantics must become real gates;
- rebuild Sanctum as organ-centered cockpit, not action-card dashboard;
- start Mechanicus Arsenal through candidate cards, validation gates, and receipts.

## Work phases

### Phase 0 — Verify and read

1. `git status --short`
2. `git rev-parse HEAD`
3. Confirm current HEAD is `09215e7...` or later and contains the Doctrinarium doctrine files.
4. Read the mandatory documents listed in `00_START_HERE_SERVITOR.md`.
5. Create the report root:
   `IMPERIUM_NEW_GENERATION/REPORTS/TASK-NEWGEN-COMMIT-36DF325-CLEANUP-HARDENING-PC-V0_1/`

### Phase 1 — Inventory

Classify the L2 footprint into:

- `KEEP_SOURCE`
- `KEEP_CURATED_EVIDENCE`
- `QUARANTINE_GENERATED`
- `DELETE_RUNTIME_JUNK`
- `REWRITE_REQUIRED`
- `UNKNOWN_REVIEW_REQUIRED`

Write:

`IMPERIUM_NEW_GENERATION/REPORTS/TASK-NEWGEN-COMMIT-36DF325-CLEANUP-HARDENING-PC-V0_1/cleanup_classification_manifest.json`

### Phase 2 — Preserve signal

Keep source/backend seed, schemas, registry, smoke/playwright harness, final reports, closure receipts, and one negative visual baseline if it has explanation.

Do not remove source files listed in the doctrine/speculum keep-list unless a stronger local reason is found and recorded.

### Phase 3 — Remove or quarantine dirt

Remove tracked runtime junk such as:

- `server_pid.txt`
- `server_stdout.log`
- `server_stderr.log`
- committed last-result caches
- duplicate click receipts without new evidence
- duplicate demo owner decisions/notes
- duplicate continuity builds/zips from intermediate runs

Quarantine generated artifacts that may still contain evidence value but should not be treated as source progress.

Recommended quarantine root:

`IMPERIUM_NEW_GENERATION/ARTIFACTS/QUARANTINE/COMMIT_36DF325_L2_EVIDENCE_BURST/`

### Phase 4 — Add hygiene guard

Add a small checker/report if missing or useful. It must detect tracked files matching forbidden runtime patterns in NewGen dashboard/report areas.

Recommended output:

`IMPERIUM_NEW_GENERATION/REPORTS/TASK-NEWGEN-COMMIT-36DF325-CLEANUP-HARDENING-PC-V0_1/tracked_artifact_hygiene_report.json`

The checker may live under a relevant NewGen/Mechanicus/Sanctum tools folder, but do not create a full Arsenal foundation yet.

### Phase 5 — Final reports

Write:

- `FINAL_REPORT.md`
- `cleanup_classification_manifest.json`
- `tracked_artifact_hygiene_report.json`
- `closure_receipt.json`

The final report must explicitly say what was kept, quarantined, deleted, and postponed.

### Phase 6 — Checks, commit, push

Run reasonable checks available locally:

- `git status --short`
- JSON parse checks for new JSON files
- any existing lightweight NewGen checks that do not mutate state
- optional hygiene checker
- no write-action smoke unless explicitly read-only

Commit and push with:

`TASK-20260524: clean and harden NewGen dashboard L2 footprint`

## Stop conditions

Stop and report BLOCKED if:

- repository root is not `E:\IMPERIUM`;
- HEAD does not contain the Doctrinarium doctrine commit and cannot be pulled safely;
- worktree is dirty with unrelated user changes before work;
- a required cleanup would delete source files from the keep-list;
- classification is ambiguous for more than 20 files and cannot be resolved safely;
- any command would touch private/local external context without explicit Owner permission.

## Final Owner response format

Russian only:

1. Step name
2. Full path to bundle/report
3. Verdict
4. 3–4 lines of Russian comments for Owner
