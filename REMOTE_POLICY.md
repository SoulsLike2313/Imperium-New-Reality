# New Reality Remote Policy

Status: ACTIVE_REMOTE_POLICY_V0_1
Owner organ: ADMINISTRATUM
Support organs: MECHANICUS, ASTRONOMICON, INQUISITION

## Active Remote

New Reality uses only this owner-authorized remote for PC `master` pushes:

```text
https://github.com/SoulsLike2313/Imperium-New-Reality.git
```

Git remote name:

```text
origin
```

Active branch:

```text
master
```

## First Push Rule

Before the first push, the agent must run `git ls-remote --heads https://github.com/SoulsLike2313/Imperium-New-Reality.git`.

- If no heads are returned, first push may proceed.
- If `refs/heads/master` exists and equals local HEAD, a normal non-force push may proceed.
- If any unrelated or unexpected remote history exists, stop with `REMOTE_NOT_EMPTY_REQUIRES_OWNER_DECISION`.

## Forbidden

- No force push.
- No push to Ancient Empire.
- No remote URL other than `https://github.com/SoulsLike2313/Imperium-New-Reality.git`.
- No clean PASS without remote HEAD equality proof.

## Evidence

Required receipts:

- `pc_new_reality_remote_policy_receipt.json`
- `remote_push_receipt.json`
- `remote_head_equality_receipt.json`
- `git_closure_receipt.json`
