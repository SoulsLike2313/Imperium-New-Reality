# Imperium Throne Gateway Contract V0.1

Status: CANDIDATE_V0_1
Owner: THRONE (control and storage root of the core)
Steward organ: ADMINISTRATUM
Guard organs: INQUISITION, CUSTODES
Supersedes: throne_scope = FUTURE_LAPTOP_ONLY_SCOPE (REQUIRED_9_ORGANS_V0_1.json)

## Purpose

The Throne is the single mandatory gateway above the nine organs and the control and storage root of the core. This contract states, in strict and ultimate terms, that no request is executed inside the core unless the Throne has admitted it and issued a permit. This is the base law; deep per-organ contracts are reviewed separately and later.

## Position

- The Throne sits ABOVE the nine organs. It is NOT one of the nine.
- The nine organs are functional organs under the Throne.
- The Throne is the core control point and the core storage root. Core admission state and core-root pointers live under Throne authority.
- `included_in_9_organ_core` stays false: the Throne is above the nine, not a tenth organ.

## The Nine Under the Throne

1. ADMINISTRATUM — Evidence boundary, address book, continuity, archive, and closure truth.
2. ASTRONOMICON — Task intake, task identity, route manifests, and entry admission.
3. CUSTODES — Narrow organ/matrix and life-zone audit authority.
4. DOCTRINARIUM — Execution law, doctrine, canon boundaries, and forbidden claims.
5. INQUISITION — Contradiction scans, fake-green rejection, quarantine policy, and risk gates.
6. MECHANICUS — Tools, validators, replay discipline, and capability registration.
7. OFFICIO_AGENTIS — Role routing, owner-facing language authority, and response discipline.
8. SCHOLA_IMPERIALIS — Reusable lessons, preventive rules, and learning capture.
9. STRATEGIUM — Metrics, priority, cost class, KPD, and next-route weighting.

## Mandatory Gateway Law (ultimatum)

1. Every request to the core MUST pass through the Throne before any execution.
2. No organ may self-permit or execute work without a Throne permit.
3. On a DENY verdict, execution MUST NOT proceed. There is no override inside the core.
4. The Throne does not admit a task-pack that is wrong in form, incorrect, or incomplete.
5. Every Throne decision MUST be recorded as a permit receipt (throne_permit_receipt schema).

## Admission Gate

A task-pack is admitted only if it passes all three gates:

- FORM — the task-pack matches its required schema/shape: valid manifest, declared task identity, declared target organ(s), declared evidence plan. Wrong form => DENY (FORM_INVALID).
- COMPLETENESS — all required parts are present: manifest, receipts plan, and owner decision where required. Missing parts => DENY (TASKPACK_INCOMPLETE).
- CORRECTNESS — declared content is internally consistent and does not contradict canon or current state: clean state, no fake-green, no stale receipt. Unproven or contradictory => DENY (CORRECTNESS_UNPROVEN / CANON_VIOLATION / DIRTY_STATE / FAKE_GREEN_DETECTED).

## Permit Verdicts

- PERMIT — admitted; dispatch to the named organ(s) under the Throne.
- PERMIT_WITH_CONDITIONS — admitted only under listed conditions; the conditions are binding.
- DENY — refused; execution forbidden; deny_reasons listed.

## Deny Reasons (enumerated)

FORM_INVALID, TASKPACK_INCOMPLETE, CORRECTNESS_UNPROVEN, CANON_VIOLATION, DIRTY_STATE, FAKE_GREEN_DETECTED, OWNER_DECISION_MISSING.

## Flow

owner / task-pack -> ASTRONOMICON registers task identity and route -> THRONE admission gate -> PERMIT or DENY (permit receipt) -> on PERMIT, organs lead -> SERVITOR executes within an isolated CLI session -> receipts -> INQUISITION and CUSTODES guard -> closure under ADMINISTRATUM. On any DENY, stop.

## Control and Storage Root

- The Throne is the core control point: it is the only authority that admits work into the core.
- The Throne is the core storage root: core admission state, permit receipts, and core-root pointers are held under Throne authority.
- This does not move organ-owned content out of organs; organs keep their life zones. The Throne holds the admission and control layer above them.

## Forbidden Claims (ultimatum)

- No organ self-permits.
- No execution on DENY.
- No permit without a complete, correct, valid-form task-pack.
- No fake-green permit: no PERMIT on E1-only or unverified evidence where E3+ is required.
- No silent dirty-state admission.
- This V0.1 base does NOT yet claim live runtime enforcement. It claims the permit LAW and the routing/descriptor. Runtime enforcement requires E3+ replay and is a later phase.

## Acceptance Boundary

V0.1 MAY claim: the Throne gateway law, the nine-under-Throne routing, the admission gate definition, the permit receipt shape, and the Throne as control/storage root of the core. It MAY NOT claim: live runtime permit enforcement, complete per-organ deep contracts (reviewed later), or WARP/Servitor runtime readiness.

## Provenance

Authored in Phase O step 3 (Throne gateway base). evidence_level=E1_FILE_EXISTS. Throne permit and runtime authority are declared as law here, not yet proven at runtime.
