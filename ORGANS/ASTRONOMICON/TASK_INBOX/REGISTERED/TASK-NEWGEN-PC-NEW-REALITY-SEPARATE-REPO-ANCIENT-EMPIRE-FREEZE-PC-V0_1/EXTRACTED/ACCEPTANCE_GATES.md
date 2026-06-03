# Acceptance Gates

## Local step PASS gates

A local PASS or PASS_WITH_WARNINGS requires all gates below.

### Gate 1: PC contour truth

- PC repository path checked.
- Current branch and HEAD recorded.
- Worktree state recorded.
- Source folder `E:/IMPERIUM/IMPERIUM_NEW_GENERATION` exists.

### Gate 2: Non-destructive Ancient Empire freeze

- `ancient_empire_freeze_receipt.json` exists.
- Old repository still exists after the task.
- Source NewGen folder still exists after the task.
- No deletion of old repo is performed.

### Gate 3: New Reality root

- `E:/IMPERIUM_NEW_GENERATION_NEW_REALITY` exists.
- It contains promoted NewGen core content.
- It is not a full copy of the old repository.
- It has its own root `README.md`, `AGENTS.md`, `NEW_REALITY_SCOPE_LOCK.md`, `EPOCH_MANIFEST.json`.

### Gate 4: Local git repository

- New Reality has its own `.git` directory.
- Initial commit exists.
- `git status --short` for New Reality is clean after commit unless there is a declared BLOCK/WARN reason.

### Gate 5: Scope lock

- Scope lock explicitly says Servitor default read/write/mutate root is New Reality only.
- Any access to Ancient Empire requires `SALVAGE_REQUEST` and explicit admission.
- Private folders and arbitrary parent paths are forbidden.

### Gate 6: Dependency scan

- External references scan completed.
- Findings are recorded, not hidden.
- If critical external dependencies exist, verdict cannot be clean PASS.

### Gate 7: Receipts and bundle

- Required receipts exist.
- SHA256SUMS exist.
- Final task report bundle exists.

## BLOCK gates

Return BLOCK if:

- Source NewGen folder is missing.
- Target New Reality root exists and is non-empty without Owner admission.
- Copy would overwrite unrelated files.
- Old repo would be deleted or rewritten.
- New Reality cannot be initialized as local git repo.
- New Reality root contracts cannot be written.

## Expected warnings

The result may remain PASS_WITH_WARNINGS if:

- No remote New Reality GitHub repo exists yet.
- VM2/VM3 are not synced yet.
- Throne is not adapted to New Reality yet.
- External dependency scan finds references that need follow-up.
