# Fixture Report

Task: $taskId

## Checker

- Tool: IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/TOOLS/check_external_finalization_semantics_v0_1.py
- Fixture dir: IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/FIXTURES/EXTERNAL_FINALIZATION_SEMANTICS_V0_1
- Total fixtures: 10
- Fixture checks passed: 10
- Fixture checks failed: 0
- Verdict distribution: PASS=2, PASS_WITH_WARNINGS=4, BLOCK=4

## Required cases covered

1. self-head paradox present
2. guessed self hash used as strict final head
3. external finalization receipt valid
4. missing external delivery head
5. cap closed without closure evidence
6. replay state NONE despite replay receipt
7. replay current-target mismatch
8. stale replay only precise state
9. clean PASS with contradictory finalization semantics
10. valid PASS_WITH_WARNINGS with external finalization pending

## Proof summary

- Failure fixture proof: BLOCK verdicts produced for paradox/contradiction cases.
- Pass fixture proof: valid semantics and stale-only precise state produce PASS.
