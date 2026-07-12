# Acceptance Gates

The corridor may be labeled `REFERENCE_CORRIDOR_READY_FOR_OWNER_REVIEW` only when all critical gates are proven by current receipts:

1. Exact audit HEAD, clean master, `master == origin/master`, branch and PowerShell 7.6.2 are re-proven.
2. External WARP is a Git worktree created from the exact base HEAD and carries Git metadata.
3. One persisted task transaction controls state with atomic transitions and stale-base blocking.
4. One canonical capability registry drives backend and UI; unknown capabilities are denied.
5. Typed execution records argv, executable/hash, cwd, environment, timeout, outputs, filesystem diff and pre/post Git truth.
6. Mutations outside the active WARP and any Reality/master write attempt are blocked.
7. Direct Tauri `RUN_*.ps1` execution is unreachable.
8. Great Nine plus Throne each produce deterministic preflight and postcheck evidence.
9. Owner gates block launch, accept/reject, land preparation, discard and destroy without explicit decisions.
10. UI renders backend state and action contracts; no local green fallback or action list exists.
11. Diagnostic demo returns Git root/context, exact HEAD, dirty state, PowerShell executable/version and Great Nine count/source.
12. All 20 mandatory adversarial scenarios have expected/actual verdict, unchanged-Reality proof and receipt path.
13. Evidence envelopes validate and finalized evidence tampering is detected.
14. State survives restart; full restore works; partial restore is honestly blocked as not implemented.
15. WARP reject/discard/destroy and disposable atomic land/rollback are proven in fixtures.
16. Required human and machine artifacts exist, parse and are hash-indexed.
17. Known gaps contain every `NOT_PROVEN`, `DEFERRED` and scaffold-only feature.
18. No land/merge/push to master occurred and `origin/master` remains the audit HEAD.

Any failed critical gate yields `REFERENCE_CORRIDOR_PARTIAL_NOT_READY`.
