# ENCODING_INTEGRITY_MATRIX

Status: `CANDIDATE_NOT_CANON`
Owner organ: `Inquisition`
Support organs: Mechanicus, Astronomicon, Administratum

## Purpose

Define UTF-8 and text integrity checks that guard canonical artifacts from encoding corruption.

## Criteria

### EI-01
- Criterion ID: `EI-01_UTF8_NO_BOM_REQUIRED`
- Owner organ: `INQUISITION`
- Evidence required: mojibake filter report + admission receipts.
- PASS logic: no UTF-8 BOM in canonical text artifacts.
- WARN logic: only legacy files have BOM and are classified with remediation.
- BLOCK logic: new canonical/taskpack-root text includes BOM.
- Cap mapping: `CAP_UTF8_BOM_NOT_DETECTED`.
- Remediation path: rewrite file as UTF-8 without BOM and rerun checks.

### EI-02
- Criterion ID: `EI-02_REPLACEMENT_CHARACTER_FORBIDDEN`
- Owner organ: `INQUISITION`
- Evidence required: filter hit ledger with line references.
- PASS logic: no replacement character (`U+FFFD`) in canonical artifacts.
- WARN logic: legacy artifacts contain replacement character and are marked for cleanup.
- BLOCK logic: replacement character appears in new canonical artifacts.
- Cap mapping: `CAP_REPLACEMENT_CHARACTER_NOT_DETECTED`.
- Remediation path: repair source encoding, regenerate artifact, rerun scanner.

### EI-03
- Criterion ID: `EI-03_UTF8_DECODE_REQUIRED`
- Owner organ: `INQUISITION`
- Evidence required: scanner decode receipts.
- PASS logic: canonical text artifacts decode as UTF-8.
- WARN logic: decode issues are legacy and classified.
- BLOCK logic: new canonical artifacts fail UTF-8 decode.
- Cap mapping: `CAP_MOJIBAKE_SIGNATURE_NOT_DETECTED`.
- Remediation path: normalize source encoding and replace corrupt bytes.
