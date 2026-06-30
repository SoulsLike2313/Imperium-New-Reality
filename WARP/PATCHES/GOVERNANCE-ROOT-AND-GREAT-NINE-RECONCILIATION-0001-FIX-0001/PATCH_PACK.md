# PATCH PACK — GOVERNANCE-ROOT-AND-GREAT-NINE-RECONCILIATION-0001-FIX-0001

status: `WARP_FIX_CANDIDATE`  
parent: `GOVERNANCE-ROOT-AND-GREAT-NINE-RECONCILIATION-0001`  
mode: `ROOT_DRIFT_FIX`

## Reason

The parent patch correctly failed with:

```text
Root contains non-canon entries: dirs=.imperium_patch_backups
```

This is a good fail. The Root Law caught an unregistered hidden backup zone.

## Decision

`.imperium_patch_backups/` is root drift.

It moves to:

```text
SUPPORT/QUARANTINE/ROOT_PATCH_BACKUPS_PENDING_BACKUP_POLICY/.imperium_patch_backups/
```

## Evidence preservation

The parent failed run already moved large root drift:

```text
relocation_count: 2083
```

This fix reads the existing failed-run relocation registry, merges it with the new `.imperium_patch_backups` relocation evidence, and writes a final PASS receipt.

## Expected verdict

```text
PASS_REALITY_ROOT_CANON_WITH_TRANSITIONAL_DEBT
```
