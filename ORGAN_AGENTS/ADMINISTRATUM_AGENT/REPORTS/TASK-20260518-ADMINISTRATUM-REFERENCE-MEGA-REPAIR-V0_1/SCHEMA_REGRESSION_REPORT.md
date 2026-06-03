# Schema Regression Report

## Implemented

New command: `schema-regression`.

The gate validates:

- `--plain-json status`;
- `--plain-json doctor-rich`;
- `--plain-json doctor-oss`;
- `--plain-json recent`;
- command receipt shape;
- freelance valid sample;
- freelance malformed sample;
- latest dossier manifest/no-PDF status when a dossier exists.

`jsonschema` is optional. The current implementation uses stdlib fallback checks and reports dependency status explicitly.

## Evidence

- `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-184633-f96489/reports/schema_regression_report.json`

Initial result: `PASS_WITH_WARNINGS` because the latest legacy dossier at that time contained a PDF.

Post-dossier result:

- `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-185615-185e48/reports/schema_regression_report.json`

Result: `PASS`, failed `0`, warnings `0`.
