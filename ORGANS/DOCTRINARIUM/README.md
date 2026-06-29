# Doctrinarium — Organ Passport V0.1

organ_id: `DOCTRINARIUM`  
organ_type: `GREAT_NINE_ORGAN`  
primary_role: `canon, doctrine, schema and rule law`  
profile_state: `BASELINE_DECLARED`  
full_implementation_claim: `false`

## Purpose

Doctrinarium is one of the Great Nine organs of Imperium.

This README is a human-readable passport. The machine-readable authority is `ORGAN_CARD.json`.

## Declared functions

- define doctrine and canonical forms
- maintain schemas and rule texts
- detect doctrine contradictions
- describe what organs must and must not do
- provide machine-readable canon targets

## Forbidden actions

- does not execute tasks
- does not grant final trust
- does not override Owner decisions
- does not treat prose as proof without validator path

## Validator

`ORGANS/DOCTRINARIUM/VALIDATORS/validate_doctrinarium_profile.py`

The validator proves only baseline profile/passport completeness.

## Receipt

`ORGANS/DOCTRINARIUM/RECEIPTS/doctrinarium_profile_receipt.json`

## Important

This organ is not declared fully implemented by this patch.

This patch gives the organ a profile, declared boundaries, and a profile validator.
