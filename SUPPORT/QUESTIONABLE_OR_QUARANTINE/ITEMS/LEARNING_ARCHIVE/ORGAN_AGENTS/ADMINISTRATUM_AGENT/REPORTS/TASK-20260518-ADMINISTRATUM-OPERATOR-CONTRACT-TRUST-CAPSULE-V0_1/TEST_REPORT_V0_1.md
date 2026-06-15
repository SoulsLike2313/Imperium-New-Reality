# Test Report V0.1

## Task
- `TASK-20260518-ADMINISTRATUM-OPERATOR-CONTRACT-TRUST-CAPSULE-V0_1`

## Executed commands
1. `python .../administratum_agent_runner.py --help`
- Result: PASS

2. `python .../administratum_agent_runner.py --no-color status`
- Result: PASS (command exit `0`)
- Run: `RUN-ADMINISTRATUM-20260518-154503-b73a0e`

3. `python .../administratum_agent_runner.py --plain-json --no-color status`
- Result: PASS
- Run: `RUN-ADMINISTRATUM-20260518-154510-8f0cb9`
- Contract keys verified: `status, command, summary, primary_refs, artifacts_written, warnings, why_trust, next_actions, metrics, limitations`

4. `python .../administratum_agent_runner.py --verbose --no-color status`
- Result: PASS
- Run: `RUN-ADMINISTRATUM-20260518-154510-60901f`
- Verified: verbose output includes `METRICS` and `DETAILS` blocks.

5. `python .../administratum_agent_runner.py --no-rich --no-color status`
- Result: PASS
- Run: `RUN-ADMINISTRATUM-20260518-154510-486a6a`

6. `python .../administratum_agent_runner.py --rich --no-color status`
- Result: PASS
- Run: `RUN-ADMINISTRATUM-20260518-154515-6e9bc4`
- Note: shell execution is non-TTY in this test harness, so rich live rendering cannot be visually guaranteed.

7. `python .../administratum_agent_runner.py --no-color doctor-rich`
- Result: PASS
- Run: `RUN-ADMINISTRATUM-20260518-154521-ee8830`

8. `python .../administratum_agent_runner.py --no-color inventory --repo-root E:/IMPERIUM`
- Result: PASS
- Run: `RUN-ADMINISTRATUM-20260518-154527-7b3f65`
- Verified live phase updates with counters/warnings/target.

9. `python .../administratum_agent_runner.py --no-color collect-reality-snapshot --repo-root E:/IMPERIUM`
- Result: PASS
- Run: `RUN-ADMINISTRATUM-20260518-154608-3a4e75`

10. `python .../administratum_agent_runner.py --no-color collect-continuity-pack --repo-root E:/IMPERIUM --include-context true --inventory-max-files 900 --provenance-limit 220`
- Result: PASS (with warnings by design)
- Run: `RUN-ADMINISTRATUM-20260518-154614-6e45bf`
- Verified: continuity maturity capsule file created and linked.

11. `python .../administratum_agent_runner.py --no-color verify-pack-against-reality --repo-root E:/IMPERIUM`
- Result: PASS
- Run: `RUN-ADMINISTRATUM-20260518-154850-3c2a10`

12. `python .../administratum_agent_runner.py --no-color check-all --repo-root E:/IMPERIUM --inventory-max-files 500`
- Result: PASS
- Run: `RUN-ADMINISTRATUM-20260518-154856-548305`
- Evidence:
  - `.../reports/check_all_report.json`
  - `.../reports/check_all_report.md`

13. Owner-readable PDF render validation
- Render source:
  - `.../REPORTS/TASK-20260518-ADMINISTRATUM-OPERATOR-CONTRACT-TRUST-CAPSULE-V0_1/OWNER_REPORT_RENDER_SOURCE_V0_1.md`
- PDF:
  - `.../REPORTS/TASK-20260518-ADMINISTRATUM-OPERATOR-CONTRACT-TRUST-CAPSULE-V0_1/OWNER_REPORT_V0_1.pdf`
- Parse validation:
  - `pypdf` load succeeded
  - page count: `3`

## Assertions verified
- Compact default response contract is rendered.
- `WHY_TRUST` appears in default outputs.
- JSON output remains parseable and stable.
- Verbose mode is more detailed than default.
- Renderer diagnostics command exists and runs.
- Continuity pack includes maturity capsule and self-verdict.
- Runtime outputs remain under `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/`.
- `git status` tracked diff remains scope-bounded to allowed files.
