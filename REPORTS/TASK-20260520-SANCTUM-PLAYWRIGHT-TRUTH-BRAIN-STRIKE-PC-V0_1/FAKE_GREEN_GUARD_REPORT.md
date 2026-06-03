# Fake Green Guard Report

## Objective
Verify that Sanctum does not pretend all organs are fully connected.

## Truth Result
- Connected: `MECHANICUS_AGENT` only.
- Placeholder: `ADMINISTRATUM_AGENT`, `OFFICIO_AGENTIS_AGENT`, `ASTRONOMICON_AGENT`, `INQUISITION_AGENT`, `DOCTRINARIUM_AGENT`, `STRATEGIUM_AGENT`, `SCHOLA_IMPERIALIS_AGENT`.
- Locked: `CUSTODES`, `THRONE`.

## Guard Checks
- UI truth counters match API `global_truth` counters.
- Zone chips show explicit status and truth mode labels.
- Placeholder/locked organs do not expose fake live content in center evidence/reports panels.
- Mechanicus remains the only real connected lane.

## Evidence
- `POST_PLAYWRIGHT/PLAYWRIGHT_TRUTH_AUDIT_POST.json`
- `POST_PLAYWRIGHT/screenshots/05_failure_gap_placeholder_mode.png`
- `POST_PLAYWRIGHT/screenshots/06_right_truth_panel.png`
