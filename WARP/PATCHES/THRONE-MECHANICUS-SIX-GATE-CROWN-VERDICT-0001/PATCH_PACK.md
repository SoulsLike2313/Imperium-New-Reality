# THRONE-MECHANICUS-SIX-GATE-CROWN-VERDICT-0001

## Purpose

Crown Mechanicus at baseline assembly level after six Mechanicus gates reached PASS_BASELINE and Custodes prosecutor gate accepted the baseline.

## Claim boundary

This patch may claim `MECHANICUS_ASSEMBLED_BASELINE_THRONE_CROWNED_NOT_CORE_V1_COMPLETE`.

It must not claim:
- Core v1 completion;
- real execution gateway readiness;
- local model membrane readiness;
- Great Nine completion.

## Files to land

- ORGANS/MECHANICUS/MANIFEST.json
- ORGANS/MECHANICUS/MATRICES/MECHANICUS_CURRENT_TRUTH_INDEX_V0_1.json
- ORGANS/THRONE/LAWS/THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_LAW_V0_1.json
- ORGANS/THRONE/MATRICES/THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT_MATRIX_V0_1.json
- ORGANS/THRONE/TOOLS/build_throne_mechanicus_six_gate_crown_verdict.py
- ORGANS/THRONE/VALIDATORS/validate_throne_mechanicus_six_gate_crown_verdict.py

## Run

```powershell
pwsh WARP/PATCHES/THRONE-MECHANICUS-SIX-GATE-CROWN-VERDICT-0001/RUN_THRONE_MECHANICUS_SIX_GATE_CROWN_VERDICT.ps1
```
