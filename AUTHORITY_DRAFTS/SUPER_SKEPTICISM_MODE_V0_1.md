# Super Skepticism Mode V0.1

## Status
Draft authority for New Generation bounded tasks.
This draft does not override canonical AGENTS or ORGANS law.

## Objective
Prevent template behavior, shallow assumptions, and fake green claims.
Require proof-first execution with explicit uncertainty handling.

## Mandatory loop per meaningful action
1. Claim: what is being asserted or planned.
2. Basis: files, commands, or contracts supporting the claim.
3. Risk: what could be wrong.
4. Scope: what paths/systems may be touched.
5. Proof plan: evidence required before success claim.
6. Action: execute only after proof plan exists.
7. Evidence: record path/output/receipt.
8. Self-verdict: classify confidence using strict taxonomy.
9. Owner-verdict pending: owner decides final acceptance.

## Self-verdict taxonomy
- `PROVED`: direct evidence exists and is inspectable.
- `STRONG`: strong evidence with explicit limitations.
- `PLAUSIBLE`: hypothesis is reasonable but not proven.
- `UNKNOWN`: not verified.
- `FAILED`: contradicted by evidence.
- `FAKE_GREEN_RISK`: success claim likely overstated.

Only `PROVED` and `STRONG` can support pass-level claims.
`PLAUSIBLE`, `UNKNOWN`, `FAILED`, and `FAKE_GREEN_RISK` cannot support PASS.

## Non-negotiable rules
- No gate bypass for speed.
- No scope expansion without explicit receipt.
- No hidden deletion of useful helper artifacts.
- No report avalanche; keep receipts compact and machine-readable.
- No conversion of assumption to fact.
- No pass claim while required deliverables are missing.

## Language and encoding
- Machine-readable artifacts: English, UTF-8 safe.
- Owner-facing brief/report: Russian allowed.
- No mojibake.

## Required evidence surfaces
- `STEP_PROOF_RECORDS.jsonl`
- validator report
- changed-files status
- final receipt with pass/warn/unknown split

## Known limitations
- This draft is task-local and should be promoted to canonical owner only by dedicated follow-up gate.

