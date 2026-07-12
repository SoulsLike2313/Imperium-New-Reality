# Rollback Plan

- Before land: Owner may reject, discard, then destroy the external WARP through explicit gates; Reality is already unchanged.
- After a future approved land: compare-and-swap the master ref only when it still equals the expected result, restore it to the recorded base on failure, then restore the clean worktree from Git.
- Partial task restore remains blocked; use a full semantic checkpoint restore unless dependency isolation is independently proven.
- Atomic land/rollback behavior is proven only in a disposable Git fixture, never on current master.
