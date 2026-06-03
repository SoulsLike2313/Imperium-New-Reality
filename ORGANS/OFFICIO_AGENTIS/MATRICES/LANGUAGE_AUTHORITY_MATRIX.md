# LANGUAGE_AUTHORITY_MATRIX

Status: `CANDIDATE_NOT_CANON`
Owner organ: `Officio Agentis`
Support organs: Astronomicon, Inquisition, Administratum

## Purpose

Define ownership and enforcement of language lanes:
- owner-facing runtime language;
- canonical machine-artifact language;
- controlled localization exceptions.

## Criteria

### LA-01
- Criterion ID: `LA-01_CANONICAL_ENGLISH_ONLY`
- Owner organ: `OFFICIO_AGENTIS`
- Evidence required: canonical scan report + claim ledger entries.
- PASS logic: canonical internal artifacts are English-only.
- WARN logic: only legacy artifacts contain non-English and are explicitly classified.
- BLOCK logic: new canonical artifact contains non-English text.
- Cap mapping: `CAP_CANONICAL_ARTIFACT_CONTAINS_CYRILLIC`, `CAP_NON_ENGLISH_TASKPACK_INTERNAL_TEXT`.
- Remediation path: isolate source, rewrite to English, re-run filter.

### LA-02
- Criterion ID: `LA-02_RUNTIME_RU_ROUTE_OFFICIO_ONLY`
- Owner organ: `OFFICIO_AGENTIS`
- Evidence required: Officio policy JSON + runtime summary metadata.
- PASS logic: runtime owner-facing Russian appears only through Officio route.
- WARN logic: runtime RU exists in legacy reports and is marked as owner-facing runtime output.
- BLOCK logic: owner-facing Russian is embedded in machine policy/contract/schema.
- Cap mapping: `CAP_OWNER_LANGUAGE_NOT_ROUTED_THROUGH_OFFICIO`.
- Remediation path: move prose to runtime summary lane; keep machine artifacts English.

### LA-03
- Criterion ID: `LA-03_LOCALIZATION_EXCEPTION_CONTROLLED`
- Owner organ: `OFFICIO_AGENTIS`
- Evidence required: localization path markers + exclusion notes in filter report.
- PASS logic: localized text is in controlled localization folders.
- WARN logic: localization resources exist but need stricter metadata.
- BLOCK logic: localization text appears outside controlled folders.
- Cap mapping: `CAP_LOCALIZATION_EXCEPTION_UNCONTROLLED`.
- Remediation path: move localized assets to `locales`/`i18n`/`translations`/`LOCALIZATION`.

## Evidence requirements

- `OFFICIO_LANGUAGE_AUTHORITY_V0_1.md`
- `OFFICIO_LANGUAGE_AUTHORITY_V0_1.json`
- `inquisition_mojibake_filter_report.json`
- `canonical_artifact_language_scan_report.md`
