# Operational Station Workflow

The implemented operator path is:

1. Capture owner intent with `new-task` or Task Console.
2. Classify through OPS and preview route and scope.
3. Apply bounded Mechanicus policy state.
4. Build a six-root-file Astronomicon-compatible taskpack.
5. Validate JSON, language, required files, scope, and SHA256.
6. Dry-run registration by default.
7. Optionally invoke explicit local PC registration for a generated taskpack.
8. Render launch and Servitor Prime handoff cards.
9. Track `HANDOFF_READY` separately from `EXECUTION_PENDING`.
10. Observe reports, receipts, safety, and git closure.

The Station composes existing components. It does not create authority for unrestricted shell, live LLM execution, remote registration, or remote VM operations.
