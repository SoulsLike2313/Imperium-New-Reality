# Task Specification

## Task

Establish the official remote policy and first remote HEAD proof for New Reality.

## Purpose

New Reality has already proven local root resolution and native taskpack registry. The next gap is remote truth. This task must give New Reality its own remote line and stop treating the Ancient Empire remote as active work truth.

## Remote

Owner-authorized remote URL:

```text
https://github.com/SoulsLike2313/Imperium-New-Reality.git
```

The remote repository is expected to be empty or safe for first push. If the remote already contains unrelated history, stop and report `REMOTE_NOT_EMPTY_REQUIRES_OWNER_DECISION` unless a safe fast-forward or exact match is proven.

## Required work

1. Verify active root is `E:/IMPERIUM_NEW_GENERATION_NEW_REALITY` through the root resolver.
2. Verify Ancient Empire root `E:/IMPERIUM` is not mutated.
3. Add or update New Reality remote policy files:
   - `REMOTE_POLICY.md`
   - `ANCIENT_EMPIRE_REFERENCE.md`
   - `NEW_REALITY_REMOTE_HEAD_CONTRACT.md`
   - `SCHEMAS/remote_push_receipt.schema.json`
4. Configure git remote `origin` for New Reality to the owner-authorized URL.
5. Commit remote policy and any necessary receipts in New Reality.
6. Push New Reality `master` to the owner-authorized remote.
7. Verify remote HEAD equals local HEAD with `git ls-remote` or equivalent.
8. Produce receipts and a final task report bundle.
9. Final answer must include exact bundle path and SHA256.

## Scope

Allowed:
- Read/write inside New Reality root.
- Read Ancient Empire only for reference if needed.
- Configure New Reality remote to the exact owner-authorized URL.
- Push New Reality branch to the exact owner-authorized remote.

Forbidden:
- Any write to `E:/IMPERIUM`.
- Any push to the Ancient Empire remote.
- Any force push.
- Any remote URL other than `https://github.com/SoulsLike2313/Imperium-New-Reality.git`.
- Any clean pass claim without remote HEAD equality proof.
