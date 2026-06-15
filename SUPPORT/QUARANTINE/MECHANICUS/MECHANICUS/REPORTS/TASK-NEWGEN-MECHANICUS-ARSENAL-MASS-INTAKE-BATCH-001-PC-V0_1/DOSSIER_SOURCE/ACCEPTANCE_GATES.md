# Acceptance Gates — TASK-NEWGEN-MECHANICUS-ARSENAL-MASS-INTAKE-BATCH-001-PC-V0_1

## PASS

PASS requires:
1. Existing Mechanicus Arsenal foundation was read.
2. All categories exist and are populated.
3. At least 80 capability cards exist.
4. Cards are organized into category folders.
5. Each card parses as JSON and has required fields.
6. No fake CANON: every CANON card has receipt/evidence.
7. LOCAL_LLM and CLOUD_LLM_ADAPTERS are not CANON.
8. Intake batch registry exists.
9. Category coverage report exists.
10. Fake-CANON detection report exists.
11. Next validation queue exists.
12. Servitor capability scope seed/export exists.
13. Owner questions exist.
14. Checker/report exists.
15. No tool installation happened.
16. No network provisioning happened.
17. No Sanctum visual work happened.
18. Commit/push succeeded.
19. Worktree clean and remote sync confirmed.

## PASS_WITH_WARNINGS

Allowed if total cards are 80+ but below recommended 100, some categories are lightly populated, many tools remain CANDIDATE, trust notes are TO_VERIFY, or checker is minimal.

## BLOCKED

Use if worktree starts dirty with unrelated files, Arsenal foundation is missing, schema cannot be adapted, reports cannot be written, checker cannot run, or commit/push fails.

## FAIL

Use if tools are installed, cloud/LLM adapters are made CANON, fake CANON appears, cards are dumped flat without useful folders, or runtime junk/log/pid/cache is committed.
