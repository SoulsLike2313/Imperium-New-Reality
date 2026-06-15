# Administratum Bundle Gate Contract V0.2

Status: `CANDIDATE_V0_2`
Owner organ: `ADMINISTRATUM`

## Purpose

Administratum V0.2 is the New Reality report bundle admission gate for
composition and minimal receipt schema validation. It extends V0.1 by proving
that required evidence classes are not accepted merely because matching
filenames exist.

## Pass Behavior

The checker may return:

- `BUNDLE_COMPOSITION_PASS`
- `BUNDLE_SCHEMA_PASS`
- `BUNDLE_PACKAGING_PASS`

A report folder reaches `BUNDLE_SCHEMA_PASS` only when:

- all required V0.1 composition classes are present;
- required JSON evidence parses as UTF-8 JSON;
- required schema fields such as `task_id` are present and match the folder
  task id supplied to the checker;
- active root fields, when present, resolve to
  `E:/IMPERIUM_NEW_GENERATION_NEW_REALITY`;
- no-Ancient receipts include core mutation/write fields;
- bundle SHA fields match the adjacent `task_report_bundle.zip` when such a
  field is present;
- adjacent self-reference proofs are declared in `adjacent_receipts_manifest.json`.

The V0.2 packager may create `task_report_bundle.zip` only after the gate returns
`BUNDLE_SCHEMA_PASS`.

## Block Behavior

The checker must return `BUNDLE_SCHEMA_BLOCK` or `BUNDLE_COMPOSITION_BLOCK` when
required classes are absent, malformed JSON is encountered, required fields are
missing, `task_id` values mismatch, Ancient is represented as the active root,
adjacent proof references are undeclared, bundle SHA values are stale, or
machine bundle text carries Owner-facing Russian without an Officio localization
exception.

The packager must not leave a final bundle behind after a block. It writes a
missing-items and invalid-fields digest instead.

## Authority Boundary

Administratum V0.2 is structural and schema-level only. It must not claim:

- `SEMANTIC_TRUTH_PASS`
- `CUSTODES_ADMISSION_PASS`
- `INQUISITION_CLEAN_PASS`
- `NO_FAKE_GREEN_FULL_PASS`

Those claims remain owned by later Inquisition, Custodes, Throne, or semantic
admission layers. A V0.2 pass means the report bundle has required classes and
minimal field integrity; it is not a deep truth seal.

## Self-Reference Limit

The final bundle, final SHA sums, final gate receipt, final packager receipt,
and final git/remote closure receipts may remain adjacent to the bundle. They
must be listed in `adjacent_receipts_manifest.json` with
`ADJACENT_SELF_REFERENCE_LIMIT` and covered by `SELF_REFERENCE_LIMIT.md`.
