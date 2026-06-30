# Passport, Constitution, and AGENTS Patch Plan

Mode: plan only. No core document was rewritten by this task.

## Discovery result

`AGENTS.md` exists at root and is active.

No active `Emperor Passport` or `Constitution` artifact was found by file-name search or content search inside the New Reality root. The only matches were references inside this taskpack. Because these authorities are absent or not named in current root, this task cannot safely propose line-level patches to existing Passport/Constitution files.

## Guardrail

Do not create or rewrite Emperor Passport or Constitution in an implementation task until Owner confirms canonical target paths and document authority. These documents are authority-bearing; guessing their paths would be fake green.

## Proposed AGENTS.md patch

Target: `AGENTS.md`.

Purpose: make the current PC/New Reality boundary explicit after root migration and prevent old-prefix/remote drift.

Patch intent:

```text
Add after the existing default rules:

Current active root shape:
- Active PC truth is this repository root, not IMPERIUM_NEW_GENERATION, VM2, VM3, Ancient, report archives, or quarantine.
- Active top-level operational homes are AGENTS.md, ORGANS/, REPORTS/, SUPPORT/, and .gitignore.
- Ignored folders, __pycache__, .taskpack_import_tmp, organ legacy mirrors, report history, and SUPPORT/QUESTIONABLE_OR_QUARANTINE are safe to read as evidence only when cited; they are not active canon by location.
- PC tasks must not require VM2/VM3 state unless the task manifest explicitly targets a remote contour.
- Path discovery must prefer current-root ORGANS/ and SUPPORT/ paths. Legacy IMPERIUM_NEW_GENERATION paths may be read only as compatibility evidence and must emit a warning.
- If Emperor Passport or Constitution are needed and no active target path exists, stop for Owner decision instead of inventing authority.
```

Expected effect: future Servitors have a short root-level rule that matches the current physical layout and blocks old-prefix assumptions.

## Proposed Constitution patch

Target: owner decision required. Candidate path should be chosen before implementation.

Recommended authority owner: `DOCTRINARIUM`, with `CUSTODES` audit and `ADMINISTRATUM` evidence custody.

Candidate content sections:

```text
1. Active Truth Boundary
   - New Reality PC root is active truth for PC tasks.
   - Ancient, VM2, VM3, reports, support imports, and quarantine are not active truth unless admitted.

2. Core Shape
   - Required nine organs are listed from ORGANS/_CORE_GOVERNANCE/REQUIRED_9_ORGANS_V0_1.json.
   - _CORE_GOVERNANCE and _POST_WORK_RING are auxiliary governance, not organs.
   - SPECULUM requires explicit auxiliary/future/candidate classification.

3. Canon vs Candidate
   - Candidate contracts may govern Stage execution only within their stated warning boundary.
   - Canon admission requires explicit Doctrinarium/Custodes/Admin evidence.

4. Contour Law
   - PC tasks are local by default.
   - Remote routes require explicit target contour and Owner-approved task scope.

5. Cleanup Law
   - Quarantine, learning archive, report history, and duplicates require retention/admission decisions before delete/move.
```

Expected effect: the Constitution becomes the durable law document for active truth, contour routing, and canon admission.

## Proposed Emperor Passport patch

Target: owner decision required. Candidate path should be chosen before implementation.

Recommended owner: `ADMINISTRATUM` for custody, with `OFFICIO_AGENTIS` for owner-facing language and `DOCTRINARIUM` for authority boundary.

Candidate content sections:

```text
1. Non-secret Identity Boundary
   - Passport records public/non-secret identity and authority metadata only.
   - It must not store credentials, private keys, tokens, SSH secrets, or personal private data.

2. Owner Authority Boundary
   - Owner approval is required for remote execution, cleanup, canon admission, tool installation, and authority-document creation.

3. Active Contour
   - PC is current local execution contour unless task manifest says otherwise.

4. Evidence Requirements
   - Any PASS claim must cite report paths, git truth, and command receipts.

5. Missing Authority Handling
   - If Passport/Constitution cannot be found, report the absence and ask for canonical path rather than synthesizing one.
```

Expected effect: the Passport becomes a safe owner-authority card without becoming a secret store.

## Implementation order

1. Owner selects canonical paths for Constitution and Emperor Passport.
2. Create a small taskpack to patch `AGENTS.md` plus create/update only the confirmed authority paths.
3. Include Doctrinarium and Officio review receipts.
4. Run root-shape and language gates.
5. Commit after evidence; no push without Owner approval.

