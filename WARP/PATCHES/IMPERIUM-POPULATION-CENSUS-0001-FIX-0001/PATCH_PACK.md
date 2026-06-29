# PATCH PACK — IMPERIUM-POPULATION-CENSUS-0001-FIX-0001

status: `WARP_FIX_CANDIDATE`  
parent_task: `IMPERIUM-POPULATION-CENSUS-0001`  
mode: `MEASURE_ONLY`  
visual_policy: `NO_VISUAL_REFIT`

## Purpose

Harden the first population census before land.

Parent census passed structurally, but review found lens defects:

1. root-level files were incorrectly treated as root zones;
2. runtime `__pycache__` appeared after Python execution;
3. `_HARNESS` fixtures/runs were weakly owned/classified;
4. special organ-like directories were mixed with Great Nine organs;
5. known governance/doctrine/platform files were left as `UNKNOWN` too often.

## Changes

This patch replaces the parent census builder and validator:

```text
WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/TOOLS/build_population_census.py
WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/VALIDATORS/validate_population_census.py
WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/MATRICES/POPULATION_CLASSIFICATION_MATRIX_V0_1.json
WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/MATRICES/ROOT_ZONE_POLICY_V0_1.json
```

It also adds this child fix pack:

```text
WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001-FIX-0001/
  PATCH_PACK.md
  RUN_FIX_AND_CENSUS.ps1
  TESTS/README.md
```

## Fixed rules

- If path has no `/`, `root_zone = ROOT`.
- Root-level files get classes: `ROOT_CONFIG`, `ROOT_SCRIPT`, `ROOT_DOC`, `ROOT_MANIFEST`, `LOCKFILE`.
- `_HARNESS/_FIXTURES/INQ*` and `_HARNESS/_NEGATIVE_EXPERIENCE` belong to `INQUISITION`.
- `_HARNESS/_RUNS` and `_HARNESS/RUNNER` belong to `MECHANICUS`.
- `DOCTRINARIUM/*` belongs to `DOCTRINARIUM`.
- `ORGANS/_CORE_GOVERNANCE/*` belongs to `OWNER` or `THRONE` depending on path.
- `ORGANS/IMPERIAL_IDE/*` and `ORGANS/SPECULUM/*` belong to `MECHANICUS` as platform/tool territory.
- Great Nine passport gaps are calculated only for Great Nine organs, not special rings or platform tool organs.

## Validator hardening

The validator now fails if:

- root-level files become root zones again;
- `__pycache__` appears in census residents;
- `fix_0001_applied` marker is missing;
- duplicate `imperium_id` appears;
- SHA256 mismatch appears;
- output count mismatch appears.

## Run

```powershell
pwsh WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001-FIX-0001/RUN_FIX_AND_CENSUS.ps1
```

## PASS meaning

PASS means the fixed census lens is structurally valid. It does not mean the Imperium is healthy.
