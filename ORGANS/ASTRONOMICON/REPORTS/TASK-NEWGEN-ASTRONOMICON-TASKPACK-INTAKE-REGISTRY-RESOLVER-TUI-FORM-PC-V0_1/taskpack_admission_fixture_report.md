# Taskpack Admission Fixture Report

Task: `TASK-NEWGEN-ASTRONOMICON-TASKPACK-INTAKE-REGISTRY-RESOLVER-TUI-FORM-PC-V0_1`
Timestamp: `2026-05-30T23:20:18Z`

## Cases
- `missing_zip` -> `ADMISSION_BLOCK`
- `bad_zip` -> `ADMISSION_BLOCK`
- `missing_manifest` -> `ADMISSION_BLOCK`
- `missing_task_id` -> `ADMISSION_BLOCK`
- `missing_task_spec` -> `ADMISSION_BLOCK`
- `unsafe_extraction_path` -> `ADMISSION_BLOCK`
- `positive_valid_registration` -> `ADMISSION_PASS`
- `duplicate_task_id` -> `ADMISSION_BLOCK`
- `missing_route_template` -> `ADMISSION_BLOCK`
