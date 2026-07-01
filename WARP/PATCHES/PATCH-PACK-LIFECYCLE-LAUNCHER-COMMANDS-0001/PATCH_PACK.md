# PATCH PACK — PATCH-PACK-LIFECYCLE-LAUNCHER-COMMANDS-0001

status: `WARP_CANDIDATE`  
owner: `ASTRONOMICON + SUPPORT/LAUNCHER`  
mode: `OPERATOR_COMMANDS`

## Purpose

Add terminal operator commands for Patch Pack lifecycle validation.

## Commands

```text
patch preflight <PATCH_ID>
patch scope <PATCH_ID>
patch smoke <PATCH_ID>
patch smoke-all
patch smoke-summary
patch smoke-partial
patch smoke-closed
patch lifecycle <PATCH_ID>
patch lifecycle-all
```

## Expected verdict

```text
PASS_PATCH_LIFECYCLE_LAUNCHER_COMMANDS_READY
```

## Not claimed

```text
patch execution
Custodes trust
Throne verdict
```
