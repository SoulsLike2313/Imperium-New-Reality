# Custodes — Organ Passport V0.1

organ_id: `CUSTODES`  
organ_type: `GREAT_NINE_ORGAN`  
primary_role: `organ trust auditor and internal police`  
profile_state: `BASELINE_DECLARED`  
full_implementation_claim: `false`

## Purpose

Custodes is one of the Great Nine organs of Imperium.

This README is a human-readable passport. The machine-readable authority is `ORGAN_CARD.json`.

## Declared functions

- audit organ validators
- verify whether organ verdicts are trustworthy
- maintain organ trust matrices
- package trust evidence for Administratum
- answer Throne whether organs may be believed

## Forbidden actions

- does not perform every organ function itself
- does not override Owner alone
- does not approve unverified validators
- does not replace Inquisition adversarial scan

## Validator

`ORGANS/CUSTODES/VALIDATORS/validate_custodes_profile.py`

The validator proves only baseline profile/passport completeness.

## Receipt

`ORGANS/CUSTODES/RECEIPTS/custodes_profile_receipt.json`

## Important

This organ is not declared fully implemented by this patch.

This patch gives the organ a profile, declared boundaries, and a profile validator.
