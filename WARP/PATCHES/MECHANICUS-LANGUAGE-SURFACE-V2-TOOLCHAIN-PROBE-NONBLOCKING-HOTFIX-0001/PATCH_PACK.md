# PATCH PACK — MECHANICUS-LANGUAGE-SURFACE-V2-TOOLCHAIN-PROBE-NONBLOCKING-HOTFIX-0001

status: `WARP_CANDIDATE`  
owner: `MECHANICUS`  
mode: `TOOLCHAIN_PROBE_BASELINE_HOTFIX`

## Purpose

Fix `MECHANICUS-LANGUAGE-SURFACE-V2-TOOLCHAIN-VALIDATOR-DISPATCH-0001`.

## Diagnosis

The previous patch failed on:

```text
toolchain probe failed required tools
```

For this early Mechanicus baseline, that was too strict. The job of the first probe is to measure local reality and record capability debt. It must not pretend missing tools passed, but it also should not block the entire language-surface split.

## Fix

- replaces `prove_toolchains.py` with nonblocking baseline probe;
- unavailable/failed tools become capability debt;
- `npm audit fix --force` remains forbidden;
- no 100% cleanliness is claimed;
- reruns the original validator.

## Expected verdicts

```text
PASS_MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_VALIDATOR_DISPATCH_READY
PASS_MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_PROBE_NONBLOCKING_HOTFIX_READY
```
