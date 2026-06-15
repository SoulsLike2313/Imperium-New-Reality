# Imperium Core Shape Contract V0.1

Status: CANDIDATE_V0_1
Owner organ: ADMINISTRATUM
Guard organs: INQUISITION, CUSTODES

## Purpose

This contract gives the repository a machine-checkable core shape before any large physical cleanup is attempted.

## Core Classes

Every active core artifact must be treated as one of:

1. Owned by exactly one required organ.
2. Common support used by organs but not itself an organ.
3. Questionable or quarantine material that is banned from active use until admitted by an explicit salvage or admission receipt.

## Required Shape

The required V0.1 shape is:

- ORGANS/_CORE_GOVERNANCE/
- ORGANS/ADMINISTRATUM/
- ORGANS/ASTRONOMICON/
- ORGANS/CUSTODES/
- ORGANS/DOCTRINARIUM/
- ORGANS/INQUISITION/
- ORGANS/MECHANICUS/
- ORGANS/OFFICIO_AGENTIS/
- ORGANS/SCHOLA_IMPERIALIS/
- ORGANS/STRATEGIUM/
- SUPPORT/COMMON_IMPERIUM_SUPPORT/
- SUPPORT/QUESTIONABLE_OR_QUARANTINE/

Throne is explicitly out of this nine-organ core. Throne remains future laptop-only scope.

## Migration Boundary

This contract authorizes mapping, dry-run classification, alerts, receipts, and validators. It does not authorize mass moves, deletes, import path rewrite sweeps, or claims of full cleanup.

## Acceptance Boundary

V0.1 may claim machine-checkable structural authority. It may not claim complete semantic truth, full repository migration, full Custodes admission, Throne readiness, or WARP runtime readiness.
