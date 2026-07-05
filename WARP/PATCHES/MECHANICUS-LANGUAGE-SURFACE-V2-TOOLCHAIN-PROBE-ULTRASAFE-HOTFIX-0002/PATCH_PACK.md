# PATCH PACK — MECHANICUS-LANGUAGE-SURFACE-V2-TOOLCHAIN-PROBE-ULTRASAFE-HOTFIX-0002

status: `WARP_CANDIDATE`  
owner: `MECHANICUS`  
mode: `ULTRASAFE_TOOLCHAIN_PROBE_HOTFIX`

## Purpose

Fix the failed previous hotfix.

The previous nonblocking probe still failed to run/write the report on the user's host:

```text
nonblocking toolchain probe did not run/write report
```

## Fix

Replace `prove_toolchains.py` with an ultrasafe probe:

- only version probes;
- no npm build;
- no cargo check;
- no audit fix;
- no dependency mutation;
- top-level emergency report if the probe itself throws;
- missing tools are capability debt;
- no 100% clean claim.

## Expected verdicts

```text
PASS_MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_VALIDATOR_DISPATCH_READY
PASS_MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_PROBE_ULTRASAFE_HOTFIX_READY
```
