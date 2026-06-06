# ADMINISTRATUM DOSSIER FACTORY CONTRACT V0.1

## Purpose
Define a reproducible dossier package for large Administratum outputs.

## Canonical truth
- Canonical truth remains English markdown reports and JSON receipts.
- Default exchange dossiers are markdown/json ZIP packages.
- PDF artifacts are optional external renders only and must not be included in the default dossier ZIP.

## Required package structure
- `ADMINISTRATUM_DOSSIER_<RUN_OR_TASK_ID>.zip`
- `MANIFEST.json`
- `SHA256SUMS.txt`
- `README.md`
- `machine/` with machine-first JSON files
- `reports_en/` with canonical English reports
- `owner_ru/` with Russian Owner markdown summary
- `evidence/` with indexed captures

## Required machine fields
Manifest must include:
- task id / run id / timestamp
- git truth (head/branch/dirty)
- verdict
- warnings / limitations / unverified
- included files and hashes
- no-PDF default policy status

## Safety
- No private payload content export by default.
- Runtime artifacts must remain under RUNS root.
- No unrelated organ mutation.
- `verify-dossier` must fail a default dossier ZIP that contains any `.pdf` member.
