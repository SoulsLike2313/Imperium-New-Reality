# Officio Agentis — Organ Passport V0.1

organ_id: `OFFICIO_AGENTIS`  
organ_type: `GREAT_NINE_ORGAN`  
primary_role: `roles, servitors and authority language`  
profile_state: `BASELINE_DECLARED`  
full_implementation_claim: `false`

## Purpose

Officio Agentis is one of the Great Nine organs of Imperium.

This README is a human-readable passport. The machine-readable authority is `ORGAN_CARD.json`.

## Declared functions

- define roles and servitor classes
- describe allowed authority boundaries
- maintain servitor prompt/task language
- control who may execute what kind of task
- stop execution when owner intent is missing

## Forbidden actions

- does not let servitors execute patch packs by default
- does not grant unlimited authority
- does not allow servitors to mutate core without explicit approval
- does not invent owner intent

## Validator

`ORGANS/OFFICIO_AGENTIS/VALIDATORS/validate_officio_agentis_profile.py`

The validator proves only baseline profile/passport completeness.

## Receipt

`ORGANS/OFFICIO_AGENTIS/RECEIPTS/officio_agentis_profile_receipt.json`

## Important

This organ is not declared fully implemented by this patch.

This patch gives the organ a profile, declared boundaries, and a profile validator.
