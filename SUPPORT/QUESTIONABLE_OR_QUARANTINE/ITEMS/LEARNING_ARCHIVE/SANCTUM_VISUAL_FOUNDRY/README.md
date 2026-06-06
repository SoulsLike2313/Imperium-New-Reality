# SANCTUM VISUAL FOUNDRY

Task scope: `TASK-20260520-NEWGEN-SANCTUM-VISUAL-FOUNDRY-MECHANICUS-CONSOLE-SLICE-V0_1`

This directory contains the first Visual Foundry slice for `IMPERIUM_NEW_GENERATION`.

## Goal

Build a reproducible visual pipeline:

1. Owner intake
2. Visual contract
3. Design tokens
4. Component state manifest
5. Isolated lab
6. Screenshot baselines
7. Validation + receipts + owner report

## Structure

- `OWNER_INTAKE/` owner intent and intake artifacts
- `REFERENCES/` source reference and negative examples
- `CONTRACTS/` visual contract and interpretation card
- `TOKENS/` token JSON and CSS token export
- `COMPONENTS/` component state manifest
- `LAB/` runnable Mechanicus console slice prototype
- `PLAYWRIGHT/` screenshot proof automation
- `SCREENSHOTS/` generated screenshots for evidence
- `REPORTS/` validation and owner-facing reports
- `RECEIPTS/` machine receipts (gate ack, final receipt, KPD)
- `SCHEMAS/` task schemas copied from taskpack

## Quick Start

Open static lab directly:

1. Open `LAB/index.html` in browser

Or run screenshot automation:

1. `cd IMPERIUM_NEW_GENERATION/SANCTUM_VISUAL_FOUNDRY/PLAYWRIGHT`
2. `npm install`
3. `npx playwright install chromium`
4. `npm run screenshots`

