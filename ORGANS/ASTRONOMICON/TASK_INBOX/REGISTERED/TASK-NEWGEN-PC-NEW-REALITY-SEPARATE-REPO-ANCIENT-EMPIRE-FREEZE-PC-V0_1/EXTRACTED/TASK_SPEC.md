# Task Spec

## Task

`TASK-NEWGEN-PC-NEW-REALITY-SEPARATE-REPO-ANCIENT-EMPIRE-FREEZE-PC-V0_1`

## Mission

Create the first non-destructive PC-local split between:

- `ANCIENT_EMPIRE`: the existing full Imperium repository and its precedent memory.
- `NEW_REALITY`: the active NewGen runtime core rooted at `E:/IMPERIUM_NEW_GENERATION_NEW_REALITY`.

The task must create a separate local git repository for New Reality from `E:/IMPERIUM/IMPERIUM_NEW_GENERATION`. The existing old repository must remain intact. Any later removal of `IMPERIUM_NEW_GENERATION` from Ancient Empire is out of scope for this task and requires separate review.

## Required source and target paths

Source:

```text
E:/IMPERIUM/IMPERIUM_NEW_GENERATION
```

New active root:

```text
E:/IMPERIUM_NEW_GENERATION_NEW_REALITY
```

Optional evidence root:

```text
E:/IMPERIUM_ANCIENT_EMPIRE_EVIDENCE
```

## Required behavior

1. Record current PC repo truth for `E:/IMPERIUM`:
   - branch;
   - HEAD;
   - origin/master or default remote head if available;
   - worktree dirty state;
   - source folder existence and size estimate;
   - key top-level folder list.

2. Freeze Ancient Empire reference without destructive mutation:
   - write `ancient_empire_freeze_receipt.json`;
   - include current HEAD, intended reference commit if available, source root, and no-deletion confirmation;
   - preserve the old repo as archaeology and precedent memory.

3. Scan `IMPERIUM_NEW_GENERATION` for external dependencies before copy:
   - absolute paths;
   - parent directory references;
   - references to old root names;
   - symlinks/junctions;
   - scripts importing or reading outside NewGen;
   - large runtime/artifact folders that should not be copied or should be marked as runtime.

4. Create `E:/IMPERIUM_NEW_GENERATION_NEW_REALITY` safely:
   - block if target exists and is non-empty unless Owner explicitly admits reuse;
   - copy only the NewGen active core, not the entire old repository;
   - preserve relative paths;
   - avoid copying git internals from the old repo.

5. Initialize a new local git repository in New Reality:
   - prefer branch name `master` unless local git policy strongly requires `main`;
   - set a clean first commit with message like `NEW_REALITY: initialize active NewGen core`;
   - do not push unless Owner has already created/authorized a remote for New Reality.

6. Add New Reality root contracts:
   - `README.md`;
   - `AGENTS.md`;
   - `NEW_REALITY_SCOPE_LOCK.md`;
   - `EPOCH_MANIFEST.json`;
   - `ANCIENT_EMPIRE_REFERENCE.md`;
   - `SALVAGE_REQUEST_TEMPLATE.json`.

7. Produce report and receipts under a task report directory inside New Reality:

```text
REPORTS/TASK-NEWGEN-PC-NEW-REALITY-SEPARATE-REPO-ANCIENT-EMPIRE-FREEZE-PC-V0_1/
```

8. Validate:
   - New Reality root exists;
   - local git repo exists;
   - initial commit exists;
   - root contracts exist;
   - source NewGen still exists in old repo;
   - old repo was not deleted or rewritten;
   - external dependency scan completed;
   - no forbidden paths were written except declared output roots.

## Non-goals

This task must not:

- delete any old repository content;
- remove `IMPERIUM_NEW_GENERATION` from the old repository;
- create or push a new GitHub repository unless Owner explicitly provides credentials/remote and asks for it;
- sync VM2 or VM3 into New Reality;
- implement Throne runtime;
- implement Custodes;
- perform broad salvage from Ancient Empire;
- rewrite history.

## Required final answer

Use the strict 4-part final answer:

1. Step name
2. Step verdict
3. Commit links or local commit identifiers with short labels
4. Exactly 3-4 short Russian Owner comments
