# Validation Report

- task_id: TASK-20260520-NEWGEN-SANCTUM-SCOPE-REPAIR-MECHANICUS-PANEL-PC-V0_5
- generated_at_utc: 2026-05-20T16:49:44.4538743Z
- overall_verdict: WARN

## Gates
- GATE_SCOPE_NEW_GENERATION_ONLY: PASS
  - note: Current writes are contained in IMPERIUM_NEW_GENERATION. Historical committed contamination remains WARN only.
- GATE_REPORT_ROOT: PASS
  - note: Report root is under IMPERIUM_NEW_GENERATION/REPORTS.
- GATE_MECHANICUS_CLICK: PASS
  - note: Mechanicus click selects organ and opens Live operator panel.
- GATE_OPERATOR_PANEL_NOT_RAW_TERMINAL: PASS
  - note: RAW stream hidden by default and available through explicit RAW toggle.
- GATE_RESPONSIVE_1366: PASS
  - note: 1366/1600/1920 checks show no horizontal overflow and key zones visible.
- GATE_SSE_TRUTH: PASS
  - note: UI SSE label and event stream proof are aligned.
- GATE_PLACEHOLDERS_HONEST: PASS
  - note: Only Mechanicus stays REAL; placeholders/locked remain honest.
- GATE_GIT_CLEAN_FINAL: WARN
  - note: Task changes are not committed in this run; owner can commit after review.

## Scope Note
- Historical committed contamination under ORGANS is not rewritten in this task and remains owner-managed cleanup scope.
