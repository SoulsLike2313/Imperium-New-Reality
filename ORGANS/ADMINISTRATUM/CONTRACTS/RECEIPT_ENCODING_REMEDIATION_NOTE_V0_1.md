# ADMINISTRATUM - Receipt Encoding And Git Truth Note (CANDIDATE_V0_1)

Status: CANDIDATE_NOT_CANON
Destination: ORGANS/ADMINISTRATUM/CONTRACTS/RECEIPT_ENCODING_REMEDIATION_NOTE_V0_1.md

## Problem found

24 receipt JSON (including FINAL_COMMIT_PUSH_RECEIPT.json and role_profile.json) start with a
UTF-8 BOM. A strict json.load() throws on them, so the very receipts that prove closure are
unreadable by machine. This directly undermines "claims require receipts".

## Standing rules for Administratum receipts

1. Every receipt is written ENGLISH UTF-8 NO-BOM, LF, with a trailing newline.
2. Every reader uses encoding='utf-8-sig' so a stray BOM never silently breaks a load.
3. Closure receipts must carry a real repo_head, or AUTHORITY_GAP when .git is absent.
4. Closure is not accepted without a git-truth receipt (verify_git_truth_v0_1.py).

## Remediation step

Run fix_encoding_bom_crlf_v0_1.py --apply, then re-validate every *.json with the hygiene gate.
The 2 intentional malformed fixtures stay malformed (they live under FIXTURES/).

## Reader patch pattern

```python
with open(path, encoding='utf-8-sig') as fh:
    data = json.load(fh)
```
