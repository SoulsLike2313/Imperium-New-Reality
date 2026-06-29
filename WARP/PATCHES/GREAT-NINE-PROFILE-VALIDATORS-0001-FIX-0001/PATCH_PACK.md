# PATCH PACK — GREAT-NINE-PROFILE-VALIDATORS-0001-FIX-0001

status: `WARP_FIX_CANDIDATE`
mode: `MEASURE_ONLY`
primary_organ: `THRONE`
fixes: `GREAT-NINE-PROFILE-VALIDATORS-0001`

## Problem

`GREAT-NINE-PROFILE-VALIDATORS-0001` declared required organ slots, but several slots were empty directories.

Git/zip do not preserve empty directories reliably.

The first live run failed correctly:

```text
ASTRONOMICON profile validator = FAIL_PROFILE_BASELINE
Missing dir: RECEIPTS
Missing dir: TUI
Missing dir: DASHBOARDS
Missing dir: EYES
Missing dir: LESSONS
Missing dir: NEGATIVE_LESSONS
```

## Fix

Add `.gitkeep` to all empty required slots for all Great Nine organs, both:

```text
ORGANS/<ORGAN>/<SLOT>/.gitkeep
```

and inside original patch provenance:

```text
WARP/PATCHES/GREAT-NINE-PROFILE-VALIDATORS-0001/FILES_TO_LAND/ORGANS/<ORGAN>/<SLOT>/.gitkeep
```

## Why this is correct

The validator was right to fail.

A required slot is not real if it disappears during transport.

This fix makes slot existence transport-stable and git-trackable.

## Expected result

After this fix, rerun:

```powershell
pwsh WARP/PATCHES/GREAT-NINE-PROFILE-VALIDATORS-0001/RUN_GREAT_NINE_PROFILE_VALIDATORS.ps1
```

Expected:

```text
PASS_PROFILE_BASELINE for all 9 organs
PASS_GREAT_NINE_PROFILE_BASELINE from Throne
```
