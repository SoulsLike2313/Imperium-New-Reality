# LOGOS_OWNER_AUDIT_CARD_RESPONSE_CONTRACT_V0_1

Status: `CANDIDATE_V0_1`
Owner organ: `OFFICIO_AGENTIS`
Support organs: `ADMINISTRATUM`, `INQUISITION`

## Purpose

Register `Owner Audit Card` as a candidate Logos response format for compact verification mode.

## Trigger route

Apply when Owner asks:

- `check`
- `verify`
- equivalent short verification phrase

or provides review evidence without requesting another explicit response format.

## Required output structure

Must follow the section order defined by:

- `IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/CONTRACTS/OWNER_AUDIT_CARD_CONTRACT_V0_1.md`

and must keep Owner-facing lane in Russian under:

- `IMPERIUM_NEW_GENERATION/ORGANS/OFFICIO_AGENTIS/CONTRACTS/OWNER_FACING_RU_RESPONSE_CONTRACT.md`

## Constraints

- Keep owner-facing text compact.
- Do not include raw JSON dumps in final owner message.
- Final chat for non-BLOCK closure still obeys Officio 4-part final answer contract.

