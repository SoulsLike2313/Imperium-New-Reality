# PATCH PACK — ROOT-QUARANTINE-LONGPATH-COMPACTION-0001-FIX-0001

status: `WARP_FIX_CANDIDATE`  
parent: `ROOT-QUARANTINE-LONGPATH-COMPACTION-0001`  
mode: `UNIVERSAL_LONGPATH_BUNDLE`

## Reason

The parent compactor was too narrow.

It returned:

```text
compacted_count: 0
long_paths_after: 126
non_bundle_long_paths_after: 126
```

Meaning: long paths existed, but not under the guessed prefixes.

## Fix

Compact every visible long path in Reality except:

```text
.git/
SUPPORT/QUARANTINE/LONGPATH_BUNDLE_V0_1/FILES/
__pycache__
*.pyc
```

Bundle destination:

```text
SUPPORT/QUARANTINE/LONGPATH_BUNDLE_V0_1/FILES/<sha-prefix>/<sha256>.blob
```

Original paths are preserved in:

```text
SUPPORT/QUARANTINE/LONGPATH_BUNDLE_V0_1/LONGPATH_BUNDLE_MAP_V0_1.json
ORGANS/ADMINISTRATUM/REGISTRY/LONGPATH_QUARANTINE_COMPACTION_REGISTRY_V0_1.json
```

Restore script:

```text
SUPPORT/QUARANTINE/LONGPATH_BUNDLE_V0_1/RESTORE_LONGPATH_BUNDLE_V0_1.ps1
```

## Expected verdict

```text
PASS_LONGPATH_COMPACTED
```
