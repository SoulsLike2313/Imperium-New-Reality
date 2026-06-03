# STABLE CANDIDATE LAUNCHPOINTS V0.1

## Stable

- Path: `IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.html`
- URL: `http://127.0.0.1:8765/IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.html`

## Candidate

- Path: `IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_candidate.html`
- URL: `http://127.0.0.1:8765/IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_candidate.html`

## One-Step Helper

```powershell
cd E:\IMPERIUM
powershell -ExecutionPolicy Bypass -File IMPERIUM_NEW_GENERATION/SANCTUM_NG/OPERATOR_COCKPIT/TOOLS/launch_operator_cockpit.ps1 -Mode stable
powershell -ExecutionPolicy Bypass -File IMPERIUM_NEW_GENERATION/SANCTUM_NG/OPERATOR_COCKPIT/TOOLS/launch_operator_cockpit.ps1 -Mode candidate
```

## Safety Boundary

- UI launch only.
- No production orchestration claim.
- No autonomous runtime claim.
