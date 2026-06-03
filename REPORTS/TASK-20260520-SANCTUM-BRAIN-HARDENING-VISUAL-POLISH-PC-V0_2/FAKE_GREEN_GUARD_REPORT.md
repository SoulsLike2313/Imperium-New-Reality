# Fake Green Guard Report

## Truth Model
- REAL: `MECHANICUS_AGENT`
- PLACEHOLDER: `ADMINISTRATUM_AGENT`, `OFFICIO_AGENTIS_AGENT`, `ASTRONOMICON_AGENT`, `INQUISITION_AGENT`, `DOCTRINARIUM_AGENT`, `STRATEGIUM_AGENT`, `SCHOLA_IMPERIALIS_AGENT`
- LOCKED: `CUSTODES`, `THRONE`

## Guard Checks
- Right truth panel counters match `/api/state`.
- Organ-card status badges and truth-mode chips match backend status.
- Placeholder/locked nodes do not claim connected runtime lanes.

## Evidence
- `POST_PLAYWRIGHT/PLAYWRIGHT_TRUTH_AUDIT_POST.json`
- `POST_PLAYWRIGHT/screenshots/02_active_brain_or_organ_zone.png`
- `POST_PLAYWRIGHT/screenshots/06_right_truth_panel.png`
