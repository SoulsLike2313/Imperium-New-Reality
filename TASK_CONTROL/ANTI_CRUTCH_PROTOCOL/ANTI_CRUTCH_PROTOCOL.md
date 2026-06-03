# Anti-Crutch Protocol V0.1

## Purpose
Prevent taskpack-only workarounds from replacing canonical organ authority.

## Core Law
If a recurring rule appears only in a taskpack/prompt and is not promoted to a canonical owner, the work is debt, not done.

## Canonical Ownership Model
- Officio Agentis: role, mode, execution, communication, response contract.
- Doctrinarium: law, doctrine, compliance principles.
- Mechanicus: tools, scripts, registries, checkers.
- Inquisition: audit, fake-green detection, scope-drift detection.
- Administratum: continuity, checkpoints, evidence ledger, bundle chain.
- Astronomicon: routing, decomposition, stage map.
- Strategium: priority, volume, risk, freeze policy.
- Schola Imperialis: lessons, training, regression examples.

## Classification Model
- `CANONICAL_RULE`: rule is implemented in canonical owner artifacts.
- `TASKPACK_ONLY_WORKAROUND`: rule is local to prompt/taskpack only.
- `TEMPORARY_WORKAROUND_ACCEPTED_WITH_DEBT`: workaround exists but debt/promotion owner is explicitly recorded.
- `ORGAN_AUTHORITY_MISSING`: rule exists but canonical owner cannot be assigned.
- `CANONICAL_AUTHORITY_BYPASSED`: canonical authority exists but text tries to bypass it.

## Enforcement Model
1. Detect candidate rule text and domain hints.
2. Detect canonical references vs local-only workaround markers.
3. Assign verdict codes and promotion debt targets.
4. Emit machine-readable report for evidence.

## Anti-Crutch Requirement
Taskpacks may instruct execution details, but recurring system law must be promoted to canonical owner artifacts.
