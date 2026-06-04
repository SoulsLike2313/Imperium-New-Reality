# Administratum Bundle Gate V0.1

Status: `CANDIDATE_V0_1`
Owner organ: `ADMINISTRATUM`

This folder defines the first New Reality task report bundle composition gate.
It is the exit-side counterpart to Astronomicon taskpack admission: before a
task report bundle can be treated as closed, Administratum checks that required
report evidence classes are present and packages only a passing report folder.

V0.1 checks structure and composition only. It does not claim deep semantic
truth, red-team sufficiency, or canon admission.

## Files

- `TASK_REPORT_BUNDLE_MATRIX.md` lists required and optional report file classes.
- `ADMINISTRATUM_BUNDLE_GATE_CONTRACT.md` defines pass/block behavior.
- `administratum_bundle_gate_v0_1.py` checks a report directory and writes receipts.
- `administratum_bundle_packager_v0_1.py` packages a report only after a pass.
- `SCHEMAS/` contains JSON schemas for matrix and receipt shapes.
- `FIXTURES/` contains complete and missing report fixtures.

## Typical commands

```powershell
python ORGANS/ADMINISTRATUM/BUNDLE_GATE/administratum_bundle_gate_v0_1.py --report-dir ORGANS/ADMINISTRATUM/BUNDLE_GATE/FIXTURES/complete_report_fixture --task-id FIXTURE-COMPLETE
python ORGANS/ADMINISTRATUM/BUNDLE_GATE/administratum_bundle_packager_v0_1.py --report-dir ORGANS/ADMINISTRATUM/BUNDLE_GATE/FIXTURES/complete_report_fixture --task-id FIXTURE-COMPLETE
```

The packager refuses to create `task_report_bundle.zip` when the gate returns
`BUNDLE_COMPOSITION_BLOCK`.
