# Mechanicus Body Execution Requirements

## Mechanicus must own this class of work

This task must create a repeatable validation corridor:

1. read Arsenal cards;
2. select validation targets;
3. run safe checks;
4. build receipts;
5. update status recommendations;
6. detect fake CANON;
7. export Servitor scope;
8. ask Owner questions;
9. report dirt/risk to Inquisition;
10. register evidence for Administratum.

## Required scripts/checkers

The scripts may be minimal but must be real and runnable.

Required behavior:

- `mechanicus_capability_validator_v0_1.py`
  - reads selected cards/scope;
  - runs safe checks or marks missing;
  - writes validation results.

- `mechanicus_validation_receipt_builder_v0_1.py`
  - builds standard validation receipt JSON.

- `mechanicus_capability_scope_exporter_v0_1.py`
  - exports allowed/sandbox/candidate/forbidden capabilities for a task type.

- `mechanicus_fake_canon_detector_v0_2.py`
  - detects CANON cards without receipt/evidence.

## Registration

Any new script must be registered or at least reported for registration in:

- Mechanicus report;
- Arsenal capability card if practical;
- validation receipt if runnable.

## Inquisition hook

Write `inquisition_cleanliness_report.json`.

It must record:

- tool installs attempted: yes/no;
- network used: yes/no;
- runtime junk generated: yes/no;
- fake CANON count;
- quarantine recommendations.

## Administratum hook

Write `administratum_evidence_map.json`.

It must record:

- report paths;
- receipt paths;
- changed card paths;
- scripts created;
- next task recommendation.
