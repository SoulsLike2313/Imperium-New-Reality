# PC Contour Git Admission

Expected contour: PC.

Expected repo root: `E:/IMPERIUM`.

Required starting truth:

- Branch: `master`, unless repository policy indicates a different active branch.
- Expected starting HEAD: `1c435a944ed6fbf8bbe5ef7c24a0b8a29c1c9860`.
- `origin/master` should equal local HEAD after fetch/pull.
- Worktree must be clean before task modifications.

Minimum checks:

```powershell
git -C E:/IMPERIUM status --short
git -C E:/IMPERIUM branch --show-current
git -C E:/IMPERIUM rev-parse HEAD
git -C E:/IMPERIUM fetch origin
git -C E:/IMPERIUM rev-parse origin/master
```

If local HEAD is behind origin/master and the worktree is clean, a fast-forward pull is allowed.

If local HEAD differs in an unexpected way, stop with a blocker and do not attach evidence to the wrong history.

Create `pc_git_truth_probe.json` in the report directory.
