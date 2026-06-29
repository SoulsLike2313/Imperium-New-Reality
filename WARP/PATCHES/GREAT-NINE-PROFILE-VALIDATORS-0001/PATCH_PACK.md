# PATCH PACK — GREAT-NINE-PROFILE-VALIDATORS-0001

status: `WARP_CANDIDATE`  
mode: `MEASURE_ONLY`  
primary_organ: `THRONE`  
affected_organs: `GREAT_NINE`

## Purpose

Raise the Great Nine from mostly directory-level population into passported, declared, profile-validated organs.

This patch gives each of the 9 organs:

- `README.md`;
- `ORGAN_CARD.json`;
- `MANIFEST.json`;
- `FUNCTIONS.md`;
- required slot directories;
- a profile matrix;
- a profile schema;
- a profile validator;
- generated profile validation receipt/report.

It also gives the Throne a strictness matrix and validator that measures whether the Great Nine have real profile validators and receipts.

## Why

The previous Throne target-gap score was still too optimistic because the Throne was strong while the Great Nine remained under-described.

Core v1 cannot be trusted if the Crown is formalized but the Nine are hollow.

## Important

This patch does not claim the organs are fully implemented.

It only proves:

```text
each organ has a declared passport
each organ has an executable profile validator
each profile validator can check declared vs required baseline
the Throne can audit that all 9 profile validators exist and pass
```

## Expected verdicts

Per organ:

```text
PASS_PROFILE_BASELINE
```

Throne audit:

```text
PASS_GREAT_NINE_PROFILE_BASELINE
```

## Land policy

Land only if:

- all 9 organ profile validators pass;
- Throne Great Nine profile audit passes;
- no Python cache files are committed;
- generated receipts/reports exist for all 9 organs and Throne audit.
