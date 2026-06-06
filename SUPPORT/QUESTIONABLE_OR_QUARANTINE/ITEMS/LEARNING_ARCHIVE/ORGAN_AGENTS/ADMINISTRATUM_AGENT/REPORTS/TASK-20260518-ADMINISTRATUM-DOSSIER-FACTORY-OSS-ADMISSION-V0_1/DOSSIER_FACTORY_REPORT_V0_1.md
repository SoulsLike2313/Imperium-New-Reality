# Dossier Factory Report V0.1

## Target output contract
- ZIP name pattern:
  - `ADMINISTRATUM_DOSSIER_<TASK_ID>.zip`
- Required internal structure:
  - `MANIFEST.json`
  - `SHA256SUMS.txt`
  - `README.md`
  - `machine/*.json`
  - `reports_en/*.md`
  - `owner_ru/OWNER_DOSSIER_RU.pdf` (or fallback markdown when backend missing)
  - `evidence/*`

## Builder implementation
- Entrypoint command:
  - `python .../administratum_agent_runner.py build-dossier --task-id TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1`
- Module:
  - `TOOLS/administratum_dossier_factory.py`
- Integrity:
  - SHA256 manifest generated for staged dossier files.
  - Verify step re-checks required files and hashes.

## Runtime evidence
- build run:
  - `RUN-ADMINISTRATUM-20260518-164612-079fbf`
- verify run:
  - `RUN-ADMINISTRATUM-20260518-164627-4b6060`
- `zip_path`:
  - `E:\IMPERIUM\IMPERIUM_NEW_GENERATION\RUNS\ADMINISTRATUM_AGENT\RUN-ADMINISTRATUM-20260518-164612-079fbf\dossier_factory\ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1.zip`
- `manifest_path`:
  - `E:\IMPERIUM\IMPERIUM_NEW_GENERATION\RUNS\ADMINISTRATUM_AGENT\RUN-ADMINISTRATUM-20260518-164612-079fbf\dossier_factory\ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1\MANIFEST.json`
- `sha256sums_path`:
  - `E:\IMPERIUM\IMPERIUM_NEW_GENERATION\RUNS\ADMINISTRATUM_AGENT\RUN-ADMINISTRATUM-20260518-164612-079fbf\dossier_factory\ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1\SHA256SUMS.txt`
- `verify_report_path`:
  - `E:\IMPERIUM\IMPERIUM_NEW_GENERATION\RUNS\ADMINISTRATUM_AGENT\RUN-ADMINISTRATUM-20260518-164627-4b6060\reports\dossier_verify_report.json`
- owner PDF:
  - `E:\IMPERIUM\IMPERIUM_NEW_GENERATION\RUNS\ADMINISTRATUM_AGENT\RUN-ADMINISTRATUM-20260518-164612-079fbf\dossier_factory\ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1\owner_ru\OWNER_DOSSIER_RU.pdf`
- verify facts:
  - `zip_members_count`: `23`
  - `missing_required`: `[]`
  - `hash_verification.ok`: `true`
  - `owner_pdf_generated`: `true`

## Verdict logic and observed result
- `PASS`: PDF generated and hash verification passes with required files present.
- `WARN`: PDF backend unavailable but fallback markdown present.
- `FAIL`: missing required files or hash mismatch.
- observed build verdict: `PASS`
- observed verify verdict: `PASS`

## Note on global task verdict
- Dossier build/verify pipeline passed.
- Overall task verdict remains `WARN` due global operational warnings (pre-existing dirty state continuation, non-blocking OSS unavailable candidates, first continuity timeout retried successfully).
