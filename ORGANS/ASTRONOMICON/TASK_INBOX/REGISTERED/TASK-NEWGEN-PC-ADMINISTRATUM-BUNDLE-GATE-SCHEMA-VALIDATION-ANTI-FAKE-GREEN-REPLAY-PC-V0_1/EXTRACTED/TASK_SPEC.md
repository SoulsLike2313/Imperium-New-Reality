# Task Spec

## Task ID

`TASK-NEWGEN-PC-ADMINISTRATUM-BUNDLE-GATE-SCHEMA-VALIDATION-ANTI-FAKE-GREEN-REPLAY-PC-V0_1`

## Step name

Administratum Bundle Gate V0.2: schema validation, anti-fake-green replay, and report bundle proof hardening.

## Background

Astronomicon already owns taskpack admission. Administratum must now own report bundle admission.

Administratum V0.1 created a composition gate: complete fixture passed, incomplete fixture blocked. V0.2 must harden this from "file exists" to "file exists and satisfies a minimal schema/field contract" while still avoiding deep semantic truth claims. Custodes later owns strict semantic admission; Administratum V0.2 owns bundle structure, class coverage, schema coverage, and basic anti-fake-green fixtures.

## Mission

Inside `E:/IMPERIUM_NEW_GENERATION_NEW_REALITY`, extend the Administratum report bundle gate so that a task report bundle is not accepted merely because files with the right names exist.

The new gate must:

1. Preserve V0.1 composition checking.
2. Add schema validation for required receipt classes.
3. Add anti-fake-green negative fixtures.
4. Replay the gate against at least the latest 3 real report folders if available.
5. Produce migration/replay receipts for old reports.
6. Produce a compact missing-items and invalid-fields digest.
7. Pack a `task_report_bundle.zip` only after Administratum gate PASS.
8. Commit and push to the New Reality remote.
9. Prove `origin/master == HEAD`, clean worktree, and no Ancient mutation.

## Required implementation targets

Preferred paths:

```text
ORGANS/ADMINISTRATUM/BUNDLE_GATE/
  ADMINISTRATUM_BUNDLE_GATE_V0_2_CONTRACT.md
  TASK_REPORT_BUNDLE_SCHEMA_MATRIX.md
  administratum_bundle_gate_v0_2.py
  administratum_bundle_packager_v0_2.py
  SCHEMAS/
  FIXTURES/
  README.md
```

If V0.1 paths already exist, extend them without breaking existing use.

## Administratum authority boundary

Administratum V0.2 may claim:

```text
BUNDLE_COMPOSITION_PASS
BUNDLE_SCHEMA_PASS
BUNDLE_PACKAGING_PASS
BUNDLE_COMPOSITION_BLOCK
BUNDLE_SCHEMA_BLOCK
```

Administratum V0.2 must not claim:

```text
SEMANTIC_TRUTH_PASS
CUSTODES_ADMISSION_PASS
INQUISITION_CLEAN_PASS
NO_FAKE_GREEN_FULL_PASS
```

Those belong to later Inquisition/Custodes layers.

## Negative fixtures required

Create fixtures that prove the gate blocks or warns on:

1. Missing required receipt file.
2. Required JSON exists but is malformed.
3. Required JSON exists but missing `task_id`.
4. Wrong `task_id` for the folder under review.
5. Wrong active root or Ancient root as active root.
6. Missing adjacent receipts manifest where adjacent proofs are referenced.
7. Stale or mismatched bundle SHA field.
8. Missing commit chain / closure receipt class.
9. Forged no-Ancient receipt with missing core fields.
10. Owner-facing Russian file inside machine bundle without Officio exception.

## Replay requirement

Run V0.2 gate against the latest real report folders under `REPORTS/`, prioritizing:

- the Administratum V0.1 bundle gate report;
- the New Reality self-fix/sterilization report;
- the final remote closure/native replay report;
- the remote tree bundle closure validator report.

If fewer than 3 real report folders are available, run all available and record the reason.

## No uncontrolled cleanup

Do not move or delete files in this task except creating this task's own artifacts and fixtures. Do not perform repo-wide quarantine. Do not mutate Ancient Empire.
