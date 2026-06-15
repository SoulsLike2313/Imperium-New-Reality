# CLI UX Repair Report

## Repaired

- Recent parser now reads command receipts and check-all reports for command, status, warnings, run id, and key artifact path.
- The current in-progress `recent` run is excluded from its own recent list.
- Rendered operator output compacts paths with `<REPO>`, `<ADMIN>`, `<RUNS>`, and `<RUN>`.
- Shell welcome has explicit Administratum and IMPERIUM text crests.
- Shell `/help <command>` provides targeted command guidance.
- `/shell` inside shell returns `already_in_shell`.
- Unknown shell command uses stdlib `difflib` suggestion.

## Evidence

- recent parser proof: `RUN-ADMINISTRATUM-20260518-185157-32a9b5/reports/recent_runs_report.json`
- `/shell` self-guard: focused shell smoke run returned `already_in_shell`
- typo suggestion: `/soctor-oss` suggested `/doctor-oss`
- path compaction visible in rendered command outputs as `<RUN>`, `<RUNS>`, `<ADMIN>`, and `<REPO>`

## Limitation

True terminal sticky scrolling is not reliable in plain PowerShell. The implemented stable pattern reprints orientation on shell entry and `/help`, with pinned command-hint content in the welcome/help panels.

