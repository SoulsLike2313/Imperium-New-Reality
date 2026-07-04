# PATCH PACK — IMPERIUM-APP-COCKPIT-MERGE-HOTFIX-FIX-0001

status: `WARP_CANDIDATE`  
owner: `MECHANICUS + APP_PLATFORM`  
mode: `VALIDATOR_MARKER_FIX`

## Purpose

Fix the failed cockpit merge hotfix.

## Diagnosis

The UI was structurally correct enough to continue, but the validator required exact marker text:

```text
Python binds
```

The app copy used:

```text
lets Python bind
```

So the validator failed with:

```text
Mechanicus language codex not represented as in-app room
```

## Fix

Insert the exact `Python binds` marker into the Mechanicus Language Codex room and rerun the previous merge validator.

## Expected verdicts

```text
PASS_IMPERIUM_APP_COCKPIT_MERGE_HOTFIX_READY
PASS_IMPERIUM_APP_COCKPIT_MERGE_HOTFIX_FIX_READY
```
