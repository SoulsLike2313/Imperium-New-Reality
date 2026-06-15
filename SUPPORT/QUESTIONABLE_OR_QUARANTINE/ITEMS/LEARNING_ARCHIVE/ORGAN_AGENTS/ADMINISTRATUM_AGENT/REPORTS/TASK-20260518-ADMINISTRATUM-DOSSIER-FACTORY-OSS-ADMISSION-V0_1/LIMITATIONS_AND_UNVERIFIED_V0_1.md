# Limitations And Unverified V0.1

## Limitations
- Worktree was already dirty and continuation was Owner-authorized.
- Some OSS tools remain unavailable (`jsonschema`, `reportlab`, `weasyprint`, `ruff`, `duckdb`).
- Schema checks in this slice are parse validation, not semantic schema-instance validation.
- Browser screenshot capture is intentionally not part of this task scope.

## Unverified
- Stress test for concurrent `build-dossier` executions.
- Long-run archive retention policy for large dossier history.
- Cross-machine reproducibility of browser PDF rendering.

## Safety assertions
- No private payload contents were exported.
- Runtime artifacts were generated only under RUNS area.
- No unrelated organs were edited in this slice.

