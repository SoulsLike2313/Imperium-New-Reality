# OFFICIO_LANGUAGE_AUTHORITY_V0_1

Status: `CANDIDATE_NOT_CANON`
Owner organ: `OFFICIO_AGENTIS`

## Purpose

Define authoritative language behavior across IMPERIUM runtime output and canonical artifacts.

## Core policy

1. Canonical internal taskpacks and machine-readable artifacts are English-only.
2. Canonical text artifacts must use UTF-8 without BOM.
3. Runtime owner-facing Russian is allowed only when routed through Officio role/runtime settings.
4. Servitor live progress can be Russian only as owner-facing runtime communication.
5. Internal taskpacks must not contain ad hoc Russian owner prose.
6. Future Russian UI text must live in controlled localization resources (`locales`, `i18n`, `translations`, `LOCALIZATION`).

## Applies to canonical artifact classes

- `JSON`, `MD`, `TXT`, `PY`, `PS1`, `YAML`, `YML`, `CSV`, `TOML`.

## Forbidden in canonical internal artifacts

- Cyrillic text outside controlled localization resources;
- UTF-8 BOM;
- replacement character (`U+FFFD`);
- named mojibake or mixed-encoding signatures;
- runtime owner-facing Russian prose embedded in machine policy/contracts/receipts.

## Exception lane

- Runtime owner-facing summaries may be Russian only with explicit Officio runtime authorization.
- Such files must not be treated as machine policy or instruction source.

## Cap mapping

- `CAP_LANGUAGE_AUTHORITY_MISSING`
- `CAP_OWNER_LANGUAGE_NOT_ROUTED_THROUGH_OFFICIO`
- `CAP_NON_ENGLISH_TASKPACK_INTERNAL_TEXT`
- `CAP_CANONICAL_ARTIFACT_CONTAINS_CYRILLIC`
- `CAP_UTF8_BOM_NOT_DETECTED`
- `CAP_REPLACEMENT_CHARACTER_NOT_DETECTED`
- `CAP_MOJIBAKE_SIGNATURE_NOT_DETECTED`
- `CAP_LOCALIZATION_EXCEPTION_UNCONTROLLED`
