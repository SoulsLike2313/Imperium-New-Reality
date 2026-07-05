# PATCH PACK — MECHANICUS-STRICT-BUILD-LANE-RUNNER-EXIT-CODE-FIX-0001

status: `WARP_CANDIDATE`  
owner: `MECHANICUS`  
mode: `RUNNER_EXIT_CODE_FIX`

## Diagnosis

Strict build report was PASS, but process exit code was 1. The likely cause is process-level noise after report write, most likely full JSON stdout/encoding on Windows.

## Fix

- Patch `run_mechanicus_strict_build_lane.py` to v0.2.
- PASS report + zero blocking failures returns exit 0.
- FAIL report returns exit 1.
- stdout/stderr are configured as UTF-8 replace.
- runner prints compact ASCII-safe summary, not full report.
- legacy v0.1 marker remains so the existing base validator still recognizes the runner.

## Boundary

This does not weaken build proof. It removes protocol noise.
