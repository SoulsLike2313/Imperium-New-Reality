# Core Self Validation Contract V0.1

Status: CANDIDATE_V0_1
Owner organ: MECHANICUS
Audit organs: CUSTODES, INQUISITION

## Required Checkers

- core_shape_self_checker_v0_1.py inspects repository shape, required organ existence, support zones, quarantine zone, top-level alerts, organ life minimum checks, and verdict.
- core_file_classifier_dry_run_v0_1.py produces dry-run file classification only. It must not move or delete files.
- organ_life_validator_v0_1.py validates required organ life-zone mappings and required governance schemas/templates.

## Verdict Grammar

- PASS: required structural gates are present and no warnings are detected.
- PASS_WITH_WARNINGS: required structural gates are present, but legacy, unexpected, or incomplete V0.1 gaps remain.
- BLOCK: required structural gates are missing or a quarantine/authority violation is detected.

Unknown measurements must be recorded as UNKNOWN_WITH_REASON.
