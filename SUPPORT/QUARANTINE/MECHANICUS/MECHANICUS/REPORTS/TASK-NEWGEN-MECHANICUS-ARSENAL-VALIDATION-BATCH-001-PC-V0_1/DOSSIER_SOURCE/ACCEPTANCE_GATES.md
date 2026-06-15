# Acceptance Gates — TASK-NEWGEN-MECHANICUS-ARSENAL-VALIDATION-BATCH-001-PC-V0_1

## PASS

PASS requires:

1. Worktree starts clean or unrelated dirty state is blocked.
2. Field Guide and Mass Intake outputs were read.
3. Ghost_Evolve contract was followed.
4. P0/P1/P2-lite validation targets were processed.
5. Validation receipts were created for successful checks.
6. Missing tools were not installed silently.
7. Status updates, if any, obey evidence rules.
8. Reusable Mechanicus scripts/checkers were created or improved.
9. Scripts can run again and reports show how.
10. Capability scope exporter exists and produces an example export.
11. Fake-CANON detector runs.
12. Inquisition cleanliness report exists.
13. Administratum evidence map exists.
14. Ghost_Evolve training proof exists.
15. No LLM/cloud activation.
16. No visual prototype work.
17. Commit/push succeeds.
18. Worktree clean and remote sync confirmed.

## PASS_WITH_WARNINGS

Allowed if:

- some external tools are missing and remain CANDIDATE;
- ruff/mypy/pyright/pre-commit are not installed and are queued;
- Playwright/Node are only readiness-detected;
- reusable scripts are minimal but runnable;
- some CANON promotions are deferred.

## BLOCKED

Use if:

- Field Guide/mass intake outputs are missing;
- worktree starts dirty with unrelated files;
- no validation targets can be located;
- scripts cannot be written;
- checks cannot run at all;
- commit/push fails.

## FAIL

Use if:

- tools are installed without Owner approval;
- fake CANON is introduced;
- LLM/cloud adapters are activated;
- visual prototypes are started;
- no reusable Mechanicus strengthening is left;
- reports/receipts are missing.
