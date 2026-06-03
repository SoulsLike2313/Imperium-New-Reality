# Canonical Artifact Language Scan Report

Task ID: `TASK-NEWGEN-LANGUAGE-AUTHORITY-AND-MOJIBAKE-FILTER-SPINOFF-PC-V0_1`
Timestamp (UTC): `2026-06-01T05:36:16Z`
Verdict: `WARN`

## Summary

- Total files scanned: `903`
- Total hits: `361`
- Hit type counts: `{'CYRILLIC_IN_CANONICAL_ARTIFACT': 285, 'REPLACEMENT_CHARACTER': 2, 'TASKPACK_ROOT_CYRILLIC': 53, 'UTF8_BOM': 21}`
- Severity counts: `{'WARN': 361}`
- Classification counts: `{'ALLOWED_RUNTIME_OWNER_OUTPUT': 223, 'LEGACY_TO_REMEDIATE': 138}`

## Classification Policy

- `LEGACY_TO_REMEDIATE`: pre-existing violations outside strict task-change scope.
- `ALLOWED_RUNTIME_OWNER_OUTPUT`: runtime owner-facing RU files.
- `ALLOWED_LOCALIZATION`: files under controlled localization folders.
