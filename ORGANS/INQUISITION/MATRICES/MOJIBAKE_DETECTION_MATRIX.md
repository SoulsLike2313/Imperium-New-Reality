# MOJIBAKE_DETECTION_MATRIX

Status: `CANDIDATE_NOT_CANON`
Owner organ: `Inquisition`
Support organs: Mechanicus, Officio Agentis, Astronomicon

## Purpose

Define global detection and response rules for mojibake signatures and mixed-encoding artifacts.

## Criteria

### MD-01
- Criterion ID: `MD-01_NAMED_SIGNATURE_DETECTION`
- Owner organ: `INQUISITION`
- Evidence required: filter report with signature IDs and path/line references.
- PASS logic: scanner detects all configured mojibake signatures.
- WARN logic: signature detection works but needs broader signature set.
- BLOCK logic: required signature families are missing or undetected in fixture tests.
- Cap mapping: `CAP_MOJIBAKE_SIGNATURE_NOT_DETECTED`.
- Remediation path: update signature registry and rerun fixtures.

### MD-02
- Criterion ID: `MD-02_MIXED_ENCODING_PATTERN_DETECTION`
- Owner organ: `INQUISITION`
- Evidence required: mixed-pattern hits + fixture case results.
- PASS logic: suspicious mixed-encoding patterns are flagged.
- WARN logic: heuristic fired only on legacy artifacts.
- BLOCK logic: mixed encoding in new canonical artifacts is not detected.
- Cap mapping: `CAP_MOJIBAKE_SIGNATURE_NOT_DETECTED`.
- Remediation path: refine heuristics and add negative tests.

### MD-03
- Criterion ID: `MD-03_FILTER_OUTPUT_CONTRACT`
- Owner organ: `INQUISITION`
- Evidence required: JSON report + markdown summary + verdict.
- PASS logic: report includes path, line, hit type, severity, and owner organ.
- WARN logic: report exists but lacks optional enrichments.
- BLOCK logic: report missing required fields or verdict contract.
- Cap mapping: `CAP_MOJIBAKE_FILTER_MISSING`.
- Remediation path: fix report schema and rerun tool.
