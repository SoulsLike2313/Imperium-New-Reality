# PATCH PACK — RED-BLUE-TEAM-LAUNCHER-SCAN-COMMANDS-0001

status: `WARP_CANDIDATE`  
owner: `ASTRONOMICON + SUPPORT/LAUNCHER`  
mode: `OPERATOR_COMMANDS`

## Purpose

Expose Red/Blue team scan status through launcher commands.

## Expected verdict

```text
PASS_RED_BLUE_TEAM_LAUNCHER_SCAN_COMMANDS_READY
```

## Expected receipt

```text
ORGANS/ASTRONOMICON/RECEIPTS/red_blue_team_launcher_scan_commands_receipt.json
```

## Commands

```text
imperium redblue scan
imperium redblue scan organ <ORGAN>
imperium redblue summary
imperium organ <ORGAN> redblue
```

## Not claimed

```text
red_team_proven
blue_team_proven
Custodes trust
Throne verdict
organ assembled
```
