# PATCH PACK — IMPERIUM-POPULATION-CENSUS-0001

status: `WARP_CANDIDATE`  
mode: `MEASURE_ONLY`  
visual_policy: `NO_VISUAL_REFIT`  
primary_owner: `THRONE`  
registry_owner: `ADMINISTRATUM`  
tool_forge: `MECHANICUS`

## Purpose

Create the first machine-readable census of the Imperium population.

This patch does not clean, delete, move, rewrite, quarantine, or block anything. It scans the repository, classifies residents, assigns `imperium_id`, detects owners/status/classes, builds gap maps, computes first coverage metrics, validates the census, and emits a receipt.

## Why this exists

The Throne cannot govern what it cannot see. Before Throne foundation, organ passporting, KPD scoring, TUI/dashboard work, or enforcement, the Imperium must know what exists, where it lives, who likely owns it, and what is unknown.

## Organ responsibility map

| Responsibility | Organ |
|---|---|
| Sovereign meaning | `THRONE` |
| Registry / census | `ADMINISTRATUM` |
| Tool forge | `MECHANICUS` |
| Canon terms | `DOCTRINARIUM` |
| Adversarial suspicion | `INQUISITION` |
| Trust audit | `CUSTODES` |
| Strategy consumer | `STRATEGIUM` |
| Learning consumer | `SCHOLA_IMPERIALIS` |
| Role consumer | `OFFICIO_AGENTIS` |

## Files

```text
WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/
  PATCH_PACK.md
  CENSUS_POLICY_V0_1.md
  IMPERIUM_ID_POLICY_V0_1.md
  RUN_POPULATION_CENSUS.ps1
  MATRICES/
  SCHEMAS/
  TOOLS/build_population_census.py
  VALIDATORS/validate_population_census.py
  OUTPUTS/.gitkeep
  RECEIPTS/.gitkeep
  REPORTS/.gitkeep
  TESTS/README.md
```

## Execution

```powershell
pwsh WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/RUN_POPULATION_CENSUS.ps1
```

## PASS meaning

PASS means the census output is structurally valid and tied to real filesystem evidence. It does not mean the Imperium is healthy.

## FAIL meaning

FAIL means the census cannot be trusted as a baseline: missing outputs, malformed JSON, duplicate IDs, count mismatch, missing resident fields, bad hashes, or fake-green suspicion.
