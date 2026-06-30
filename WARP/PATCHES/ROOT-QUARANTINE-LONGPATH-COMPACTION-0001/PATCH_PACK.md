# PATCH PACK — ROOT-QUARANTINE-LONGPATH-COMPACTION-0001

status: `WARP_FIX_CANDIDATE`  
reason: `pre-push long-path block after GOVERNANCE-ROOT-AND-GREAT-NINE-RECONCILIATION-0001`

## Problem

Patch 5 successfully cleaned root, but moved deep legacy report trees into quarantine while preserving original nested paths.

The pre-push hook blocked push on long paths under:

```text
SUPPORT/QUARANTINE/ROOT_REPORTS_PENDING_HARNESS_INTAKE/
```

## Solution

Compact long quarantine paths into a short SHA256-addressed bundle:

```text
SUPPORT/QUARANTINE/LONGPATH_BUNDLE_V0_1/FILES/<sha256-prefix>/<sha256>.blob
```

The original path is preserved in:

```text
SUPPORT/QUARANTINE/LONGPATH_BUNDLE_V0_1/LONGPATH_BUNDLE_MAP_V0_1.json
ORGANS/ADMINISTRATUM/REGISTRY/LONGPATH_QUARANTINE_COMPACTION_REGISTRY_V0_1.json
```

## Guarantees

- no data deleted;
- SHA256 before/after must match;
- root canon remains clean;
- root transport clutter stays absent;
- long non-bundle paths must be gone.

## Expected verdict

```text
PASS_LONGPATH_COMPACTED
```
