# Final Response Contract V0.1

For normal completion responses:

1. Step name.
2. Full path to primary outputs/report bundle.
3. Scoped verdict (`PASS_FOR_<SLICE>_ONLY`).
4. Smoke summary.
5. Commit hash / remote hash / clean status.
6. 3-4 short Owner-facing comments in Russian.
7. Next allowed task.

For auto-push completions:

1. Step name.
2. Verdict.
3. New commit hash.
4. GitHub commit URL.
5. Worktree clean yes/no and remote sync yes/no.
6. Micro-summary in Russian.
7. Next allowed task.

Rules:

- No generic PASS.
- Include NOT_PROVEN boundary.
- Do not claim production autonomy.
- If any critical action was not run, state it explicitly.
