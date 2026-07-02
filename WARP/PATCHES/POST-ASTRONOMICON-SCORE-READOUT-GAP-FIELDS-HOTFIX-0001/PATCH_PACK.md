# PATCH PACK — POST-ASTRONOMICON-SCORE-READOUT-GAP-FIELDS-HOTFIX-0001

status: `WARP_CANDIDATE`  
owner: `THRONE`  
mode: `READOUT_FAKE_GREEN_HOTFIX`

## Purpose

Fix score-readout false green.

The previous readout passed, but global current gap fields appeared as `None`:

```text
core_readiness_score: None
throne_readiness_score: None
great_nine_readiness_score: None
...
```

while the refreshed Throne gap runner clearly emitted those values.

## Fix

The readout now uses recursive field extraction and the validator requires core/great-nine fields to be non-null before PASS.

## Expected verdict

```text
PASS_POST_ASTRONOMICON_SCORE_READOUT_READY
```

## Not claimed

```text
Great Nine assembled
Core v1 ready
visual work resumed
local Crown order integrated into global stage scoring
```
