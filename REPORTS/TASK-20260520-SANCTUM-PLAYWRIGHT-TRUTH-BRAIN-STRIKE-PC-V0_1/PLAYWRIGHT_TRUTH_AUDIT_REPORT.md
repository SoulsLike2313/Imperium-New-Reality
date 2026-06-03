# Playwright Truth Audit Report

## Scope
- Task: TASK-20260520-SANCTUM-PLAYWRIGHT-TRUTH-BRAIN-STRIKE-PC-V0_1
- Target URL: http://127.0.0.1:8876
- Runs:
  - baseline: FAIL (brain zone layout missing)
  - post: PASS (all required checks passed)

## Mandatory Check Mapping
- Boot/health endpoints: PASS (`/api/health`, `/api/state`, `/api/actions`, `/api/actions/history`, `/api/terminal/history`).
- Visible claims checks: PASS for HEAD/worktree/active organ chips and truth counters.
- Required action checks: PASS for all mandatory actions:
  - `refresh_state`
  - `mechanicus_visual_status`
  - `mechanicus_visual_tools`
  - `mechanicus_visual_check`
  - `mechanicus_visual_identity`
  - `open_or_show_latest_report`
  - `open_or_show_screenshots_folder`
  - `show_api_state_json`
- Truth checks UI vs backend: PASS on post run.
- Screenshot evidence: captured for overview, brain/zone view, mechanicus view, truth panel, gap example, action result example.

## Baseline -> Post Delta
- Baseline gap: `brain_zone_layout_detected=false`.
- Post result: `brain_zone_layout_detected=true`.
- No failed checks remained in post run.

## Evidence Files
- `PLAYWRIGHT_TRUTH_AUDIT_SUMMARY.json`
- `BASELINE_PLAYWRIGHT/PLAYWRIGHT_TRUTH_AUDIT_BASELINE.json`
- `POST_PLAYWRIGHT/PLAYWRIGHT_TRUTH_AUDIT_POST.json`
- `PLAYWRIGHT_SCREENSHOTS_INDEX.json`
