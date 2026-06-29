# PATCH PACK — OWNER-DOCS-VALIDATION-WARP-0001

## Status

`WARP_CANDIDATE`

This pack validates the direct-Reality Owner foundation documents landed under:

`ORGANS/_CORE_GOVERNANCE/OWNER_DECISIONS/`

## Purpose

Create the first code-checkable validation layer for Owner foundation documents.

The validator proves that the Owner decision layer contains the mandatory decisions required before Imperium proceeds to Population Census, Throne Crown Organ foundation, organ passporting, KPD, TUI, and enforcement work.

## Responsibility map

| Role | Organ | Meaning |
|---|---|---|
| Sovereign owner | `THRONE` | Owns meaning and final verdict |
| Temporary host | `_CORE_GOVERNANCE/OWNER_DECISIONS` | Hosts current Owner docs until Throne exists |
| Tool forge | `MECHANICUS` | Owns validator implementation quality |
| Trust auditor | `CUSTODES` | Later audits validator/organs trust |
| Adversarial checker | `INQUISITION` | Later checks fake-green, hardcode, dirt |
| Receipt registry | `ADMINISTRATUM` | Later registers receipts/history |
| Canon reference | `DOCTRINARIUM` | Keeps wording/schema/canon consistent |

## Files added

```text
WARP/PATCHES/OWNER-DOCS-VALIDATION-WARP-0001/
  PATCH_PACK.md
  RUN_OWNER_DOCS_VALIDATION.ps1
  SCHEMAS/
    owner_answer_lock.schema.json
    owner_decision_index.schema.json
    implementation_zones.schema.json
    owner_docs_validation_receipt.schema.json
  VALIDATORS/
    validate_owner_foundation_docs.py
  RECEIPTS/
    .gitkeep
  REPORTS/
    .gitkeep
  TESTS/
    README.md
```

## Checks

The validator checks:

1. All mandatory Owner docs exist.
2. JSON/text files are UTF-8 and parse correctly.
3. `OWNER_ANSWER_LOCK_V0_1.json` includes:
   - Throne = `CROWN_ORGAN`
   - Throne mode = `MEASURE_ONLY`
   - override = `OWNER_ONLY`
   - final Great Nine list
   - visual refit frozen
4. `IMPLEMENTATION_ZONES_V0_1.json` includes zones `0..9`.
5. `VALIDATION_BACKLOG_V0_1.md` exists and is non-empty.
6. `README.md` references the core Owner documents.
7. root `OWNER_DOCS_FILE_MANIFEST_SHA256.json` exists.
8. receipt/report are generated from actual file checks, not hand-written.

## Non-goals

- Does not create `ORGANS/THRONE/` yet.
- Does not land validators into Reality yet.
- Does not hard-block repo.
- Does not touch Eyes/Graph Viewer visual refit.

## Run

From repo root:

```powershell
pwsh WARP/PATCHES/OWNER-DOCS-VALIDATION-WARP-0001/RUN_OWNER_DOCS_VALIDATION.ps1
```

Expected outputs:

```text
WARP/PATCHES/OWNER-DOCS-VALIDATION-WARP-0001/RECEIPTS/owner_docs_validation_receipt.json
WARP/PATCHES/OWNER-DOCS-VALIDATION-WARP-0001/REPORTS/OWNER_DOCS_VALIDATION_REPORT_V0_1.md
```

## Pass policy

This pack may be reviewed only if:

```text
validator_exit_code = 0
receipt.verdict = PASS
receipt.fake_green_guard = PASS
```

## Land policy

Land only after WARP run, generated receipt, Owner review, and no fake-green.
