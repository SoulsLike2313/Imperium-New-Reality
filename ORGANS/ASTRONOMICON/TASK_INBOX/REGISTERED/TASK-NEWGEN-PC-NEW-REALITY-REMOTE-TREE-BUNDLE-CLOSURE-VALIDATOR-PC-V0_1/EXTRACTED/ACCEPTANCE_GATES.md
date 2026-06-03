# Acceptance Gates

## PASS gates

- New Reality root is used as the only active root.
- Ancient Empire is not mutated.
- Native New Reality Astronomicon is used for registration/replay, not Ancient bridge.
- Validator tool exists and runs successfully.
- Schema exists and validates or at least structurally documents validator receipt.
- Remote URL is the New Reality remote.
- Branch is `master`.
- Local `HEAD == origin/master` after final push.
- `git ls-remote` agrees with local remote tracking branch.
- Worktree is clean after final closure.
- Report bundle exists and SHA256 is recorded.
- Invalid taskpack recheck proves no launch card/start-task after admission block.
- Final Owner response gives exact bundle path and SHA256.

## BLOCK gates

- Any mutation inside Ancient Empire.
- Any push to the Ancient Empire remote.
- Any active runtime use of `E:/IMPERIUM` as repo root.
- Missing report bundle.
- Missing bundle SHA256.
- Claiming remote proof without git remote evidence.
- Admission block still printing launch/start-task after the fix is claimed.
- Worktree dirty at final closure without explicit accepted reason.

## Warning gates

- Git self-reference limit on final closure receipts.
- Optional GitHub browser visibility not checked, if git remote proof passes.
- Historical/report references to Ancient paths remain, if classified as non-runtime and non-mutating.
