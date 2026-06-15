# H Contour Patch Backup Hygiene Law v0.1

## Закон

H-contour patch backup, handoff, smoke and temporary operator zones are not source.

A patch application may create backups for rollback, but those backups must not be tracked by git and must not be transferred to main as project state.

## Required practice

Before every H commit acceptance:

1. run smoke relevant to the patch;
2. run git status/diff review;
3. run Inquisition patch backup hygiene gate;
4. verify no local-only root is tracked;
5. commit only source/policy/index/gate changes.

## Source vs local operator zones

Source may contain:

- policies;
- tool passports;
- source code;
- schemas;
- small fixtures with manifest/source exception;
- Data Atlas cards and machine-readable indexes intended for source.

Source must not contain:

- `.imperium_patch_backups/`;
- `_LOCAL_HANDOFF/`;
- smoke vaults;
- temporary patch extraction folders;
- raw screenshots/logs/traces unless converted into fixture/evidence-vault pack with manifest.

## Handoff implication

Future patch ZIP apply scripts should store rollback backups outside the repository by default, for example under `E:\_LOCAL_HANDOFF\PATCH_BACKUPS\...`, or ensure the repo-local backup root is already ignored before any operator can run `git add -A`.
