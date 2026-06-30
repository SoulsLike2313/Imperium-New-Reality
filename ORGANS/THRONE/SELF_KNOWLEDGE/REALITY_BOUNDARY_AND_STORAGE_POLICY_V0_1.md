# REALITY BOUNDARY AND STORAGE POLICY V0.1 FIX 0001

patch_id: `GOVERNANCE-ROOT-AND-GREAT-NINE-RECONCILIATION-0001-FIX-0001`  
owner: `THRONE`  
status: `ACTIVE_ROOT_LAW`

## Fix reason

Initial governance run correctly failed because root still contained:

```text
.imperium_patch_backups/
```

This is not allowed Reality root canon.

## Decision

`.imperium_patch_backups/` is useful but not root-canonical.

It must move to:

```text
SUPPORT/QUARANTINE/ROOT_PATCH_BACKUPS_PENDING_BACKUP_POLICY/.imperium_patch_backups/
```

## Root allowed entries

```text
ORGANS/
SUPPORT/
AGENTS.md
README.md
.gitignore
.gitattributes
.editorconfig
```

## Transitional debt

```text
WARP/
_HARNESS/
```

They are tolerated only as transitional debt until externalization:

```text
E:\IMPERIUM_WARP
E:\IMPERIUM_HARNESS
```

## Forbidden active root drift

```text
DOCTRINARIUM/
SCHEMAS/
REPORTS/
.imperium_patch_backups/
APPLY_*.ps1
*_FILE_MANIFEST_SHA256.json
```

## Meaning

The failure was valuable: it proved the Root Law is strict enough to catch a hidden backup zone.
