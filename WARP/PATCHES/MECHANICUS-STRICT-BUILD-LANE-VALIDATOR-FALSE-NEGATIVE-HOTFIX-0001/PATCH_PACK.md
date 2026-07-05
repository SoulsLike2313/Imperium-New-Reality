# PATCH PACK — MECHANICUS-STRICT-BUILD-LANE-VALIDATOR-FALSE-NEGATIVE-HOTFIX-0001

status: `WARP_CANDIDATE`  
owner: `MECHANICUS`  
mode: `VALIDATOR_FALSE_NEGATIVE_HOTFIX`

## Diagnosis

The strict build lane report showed:

```text
verdict: PASS_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION
blocking_failure_count: 0
all detected targets ok: True
```

But the foundation validator returned FAIL.

## Fix

Update `validate_mechanicus_strict_build_lane_foundation.py` to v0.2:

- report verdict PASS is primary truth;
- blocking failures must be zero;
- every detected target must be ok;
- every detected target must have command/compile receipt;
- dependency installation must not be attempted;
- planner must no longer report `STRICT_BUILD_LANE_REQUIRED`.

## Boundary

This does not weaken build proof. It fixes a validator false negative.
