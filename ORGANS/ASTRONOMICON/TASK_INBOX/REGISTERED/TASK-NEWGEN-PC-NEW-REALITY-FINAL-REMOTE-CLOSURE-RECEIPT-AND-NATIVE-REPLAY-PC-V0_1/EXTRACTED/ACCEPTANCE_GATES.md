# Acceptance Gates

## Local root gates

PASS requires:

- New Reality root is resolved by explicit root/env/marker discovery.
- `EPOCH_MANIFEST.json` exists and identifies `NEW_REALITY`.
- `NEW_REALITY_SCOPE_LOCK.md` exists.
- `AGENTS.md` exists.
- Ancient Empire is not used as active runtime.

## Native Astronomicon gates

PASS requires:

- taskpack registration is executed from New Reality native Astronomicon;
- registered task path is inside New Reality;
- `current_expected_task.json` is updated only for valid intake;
- task resolver passes for the smoke task;
- invalid taskpack is blocked;
- no launch card is emitted for blocked intake.

## Remote gates

PASS requires:

- `origin` points to `https://github.com/SoulsLike2313/Imperium-New-Reality.git`;
- local commit is created;
- push succeeds;
- `git ls-remote origin refs/heads/master` equals local `HEAD`;
- `git status --short --branch` is clean after closure.

## Evidence gates

PASS requires:

- `task_report_bundle.zip` exists;
- bundle SHA256 is written in a receipt and final Owner response;
- final closure receipt records local HEAD, remote HEAD, branch, remote URL, worktree state, and bundle hash;
- Ancient Empire read-only guard receipt exists;
- no fake-green: unknown data must be marked unknown, not guessed.

## Clean PASS rule

Clean PASS is allowed only if every local/root/native/remote/evidence gate passes.

If final bundle cannot contain its own post-bundle commit hash due self-reference, state the limitation clearly and produce a follow-up closure receipt after final push.
