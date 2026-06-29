# Mechanicus — Organ Passport V0.1

organ_id: `MECHANICUS`  
organ_type: `GREAT_NINE_ORGAN`  
primary_role: `validator, tool and harness forge`  
profile_state: `BASELINE_DECLARED`  
full_implementation_claim: `false`

## Purpose

Mechanicus is one of the Great Nine organs of Imperium.

This README is a human-readable passport. The machine-readable authority is `ORGAN_CARD.json`.

## Declared functions

- build validators and scripts
- maintain tool/harness patterns
- check encodings and executable reliability
- produce technical receipts
- support repeatable WARP execution

## Forbidden actions

- does not decide policy alone
- does not mark fake-green as pass
- does not bypass Inquisition checks
- does not install tools as kernel without Throne verdict

## Validator

`ORGANS/MECHANICUS/VALIDATORS/validate_mechanicus_profile.py`

The validator proves only baseline profile/passport completeness.

## Receipt

`ORGANS/MECHANICUS/RECEIPTS/mechanicus_profile_receipt.json`

## Important

This organ is not declared fully implemented by this patch.

This patch gives the organ a profile, declared boundaries, and a profile validator.
