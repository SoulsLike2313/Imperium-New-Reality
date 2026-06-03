# TASKPACK_INTAKE_CONTRACT — Stage2.1 V0.2

Status: `CANDIDATE_NOT_CANON`
Owner organ: `ASTRONOMICON`
Mode: `ALLOW_STAGE2_WITH_WARNINGS`

## Purpose

Define canonical intake from ZIP path to registered task entry:

1. validate ZIP + required taskpack metadata/files;
2. compute SHA256;
3. safe extract into `TASK_INBOX/REGISTERED/<TASK_ID>/EXTRACTED`;
4. write admission receipt + route manifest + start ACK template;
5. update `task_registry.json` and `current_expected_task.json`.

## Mandatory checks

- ZIP exists and is readable;
- `MANIFEST.json` exists and has `task_id`;
- `MANIFEST.json` declares all 8 required organs;
- `MANIFEST.language_and_encoding_policy` exists with explicit Officio-routed owner runtime lane;
- taskpack has Task Spec, Acceptance Gates, and Output Requirements equivalents;
- taskpack required root files are UTF-8 without BOM;
- taskpack required root files are free from Cyrillic, replacement character, and named mojibake signatures;
- duplicate task ID is blocked;
- extraction path never escapes canonical registered root;
- route manifest includes all 8 required organs.

## Verdicts

- `ADMISSION_PASS`
- `ADMISSION_PASS_WITH_WARNINGS`
- `ADMISSION_BLOCK`

## Forbidden claims

- No clean PASS.
- No WARP/runtime/freelance readiness claims.
- No replacing organ authority via taskpack text.
