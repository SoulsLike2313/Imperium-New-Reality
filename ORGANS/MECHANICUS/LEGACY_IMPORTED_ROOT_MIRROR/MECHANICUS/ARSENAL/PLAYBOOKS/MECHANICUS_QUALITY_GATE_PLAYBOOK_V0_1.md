# MECHANICUS QUALITY GATE PLAYBOOK V0.1

## Purpose

Repeatable pre/post-task quality gate for NewGen Servitor execution in Mechanicus body with mandatory Officio role/language admission.

## When to run

1. Before editing in a new NewGen task (admission preflight + scope consumption).
2. After creating/updating Mechanicus tools/reports for evidence closure.
3. Before commit/push when task claims PASS or PASS_WITH_WARNINGS.

## Officio gate inclusion

1. Ensure `GATE_ACK.md` exists in report root with:
   - `ROLE_ACK`
   - `LANGUAGE_ACK`
   - `SCOPE_ACK`
   - `STOP_CONDITIONS_ACK`
   - `FORBIDDEN_ACTIONS_ACK`
2. Ensure owner-facing progress/final summaries are Russian.
3. Produce `officio_gate_use_report.json` and reference Officio role pack.

## Scope packs consumed

Runner consumes these packs from `IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/SCOPE_PACKS/V0_1`:

- `scope_code_quality_task_v0_1.json`
- `scope_json_schema_validation_task_v0_1.json`
- `scope_mechanicus_tool_validation_task_v0_1.json`
- `scope_repo_hygiene_task_v0_1.json`
- `scope_taskpack_generation_task_v0_1.json`
- `scope_controlled_tool_provision_task_v0_1.json`

## Checks run by gate

1. Officio gate use and ACK completeness.
2. Scope pack consumption report.
3. Code quality:
   - `python -m py_compile`
   - `python -m ruff check`
   - `python -m mypy` (WARN allowed for first-pass typing debt)
4. JSON/schema gate:
   - JSON parse for targeted artifacts.
   - `jsonschema` validation where schema exists.
   - `NO_SCHEMA_AVAILABLE` when schema is absent.
5. Taskpack validation:
   - required dossier files/templates present and parseable.
6. NewGen hygiene:
   - report-only scan for `__pycache__`, `*.pyc`, `*.log`, `*.tmp`, `server_pid.txt`, taskpack leftovers.
7. Fake-CANON detection.
8. SQLite/FTS evidence smoke index over report artifacts.

## PASS/WARN/FAIL interpretation

- `PASS`: no failing gates and no warnings.
- `PASS_WITH_WARNINGS`: no failing gates, but warnings exist (for example mypy WARN, no schema, hygiene hits in report-only mode).
- `FAIL`: one or more gates are `FAIL`/`BLOCKED` or fake-canon evidence is non-zero.

## Core runner command

```powershell
python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_quality_gate_runner_v0_1.py `
  --task-id TASK-NEWGEN-MECHANICUS-VALIDATION-BATCH-002-PC-V0_1 `
  --report-root IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-VALIDATION-BATCH-002-PC-V0_1 `
  --taskpack-zip C:\Users\PC\Downloads\TASK-NEWGEN-MECHANICUS-VALIDATION-BATCH-002-PC-V0_1_DOSSIER.zip `
  --taskpack-dir C:\Users\PC\AppData\Local\Temp\imperium_task_batch_002
```

## Key outputs

- `quality_gate_run_report.json`
- `code_quality_report.json`
- `schema_validation_report.json`
- `taskpack_validation_report.json`
- `newgen_hygiene_report.json`
- `fake_canon_detector_report.json`
- `evidence_index_smoke_report.json`
- `administratum_evidence_map.json`
- `inquisition_hygiene_handoff.json`
- `closure_receipt.json`
- `FINAL_REPORT.md`
