# ARSENAL POLICY V0.1

## Purpose
Establish legal intake, status transitions, and evidence discipline for Mechanicus capabilities.

## Core Constraints
1. A capability MUST have a card conforming to `capability_card_schema_v0_1.json`.
2. Capability status MUST be one of: `CANDIDATE`, `SANDBOX`, `CANON`, `QUARANTINE`, `REJECTED`.
3. `CANON` status requires explicit evidence path(s) or validation receipt path(s).
4. Any missing source/license/trust note blocks promotion above `CANDIDATE`.
5. Install or network provisioning is forbidden in this foundation task.

## Promotion Rules
1. `CANDIDATE -> SANDBOX` requires bounded test plan and gate acknowledgment.
2. `SANDBOX -> CANON` requires:
- validated execution or repository evidence;
- receipt/report path attached in card;
- no unresolved safety/security blockers.
3. `ANY -> QUARANTINE` if risk, license ambiguity, dirty artifacts, or inconsistent behavior appears.
4. `ANY -> REJECTED` when value is insufficient or risk is unacceptable.

## Evidence Rules
1. Evidence paths must be repository-relative and auditable.
2. Receipts must be JSON and machine-readable.
3. Claims without receipts/evidence are downgraded to `CANDIDATE`.

## Ownership
Default owner organ is `MECHANICUS` unless explicitly reassigned in card metadata.

## Scope Discipline
This foundation controls only Mechanicus Arsenal intake structures and associated reports.
