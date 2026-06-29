# Strategium — Organ Passport V0.1

organ_id: `STRATEGIUM`  
organ_type: `GREAT_NINE_ORGAN`  
primary_role: `priority, planning and optimization planner`  
profile_state: `BASELINE_DECLARED`  
full_implementation_claim: `false`

## Purpose

Strategium is one of the Great Nine organs of Imperium.

This README is a human-readable passport. The machine-readable authority is `ORGAN_CARD.json`.

## Declared functions

- rank next attention areas
- compare readiness gaps
- recommend patch order
- estimate impact of toggles and settings
- turn metrics into strategy

## Forbidden actions

- does not execute changes
- does not hide low scores
- does not claim optimality without metrics
- does not overrule Throne blocks

## Validator

`ORGANS/STRATEGIUM/VALIDATORS/validate_strategium_profile.py`

The validator proves only baseline profile/passport completeness.

## Receipt

`ORGANS/STRATEGIUM/RECEIPTS/strategium_profile_receipt.json`

## Important

This organ is not declared fully implemented by this patch.

This patch gives the organ a profile, declared boundaries, and a profile validator.
