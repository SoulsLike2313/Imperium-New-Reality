# Dossier No-PDF Policy Report

## Repair

Default dossier ZIP generation now writes markdown/json only:

- `owner_ru/OWNER_SUMMARY_RU.md`;
- `machine/*.json`;
- `reports_en/*.md`;
- `evidence/*`;
- `README.md`;
- `MANIFEST.json`;
- `SHA256SUMS.txt`.

PDF generation is no longer called by the default dossier factory path. `verify-dossier` scans ZIP members and fails a default dossier containing `.pdf`.

## Evidence Before New Build

`schema-regression` detected a legacy old dossier containing `owner_ru/OWNER_DOSSIER_RU.pdf`; this was reported as a legacy warning rather than hidden.

## Final Proof

After receipt creation, this task ran:

- `build-dossier --task-id TASK-20260518-ADMINISTRATUM-REFERENCE-MEGA-REPAIR-V0_1`;
- `verify-dossier --latest`.

Evidence:

- build report: `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-185524-182acc/reports/dossier_factory_build_report.json`
- verify report: `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-185531-3b3a05/reports/dossier_verify_report.json`
- zip: `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-185524-182acc/dossier_factory/ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-REFERENCE-MEGA-REPAIR-V0_1.zip`

Result: `PASS`, `default_dossier_has_pdf: false`, `pdf_members: []`, `hash_verification.ok: true`.

Tamper test:

- `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-185609-4e42b6/reports/dossier_verify_report.json`

Result: `FAIL` as expected with `hash_verification_failed`.
