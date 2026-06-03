# Red / Black Attack Matrix Report

| # | Attack angle | Severity | Reproduction | Evidence | Fix recommendation | Status |
|---|---|---|---|---|---|---|
| 1 | Fake green | Critical | Compare UI truth claims with `/api/state` organ statuses | `POST_PLAYWRIGHT/PLAYWRIGHT_TRUTH_AUDIT_POST.json` | Keep strict real/placeholder/locked mapping in UI | Fixed now |
| 2 | Broken buttons | High | Click mandatory action set and inspect history | `POST_PLAYWRIGHT/PLAYWRIGHT_TRUTH_AUDIT_POST.json` | Keep allowlisted action IDs and history verification | Fixed now |
| 3 | Stale paths | High | Trigger report/screenshots path actions and validate paths exist | `POST_PLAYWRIGHT/PLAYWRIGHT_TRUTH_AUDIT_POST.json` | Keep path existence checks in audit harness | Fixed now |
| 4 | Misleading counts | High | Compare right-panel counters with API `global_truth` | `POST_PLAYWRIGHT/PLAYWRIGHT_TRUTH_AUDIT_POST.json` | Retain counter truth checks per run | Fixed now |
| 5 | Placeholder pretending real | Critical | Select non-mechanicus zones and inspect center panel behavior | `POST_PLAYWRIGHT/screenshots/05_failure_gap_placeholder_mode.png` | Preserve placeholder/locked fallback text and blocked live content | Fixed now |
| 6 | Weak operator UX | Medium | Review center brain viewport before/after | `BASELINE_PLAYWRIGHT/screenshots/02_active_brain_or_organ_zone.png` and `POST_PLAYWRIGHT/screenshots/02_active_brain_or_organ_zone.png` | Keep brain-centric composition and status coding | Fixed now |
| 7 | Missing live telemetry | Medium | Inspect LIVE terminal and action history updates after clicks | `POST_PLAYWRIGHT/screenshots/03_action_click_result_examples.png` | Keep polling and history feed; consider push transport later | Deferred |
| 8 | Bad viewport focus | Medium | Verify Mechanicus zone refocuses to live/evidence panels | `POST_PLAYWRIGHT/screenshots/04_mechanicus_expanded_view.png` | Keep active zone focus and center tabs | Fixed now |
| 9 | Performance drag | Medium | Headless rAF sample under animation load | `PERFORMANCE_PROBE.json` | Profile in headed mode and reduce expensive paint effects if needed | Deferred |
| 10 | Poor brain metaphor fidelity | Critical | Baseline run fails brain-zone detection | `BASELINE_PLAYWRIGHT/PLAYWRIGHT_TRUTH_AUDIT_BASELINE.json` | Enforce `#brainZoneMap` and neural links in regression audits | Fixed now |
| 11 | No clear zone ownership | Medium | Inspect zone IDs and truth chips per node | `POST_PLAYWRIGHT/screenshots/02_active_brain_or_organ_zone.png` | Keep per-zone organ ID and truth-mode chip | Fixed now |
| 12 | Missing evidence links | High | Validate report/screenshot index artifacts | `PLAYWRIGHT_SCREENSHOTS_INDEX.json` | Maintain index generation in task bundle | Fixed now |
| 13 | Unsafe action patterns | High | Verify blocked/unallowlisted model remains enforced server-side | `IMPERIUM_NEW_GENERATION/SANCTUM_MINI/api/actions.py` + post audit | Keep allowlist-only execution model | Fixed now |
| 14 | Unclear fallbacks | Medium | Inspect placeholder/locked message clarity in EVIDENCE/REPORTS | `POST_PLAYWRIGHT/screenshots/05_failure_gap_placeholder_mode.png` | Keep explicit fallback copy in RU/EN | Fixed now |
| 15 | Missing roadmap | High | Check presence of OSS path and growth plan docs | `OSS_RESEARCH_REPORT.md`, `OSS_ADMISSION_MATRIX.json` | Continue with near/medium/future admission phases | Fixed now |
