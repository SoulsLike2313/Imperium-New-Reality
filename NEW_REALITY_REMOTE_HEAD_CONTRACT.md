# New Reality Remote HEAD Contract

Status: CANDIDATE_REMOTE_HEAD_CONTRACT_V0_1
Owner organ: ADMINISTRATUM
Support organs: MECHANICUS, INQUISITION

## Purpose

Define how New Reality proves remote truth after commit and push.

## Canonical Remote

```text
https://github.com/SoulsLike2313/Imperium-New-Reality.git
```

## Required Checks

1. Local branch is `master`.
2. `origin` URL equals the canonical remote exactly.
3. Push command is a normal non-force push.
4. `git ls-remote origin refs/heads/master` returns the same 40-character commit as local `git rev-parse HEAD`.
5. Receipts distinguish implementation/policy payload proof from any later closure receipt commit.

## Blocking Conditions

- Remote URL mismatch.
- Remote has unrelated history.
- Force push needed.
- Ancient Empire mutation or push.
- Empty or malformed local/remote HEAD fields.

## Evidence Level

Remote equality is an E3 runtime claim only when backed by the executed `git ls-remote` command result.
