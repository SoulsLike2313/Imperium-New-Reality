# Administratum Bundle Gate Contract V0.1

Status: `CANDIDATE_V0_1`
Owner organ: `ADMINISTRATUM`

## Purpose

Administratum is the formal exit-side composition gate for New Reality task
report bundles. It blocks bundle creation when required report file classes are
missing.

## Pass behavior

The checker returns `BUNDLE_COMPOSITION_PASS` only when all required classes in
`TASK_REPORT_BUNDLE_MATRIX.md` are satisfied by report files or accepted
adjacent receipt manifest entries.

The packager may create `task_report_bundle.zip` only after a pass. It writes:

- `administratum_bundle_composition_receipt.json`
- `bundle_file_inventory.json`
- `sha256sums.txt`

## Block behavior

When required classes are missing, the checker returns
`BUNDLE_COMPOSITION_BLOCK` and writes `missing_items_request.json` unless a
different output path is supplied. The packager must not create or update the
bundle after a block.

## Boundary

V0.1 is structural. It does not replace Inquisition, Speculum, Custodes, Throne,
or semantic audit. A pass means "the required report bundle classes are present"
and nothing stronger.
