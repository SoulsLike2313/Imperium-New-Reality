# Administratum — Organ Passport V0.1

organ_id: `ADMINISTRATUM`  
organ_type: `GREAT_NINE_ORGAN`  
primary_role: `object, task, receipt and archive registry`  
profile_state: `BASELINE_DECLARED`  
full_implementation_claim: `false`

## Purpose

Administratum is one of the Great Nine organs of Imperium.

This README is a human-readable passport. The machine-readable authority is `ORGAN_CARD.json`.

## Declared functions

- register tasks, patches, objects and receipts
- maintain canonical ids and provenance
- assemble context packs
- store archives and historical evidence
- serve retrieval paths for audit

## Forbidden actions

- does not validate trust by itself
- does not replace Throne verdict
- does not invent owner intent
- does not accept unregistered core mutation

## Validator

`ORGANS/ADMINISTRATUM/VALIDATORS/validate_administratum_profile.py`

The validator proves only baseline profile/passport completeness.

## Receipt

`ORGANS/ADMINISTRATUM/RECEIPTS/administratum_profile_receipt.json`

## Important

This organ is not declared fully implemented by this patch.

This patch gives the organ a profile, declared boundaries, and a profile validator.
