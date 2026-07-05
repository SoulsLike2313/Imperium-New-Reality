# PATCH PACK — MECHANICUS-STRICT-BUILD-LANE-RUNNER-EXIT-CODE-FIX-0002

status: `WARP_CANDIDATE`  
owner: `MECHANICUS`  
mode: `RUNNER_EXIT_CODE_FIX_V2_FULL_REPLACEMENT`

## Diagnosis

V1 tried to patch the existing runner by text replacement and failed because the local runner shape did not match the expected exact patterns.

## Fix

V2 replaces the runner file entirely with a v0.2 implementation:

- `TOOL_ID = mechanicus_strict_build_lane_foundation_runner.v0_2_exit_code_consistent`;
- legacy v0.1 marker preserved for existing base validator;
- PASS report + zero blocking failures returns exit 0;
- FAIL report returns exit 1;
- compact ASCII-safe stdout summary;
- full JSON/Markdown reports still written to files.

## Boundary

This does not weaken build proof. It removes protocol noise and avoids fragile text patching.
