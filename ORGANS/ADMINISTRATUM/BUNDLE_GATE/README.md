# Administratum Bundle Gate

Status: `CANDIDATE_V0_2`
Owner organ: `ADMINISTRATUM`

This folder defines the New Reality task report bundle composition and schema
gate. It is the exit-side counterpart to Astronomicon taskpack admission:
before a task report bundle can be treated as closed, Administratum checks that
required report evidence classes are present and that required JSON evidence
has minimal field integrity.

V0.1 remains available as the original composition-only checker. V0.2 preserves
that composition surface and adds schema validation, negative fixture replay,
read-only real-report replay, and pass-gated packaging. Neither version claims
deep semantic truth, red-team sufficiency, Custodes admission, or canon
admission.

## Files

- `TASK_REPORT_BUNDLE_MATRIX.md` lists required and optional report file classes.
- `ADMINISTRATUM_BUNDLE_GATE_CONTRACT.md` defines pass/block behavior.
- `administratum_bundle_gate_v0_1.py` checks a report directory and writes receipts.
- `administratum_bundle_packager_v0_1.py` packages a report only after a pass.
- `TASK_REPORT_BUNDLE_SCHEMA_MATRIX.md` lists the V0.2 schema field contracts.
- `ADMINISTRATUM_BUNDLE_GATE_V0_2_CONTRACT.md` defines V0.2 pass/block behavior.
- `administratum_bundle_gate_v0_2.py` checks composition plus schema fields.
- `administratum_bundle_packager_v0_2.py` packages only after V0.2 gate pass.
- `SCHEMAS/` contains JSON schemas for matrix and receipt shapes.
- `FIXTURES/` contains complete, missing, and anti-fake-green report fixtures.

## Typical commands

```powershell
python ORGANS/ADMINISTRATUM/BUNDLE_GATE/administratum_bundle_gate_v0_1.py --report-dir ORGANS/ADMINISTRATUM/BUNDLE_GATE/FIXTURES/complete_report_fixture --task-id FIXTURE-COMPLETE
python ORGANS/ADMINISTRATUM/BUNDLE_GATE/administratum_bundle_packager_v0_1.py --report-dir ORGANS/ADMINISTRATUM/BUNDLE_GATE/FIXTURES/complete_report_fixture --task-id FIXTURE-COMPLETE
python ORGANS/ADMINISTRATUM/BUNDLE_GATE/administratum_bundle_gate_v0_2.py --write-fixture-suite ORGANS/ADMINISTRATUM/BUNDLE_GATE/FIXTURES
python ORGANS/ADMINISTRATUM/BUNDLE_GATE/administratum_bundle_gate_v0_2.py --run-fixtures ORGANS/ADMINISTRATUM/BUNDLE_GATE/FIXTURES
python ORGANS/ADMINISTRATUM/BUNDLE_GATE/administratum_bundle_packager_v0_2.py --report-dir ORGANS/ADMINISTRATUM/BUNDLE_GATE/FIXTURES/v0_2_complete_report_fixture --task-id FIXTURE-V0_2_COMPLETE_REPORT_FIXTURE
```

The packager refuses to create `task_report_bundle.zip` when the gate returns
`BUNDLE_COMPOSITION_BLOCK` or `BUNDLE_SCHEMA_BLOCK`.
