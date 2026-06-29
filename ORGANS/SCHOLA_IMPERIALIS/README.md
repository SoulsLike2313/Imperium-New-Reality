# Schola Imperialis — Organ Passport V0.1

organ_id: `SCHOLA_IMPERIALIS`  
organ_type: `GREAT_NINE_ORGAN`  
primary_role: `learning, lessons and negative example memory`  
profile_state: `BASELINE_DECLARED`  
full_implementation_claim: `false`

## Purpose

Schola Imperialis is one of the Great Nine organs of Imperium.

This README is a human-readable passport. The machine-readable authority is `ORGAN_CARD.json`.

## Declared functions

- store lessons and negative examples
- turn failures into reusable guidance
- maintain learning records
- separate active doctrine from archived lessons
- support future improvement loops

## Forbidden actions

- does not promote negative examples to active doctrine
- does not execute tasks
- does not validate implementation alone
- does not forget provenance

## Validator

`ORGANS/SCHOLA_IMPERIALIS/VALIDATORS/validate_schola_imperialis_profile.py`

The validator proves only baseline profile/passport completeness.

## Receipt

`ORGANS/SCHOLA_IMPERIALIS/RECEIPTS/schola_imperialis_profile_receipt.json`

## Important

This organ is not declared fully implemented by this patch.

This patch gives the organ a profile, declared boundaries, and a profile validator.
