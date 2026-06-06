# Taskpack Acceptance Rules V0.1

## Purpose

Define when Officio may admit execution of a taskpack-driven task.

## Required Inputs

1. `task_id`
2. `starting_head`
3. `allowed_write_paths`
4. `forbidden_paths`
5. `required_gates`
6. `stop_conditions`
7. `expected_receipts`

## Mandatory Gates

- `GATE-U00-GIT-TRUTH`
- `GATE-U01-ROLE-ACK`
- `GATE-U02-SCOPE-BOUNDARY`
- `GATE-U04-EVIDENCE-RECEIPT`
- `GATE-U05-STOP-CONDITIONS`
- `GATE-U08-REPO-PURITY`
- `GATE-U09-NO-FAKE-GREEN`
- `GATE-U12-REPORT-OUTPUT-BUDGET`
- `GATE-U13-PYTHON-TYPE-SAFETY`
- `GATE-U14-WHOLE-REPO-SCOPE-RECON`
- `GATE-U15-OPERATIONALITY-IMPACT`
- `GATE-U16-BILINGUAL-UI`
- `GATE-U17-DELIVERABLE-PACKAGE`
- `GATE-U18-AGENT-FACTORY-COMPLIANCE`
- `GATE-U19-SCRIPT-ARTIFACT-PRESERVATION`
- `GATE-U20-AGENT-KPD-SELF-REVIEW`
- `GATE-U21-COMMAND-CHUNKING`
- `GATE-AI00-NO-DIRECT-MODEL-COMMAND`

## Admission Verdicts

- `PASS`: all required inputs and gate acknowledgements are present and verifiable.
- `CLARIFY`: non-critical missing data that can be resolved without scope drift.
- `STOP`: truth/scope/safety blocker detected.

## Historical Report Integrity

Checkers and scripts must write only to:
- current task report folder; or
- explicitly declared output path under current task scope.
