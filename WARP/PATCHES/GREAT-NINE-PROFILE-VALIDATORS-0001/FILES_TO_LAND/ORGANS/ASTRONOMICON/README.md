# Astronomicon — Organ Passport V0.1

organ_id: `ASTRONOMICON`  
organ_type: `GREAT_NINE_ORGAN`  
primary_role: `request intake gate`  
profile_state: `BASELINE_DECLARED`  
full_implementation_claim: `false`

## Purpose

Astronomicon is one of the Great Nine organs of Imperium.

This README is a human-readable passport. The machine-readable authority is `ORGAN_CARD.json`.

## Declared functions

- validate incoming task packs
- check owner intent clarity
- verify pass/fail criteria presence
- admit or reject work before execution
- return tasks to fix when intake is incomplete

## Forbidden actions

- does not issue final Throne verdict
- does not mutate Core directly
- does not bypass Administratum registration
- does not claim implementation success without receipts

## Validator

`ORGANS/ASTRONOMICON/VALIDATORS/validate_astronomicon_profile.py`

The validator proves only baseline profile/passport completeness.

## Receipt

`ORGANS/ASTRONOMICON/RECEIPTS/astronomicon_profile_receipt.json`

## Important

This organ is not declared fully implemented by this patch.

This patch gives the organ a profile, declared boundaries, and a profile validator.
