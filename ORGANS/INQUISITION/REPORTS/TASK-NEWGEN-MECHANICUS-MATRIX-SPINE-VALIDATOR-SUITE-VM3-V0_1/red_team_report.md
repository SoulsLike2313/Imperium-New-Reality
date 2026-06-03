# Red-Team Report — TASK-NEWGEN-MECHANICUS-MATRIX-SPINE-VALIDATOR-SUITE-VM3-V0_1

Timestamp (UTC): 2026-05-29T22:44:29Z

## Attack scope
- validator replayability
- schema alignment quality
- negative fixture honesty
- fake-green verdict inflation risk

## Findings
1. Replayability claim is supported by executable runners and produced receipts.
2. Schema alignment is meaningful (required runtime fields enforced), but remains candidate-level and not canon.
3. Negative fixtures are detected as expected (three bad cases caught).
4. Full PASS remains blocked by non-canonical status aliases and absent runtime start-task corridor proof.

## Downgrade policy
- PASS escalation denied.
- Final red-team verdict stays `PASS_WITH_WARNINGS`.

## Required follow-up
- normalize remaining `CANDIDATE_NOT_CANON` statuses to canonical vocabulary (or formal alias policy);
- add end-to-end start-task runtime corridor evidence for enforcement claims.
