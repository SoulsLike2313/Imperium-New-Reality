# Task Spec

## Task ID

`TASK-NEWGEN-PC-ADMINISTRATUM-TASK-REPORT-BUNDLE-GATE-MATRIX-AND-PACKAGER-PC-V0_1`

## Step name

Administratum task report bundle gate matrix and packager.

## Purpose

Astronomicon already blocks incomplete taskpacks before task start. New Reality now needs a symmetric exit gate: Administratum must block or accept task report bundles before closure.

This task creates the first Administratum bundle composition matrix and reusable packager. Version 0.1 checks structure and composition only. It does not claim deep semantic truth and does not replace Inquisition, Speculum, Custodes, or Throne.

## Required implementation

Create the Administratum bundle gate under:

```text
ORGANS/ADMINISTRATUM/BUNDLE_GATE/
```

Required files:

```text
ORGANS/ADMINISTRATUM/BUNDLE_GATE/README.md
ORGANS/ADMINISTRATUM/BUNDLE_GATE/TASK_REPORT_BUNDLE_MATRIX.md
ORGANS/ADMINISTRATUM/BUNDLE_GATE/ADMINISTRATUM_BUNDLE_GATE_CONTRACT.md
ORGANS/ADMINISTRATUM/BUNDLE_GATE/administratum_bundle_gate_v0_1.py
ORGANS/ADMINISTRATUM/BUNDLE_GATE/administratum_bundle_packager_v0_1.py
ORGANS/ADMINISTRATUM/BUNDLE_GATE/SCHEMAS/task_report_bundle_matrix.schema.json
ORGANS/ADMINISTRATUM/BUNDLE_GATE/SCHEMAS/missing_items_request.schema.json
ORGANS/ADMINISTRATUM/BUNDLE_GATE/SCHEMAS/bundle_composition_receipt.schema.json
ORGANS/ADMINISTRATUM/BUNDLE_GATE/FIXTURES/complete_report_fixture/
ORGANS/ADMINISTRATUM/BUNDLE_GATE/FIXTURES/missing_report_fixture/
```

The gate must:

1. Read a task report directory.
2. Check the required composition matrix.
3. Return `BUNDLE_COMPOSITION_PASS` only when the required file classes are present.
4. Return `BUNDLE_COMPOSITION_BLOCK` plus `missing_items_request.json` when required files are missing.
5. Create `task_report_bundle.zip` only after pass.
6. Write `administratum_bundle_composition_receipt.json`.
7. Write `bundle_file_inventory.json`.
8. Write or update `sha256sums.txt` covering the final bundle and included files where practical.
9. Support adjacent receipt manifest logic for self-reference-limited proof files.

## Required composition matrix v0.1

At minimum, the matrix must include these file classes:

- task identity and task report metadata;
- commit chain / commit identifiers;
- git closure and remote closure proof;
- worktree clean or explicit cap receipt;
- scope lock / no Ancient mutation receipt;
- claim ledger;
- capability split receipt;
- red team verdict;
- final owner summary boundary or Officio localization reference;
- bundle manifest / file inventory;
- sha256 sums;
- adjacent receipts manifest when proof files live next to the bundle;
- Administratum composition receipt.

The matrix may support optional classes:

- screenshots/assets;
- web research dossier;
- Inquisition review;
- Speculum review;
- Mechanicus tool/candidate receipts;
- performance/cost/KPD receipts.

## Required proof runs

Run the gate on at least two fixtures:

1. Complete fixture: must pass and produce a zip.
2. Missing fixture: must block and produce a missing-items request.

Also run the gate against one real recent report folder if available. Preferred source:

```text
REPORTS/TASK-NEWGEN-PC-NEW-REALITY-SELF-FIX-CLEAN-DEV-ENV-SERVITOR-CONTROL-MECHANICUS-SKILL-ARSENAL-AND-REPO-STERILIZATION-PC-V0_1/
```

If that folder is not available, choose the most recent New Reality report folder and explain the substitution in the receipt.

## Closure

Commit and push to the New Reality remote:

```text
https://github.com/SoulsLike2313/Imperium-New-Reality.git
```

Verify:

```text
git status --porcelain
git rev-parse HEAD
git ls-remote origin refs/heads/master
```

Final answer must be in Russian, 4-part format, and include exact report bundle path and SHA256.
