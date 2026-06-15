# Custodes Organ Matrix Audit Contract V0.1

Status: `NARROW_CANDIDATE_V0_1`
Owner organ: `CUSTODES`

## Purpose

Custodes V0.1 audits the post-work organ receipt matrix. This is not full Custodes admission and not Throne scope.

## Scope

Custodes checks only:

- all nine required post-work organs are represented;
- each organ row has `organ_id`, `task_id`, `status`, `owned_checks`, `evidence_paths`, and `learned_rules`;
- any `NOT_YET_IMPLEMENTED` row has a reason and next task route;
- no row claims full semantic truth without evidence.

## Block Conditions

- missing organ row;
- malformed organ row;
- missing Inquisition contradiction scan;
- missing Administratum bundle receipt;
- missing or malformed Custodes audit receipt.
