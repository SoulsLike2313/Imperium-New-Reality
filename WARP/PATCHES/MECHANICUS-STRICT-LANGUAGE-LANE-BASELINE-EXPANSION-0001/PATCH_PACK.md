# PATCH PACK — MECHANICUS-STRICT-LANGUAGE-LANE-BASELINE-EXPANSION-0001

status: `WARP_CANDIDATE`  
owner: `MECHANICUS + CUSTODES + THRONE`  
mode: `STRICT_LANGUAGE_LANE_BASELINE_EXPANSION`

## Purpose

Expand baseline dispatch for active language lanes.

The previous readout showed active lanes still foundation-only:

```text
PowerShell
Rust
Node frontend
CSS UI
```

This patch gives them lane-specific baseline evidence without claiming strict build/lint/type/security success.

## Boundary

```text
Baseline expansion is not 100% clean.
cargo check is not claimed.
npm build is not claimed.
eslint/stylelint/mypy/PSScriptAnalyzer are not claimed.
```
