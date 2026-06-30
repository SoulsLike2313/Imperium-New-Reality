# PATCH PACK — GOVERNANCE-ROOT-AND-GREAT-NINE-RECONCILIATION-0001

status: `WARP_CANDIDATE`  
mode: `ROOT_CANON_AND_GOVERNANCE_RECONCILIATION`  
primary_organ: `THRONE`  
supporting_organs: `ADMINISTRATUM`, `MECHANICUS`, `DOCTRINARIUM`

## Purpose

Establish the first real `Reality Canon / Root Law`.

This is patch 5/6 of the hygiene/control series.

## Corrected architecture

```text
E:\IMPERIUM_REALITY = Core Reality
E:\IMPERIUM_WARP    = external WARP pillar
E:\IMPERIUM_HARNESS = external HARNESS pillar
```

`WARP/` and `_HARNESS/` inside the repo are not final v1 root canon.

They are transitional debt until dedicated externalization patches:

```text
WARP-EXTERNALIZATION-AND-PROVENANCE-MIGRATION-0001
HARNESS-EXTERNALIZATION-AND-EVIDENCE-CANON-0001
```

## Allowed Reality root

```text
ORGANS/
SUPPORT/
AGENTS.md
README.md
.gitignore
.gitattributes
.editorconfig
```

## Transitional root debt

```text
WARP/
_HARNESS/
```

## Root drift to relocate now

```text
DOCTRINARIUM/ -> ORGANS/DOCTRINARIUM/LEGACY_ROOT_IMPORT/DOCTRINARIUM/
SCHEMAS/AUTHORED/T4/ -> ORGANS/DOCTRINARIUM/SCHEMAS/AUTHORED/T4/
other SCHEMAS/* -> ORGANS/DOCTRINARIUM/LEGACY_ROOT_IMPORT/SCHEMAS/
REPORTS/ -> SUPPORT/QUARANTINE/ROOT_REPORTS_PENDING_HARNESS_INTAKE/REPORTS/
```

## Added law

```text
ORGANS/THRONE/MATRICES/REALITY_ROOT_CANON_MATRIX_V0_1.json
ORGANS/THRONE/MATRICES/IMPERIUM_PILLAR_BOUNDARY_MATRIX_V0_1.json
ORGANS/THRONE/MATRICES/GREAT_NINE_CANON_AND_ALIAS_MATRIX_V0_1.json
ORGANS/THRONE/SELF_KNOWLEDGE/REALITY_BOUNDARY_AND_STORAGE_POLICY_V0_1.md
```

## Validator

```text
ORGANS/MECHANICUS/VALIDATORS/validate_reality_root_governance.py
```

Expected verdict:

```text
PASS_REALITY_ROOT_CANON_WITH_TRANSITIONAL_DEBT
```

This is intentionally honest: root drift is removed, but WARP/HARNESS externalization debt remains visible.
