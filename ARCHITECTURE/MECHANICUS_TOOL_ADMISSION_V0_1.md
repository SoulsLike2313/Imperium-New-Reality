# Mechanicus Tool Admission V0.1

## Purpose
Mechanicus Tool Admission V0.1 is a deterministic foundation layer for evaluating external tooling before installation or operational use inside IMPERIUM.

It answers:
- what tool is being considered;
- why the tool is needed;
- who owns the decision;
- what capability is expected;
- what risks must be controlled;
- what evidence is required before approval;
- what receipts are required after any future use.

## Relation To Phases 1-9
This phase is downstream of NewGen foundations already established:
1. Task Kernel Registry V0.1.
2. Astronomicon Task Formation V0.1.
3. 8-Organ Scoping Corridor V0.1.
4. Servitor Run/Rerun Loop V0.1.
5. Task State + Evidence Binder V0.1.
6. Visual Brain Task Corridor V0.1.
7. Organ Packet Protocol V0.1.
8. Architecture map and bounded operating language.
9. Skill Growth System V0.1.

Phase 10 does not replace those layers. It adds controlled tool-admission contracts that future tasks can consume.

## Admission States
Controlled states for this version:
- `CANDIDATE_ONLY`
- `AVAILABLE_ON_HOST_UNVERIFIED_FOR_IMPERIUM`
- `AVAILABLE_ON_HOST_VERIFIED_BASIC`
- `DEFERRED_NEEDS_OWNER`
- `DEFERRED_NEEDS_ADMISSION_TASK`
- `BLOCKED_BY_RISK`
- `APPROVED_FOR_FUTURE_INSTALL_TASK`
- `APPROVED_FOR_READ_ONLY_USE`
- `INSTALLED_AND_REGISTERED`

V0.1 default posture: candidate/deferred, not installed.

## Allowed And Forbidden Claims
Allowed claims:
- foundation contracts exist for candidate/risk/decision/receipt/index records;
- deterministic builder and validator are available;
- candidate tools are tracked with explicit decision states;
- no-install policy is active for this phase.

Forbidden claims:
- production toolchain readiness is already achieved;
- Playwright/Vitest/ESLint/Storybook/Nx/Turborepo were installed by this phase;
- unrestricted external-tool approval already exists;
- autonomous production package management is already proven.

## Proof Requirements
Before future installation approval, each tool must have:
- candidate record with ownership and rationale;
- risk record with mitigation and severity;
- explicit decision record with allowed/forbidden actions;
- evidence references for admission checks;
- receipt requirements for post-use traceability.

PASS-level claims require machine-readable evidence artifacts and a validator report.

## Tool Lifecycle
V0.1 lifecycle:
1. Register tool candidate.
2. Attach risk controls and mitigation plan.
3. Emit bounded decision record.
4. Require evidence for any state promotion.
5. Emit capability receipt only after bounded use.
6. Update registry index and reports.

## No-Install Rule For V0.1
This phase does not install new external packages.
All listed tools are treated as candidates/deferred unless a separate installation task provides proof and explicit Owner-admitted scope.

## Future Install Workflow
A future install task may promote a candidate only when:
1. Owner gate admits install scope.
2. Risk gates are satisfied.
3. Install receipts are produced.
4. Capability receipts confirm bounded operation.
5. Decision state is updated to an approved installed state with evidence.

## Owner-Facing Interpretation
What exists now:
- a governed admission protocol and deterministic records.

What does not exist yet:
- approved production installation outcomes.

What this enables:
- controlled future tasks for Playwright/Vitest/ESLint/Storybook/Nx/Turborepo and CLI UI candidates without chaotic installs.
