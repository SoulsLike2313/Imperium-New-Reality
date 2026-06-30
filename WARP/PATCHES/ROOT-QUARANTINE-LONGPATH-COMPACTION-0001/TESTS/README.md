# TESTS — ROOT-QUARANTINE-LONGPATH-COMPACTION-0001

Valid if:

- pre-push long paths under SUPPORT/QUARANTINE are compacted;
- bundle map preserves original path and SHA256;
- root stays: ORGANS, SUPPORT, WARP, _HARNESS plus root governance files;
- no root-level APPLY/manifests return;
- receipt verdict is PASS_LONGPATH_COMPACTED.
