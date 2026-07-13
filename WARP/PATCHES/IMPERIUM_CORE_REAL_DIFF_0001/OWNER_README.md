# IMPERIUM_CORE_REAL_DIFF_0001

Phase 5 patch for the existing Reference Corridor WARP.

## Exact target

- WARP HEAD: `f686b90ea0d2e1af06e2243dd543324f5be6c9e3`
- Branch: `servitor/imperium-core-reference-corridor-0001`
- Reality/master HEAD: `281c3a7c8463de7fb64473929fe0ed975f99f595`
- PowerShell: `7.6.2`

## Purpose

Replace the misleading clean/dirty-only Diff card with a measured Git comparison:

`base_head -> current result HEAD`

The UI will show committed file changes, insertions/deletions, renames, binary files, a compact patch preview, and dirty state as a separate boundary.

## Launch

Extract this ZIP into the existing WARP root, then run:

```powershell
cd E:\IMPERIUM_WARPS\IMPERIUM-CORE-REFERENCE-CORRIDOR-0001
pwsh WARP/PATCHES/IMPERIUM_CORE_REAL_DIFF_0001/RUN_IMPERIUM_CORE_REAL_DIFF_0001.ps1
```

## Verify again

```powershell
pwsh WARP/PATCHES/IMPERIUM_CORE_REAL_DIFF_0001/VERIFY_IMPERIUM_CORE_REAL_DIFF_0001.ps1
```

## Restore before commit only

```powershell
pwsh WARP/PATCHES/IMPERIUM_CORE_REAL_DIFF_0001/RESTORE_IMPERIUM_CORE_REAL_DIFF_0001.ps1
```

The patch does not commit, push, merge, land, or change Reality/master.
