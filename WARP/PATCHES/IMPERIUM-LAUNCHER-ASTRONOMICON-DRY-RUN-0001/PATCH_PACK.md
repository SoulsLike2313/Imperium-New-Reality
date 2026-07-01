# PATCH PACK — IMPERIUM-LAUNCHER-ASTRONOMICON-DRY-RUN-0001

status: `WARP_CANDIDATE`  
owner: `ASTRONOMICON` + `SUPPORT/LAUNCHER`  
mode: `DRY_RUN_ONLY`

## Purpose

Create the first terminal launcher skeleton and first Astronomicon dry-run intake.

It can register machine-readable tasks from raw Owner text, but it cannot execute them.

## Commands

```text
pwsh SUPPORT/LAUNCHER/imperium.ps1 status
pwsh SUPPORT/LAUNCHER/imperium.ps1 organs
pwsh SUPPORT/LAUNCHER/imperium.ps1 organ astronomicon status
pwsh SUPPORT/LAUNCHER/imperium.ps1 patch list
pwsh SUPPORT/LAUNCHER/imperium.ps1 patch inspect <PATCH_ID>
pwsh SUPPORT/LAUNCHER/imperium.ps1 intake dry-run "<owner text>"
```

## Expected verdict

```text
PASS_LAUNCHER_AND_ASTRONOMICON_DRY_RUN_READY
```

## Hard law

Dry-run intake may create task documents and receipts.

It must not execute, mutate target products, run patch packs, claim trust, or claim Throne verdict.
