# TASKPACK_LANGUAGE_ADMISSION_MATRIX

Status: `CANDIDATE_NOT_CANON`
Owner organ: `Astronomicon`
Support organs: Inquisition, Officio Agentis, Mechanicus

## Purpose

Define taskpack intake language and encoding gates before task registration is admitted.

## Criteria

### TLA-01
- Criterion ID: `TLA-01_MANIFEST_LANGUAGE_POLICY_REQUIRED`
- Owner organ: `ASTRONOMICON`
- Evidence required: `TASKPACK_ADMISSION_RECEIPT.json` with language gate fields.
- PASS logic: manifest includes language policy with Officio-routed runtime lane.
- WARN logic: policy exists but is partially explicit and non-blocking under legacy intake mode.
- BLOCK logic: policy missing, malformed, or owner runtime lane bypasses Officio.
- Cap mapping: `CAP_ASTRONOMICON_ADMISSION_LANGUAGE_GATE_MISSING`, `CAP_OWNER_LANGUAGE_NOT_ROUTED_THROUGH_OFFICIO`.
- Remediation path: fix manifest language policy fields and re-register.

### TLA-02
- Criterion ID: `TLA-02_ROOT_FILE_ENCODING_AND_LANGUAGE_GUARD`
- Owner organ: `ASTRONOMICON`
- Evidence required: intake gate warnings + fixture outputs.
- PASS logic: required root files are UTF-8 no BOM, English-only, no replacement/mojibake signature.
- WARN logic: legacy taskpack warning mode only (no clean pass claim).
- BLOCK logic: root files contain BOM, Cyrillic, replacement character, or mojibake signature.
- Cap mapping: `CAP_UTF8_BOM_NOT_DETECTED`, `CAP_NON_ENGLISH_TASKPACK_INTERNAL_TEXT`, `CAP_REPLACEMENT_CHARACTER_NOT_DETECTED`, `CAP_MOJIBAKE_SIGNATURE_NOT_DETECTED`.
- Remediation path: repair root files and rerun intake.

### TLA-03
- Criterion ID: `TLA-03_ADMISSION_RECEIPT_LANGUAGE_GATE_FIELDS`
- Owner organ: `ASTRONOMICON`
- Evidence required: admission receipt contains `language_gate_passed` and cap list.
- PASS logic: receipt records gate status and related caps.
- WARN logic: receipt has gate status but partial detail.
- BLOCK logic: receipt omits language gate result while claiming admission pass.
- Cap mapping: `CAP_ASTRONOMICON_ADMISSION_LANGUAGE_GATE_MISSING`.
- Remediation path: restore receipt contract and rerun registration.
