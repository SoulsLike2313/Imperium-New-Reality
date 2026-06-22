# KERNEL_BOUNDARY_CONTRACT

```yaml
task_id:        DOCTR-TOOLS-0001
law_id:         DOCTR.LAW.KERNEL_BOUNDARY.v1_0
version:        1.0.0
lineage:        master 59159278802dc37da1386ca7451eadd8b96f6f06
authored_by:    NOTION_OPUS (CHAT / Opus 4.5)
target_organ:   DOCTRINARIUM
schema_version: imperium.law.v0_1
echolon:        1
status:         OBSERVER
severity:       BLOCKING (when ENFORCED)
seal_required:  EMPEROR_SEAL_v0_1 (when ENFORCED)
```

## §0 NO_LLM_IN_PIPELINE

This law is read and enforced by deterministic stdlib code only.
No LLM call MAY produce, modify, or sign a kernel-boundary verdict.
LLM-authored prose MAY recommend; only `kernel_write_guard_v0_1.py` decides.

## §1 Purpose

KERNEL is the irreducible authority layer of Imperium. A kernel write changes
rules-of-the-game for every actor. KERNEL_BOUNDARY_CONTRACT defines:

1. WHICH paths constitute the kernel.
2. WHO may attempt a kernel write.
3. WHAT receipts must accompany a kernel write.
4. WHEN the contract is OBSERVER (log-only) vs ENFORCED (block-on-violation).

## §2 KERNEL_PATTERNS (canonical, forward-slash)

The following glob patterns, evaluated against the path of any tracked file
added, modified, or deleted in a commit, define the kernel:

```
ORGANS/_CORE_GOVERNANCE/CONSTITUTION/**
ORGANS/_CORE_GOVERNANCE/EMPEROR/**
ORGANS/_CORE_GOVERNANCE/THRONE/**
ORGANS/_CORE_GOVERNANCE/GOVERNANCE_INDEX.json
ORGANS/_CORE_GOVERNANCE/REQUIRED_9_ORGANS_V0_1.json
ORGANS/_CORE_GOVERNANCE/SCHEMAS/imperium.constitution.*
ORGANS/_CORE_GOVERNANCE/SCHEMAS/imperium.passport_of_the_emperor.*
ORGANS/_CORE_GOVERNANCE/SCHEMAS/imperium.throne_*
ORGANS/_CORE_GOVERNANCE/TOOLS/core_self_validation*
ORGANS/_CORE_GOVERNANCE/TOOLS/organ_life_validator*
ORGANS/_CORE_GOVERNANCE/TOOLS/quarantine_active_use_checker*
ORGANS/_CORE_GOVERNANCE/MATRICES/required_organs*
DOCTRINARIUM/CHARTERS/DOCTRINARIUM.md
DOCTRINARIUM/CHARTERS/DOCTRINARIUM.en.md
ORGANS/DOCTRINARIUM/LAWS/KERNEL_BOUNDARY_CONTRACT.md
ORGANS/DOCTRINARIUM/LAWS/CANONICAL_PIPELINE.md
```

NON-KERNEL: every other path in the repository. Non-kernel writes follow the
ordinary canon-admission boundaries (see CANONICAL_PIPELINE §3) but DO NOT
require EMPEROR_SEAL.

The pattern list is authoritative in this file. `kernel_write_guard_v0_1.py`
MUST parse this file to derive its patterns; it MUST NOT hard-code a separate
list.

## §3 Authorized actors for kernel writes

| Actor          | Authority for kernel write             | Notes                                   |
|----------------|----------------------------------------|-----------------------------------------|
| OWNER_MANUAL   | YES, sovereign                         | Bypass authority of last resort.        |
| THRONE         | YES, only with valid EMPEROR_SEAL_v0_1 | Enforced by `kernel_write_guard`.       |
| LOGOS_PRIME    | NO (proposes only)                     | May draft + sign as author; cannot land.|
| SPECULUM       | NO                                     | Audit only.                             |
| SERVITOR_*     | NO                                     | Executes plans only.                    |
| Any other      | NO                                     | Refused at guard.                       |

A kernel write executed during DOCTR-TOOLS-0001 itself is permitted under
OWNER_MANUAL sovereign bypass; the guard records the bypass in its receipt.

## §4 Required receipts for a kernel write (when ENFORCED)

All of the following MUST be produced and persisted with the kernel-touching
commit:

1. `imperium.kernel_write_guard.v0_1` receipt with `verdict: ALLOW`.
2. `imperium.throne_permit.emperor_seal.v0_1` receipt with non-expired TTL.
3. `imperium.snapshot_digest.v0_1` of the repository state immediately before
   the kernel write (so the prior kernel can be reconstructed).
4. `imperium.e3_results.v0_1` showing E3 self-tests of the touched organ pass.
5. Append-only entry in `ORGANS/_CORE_GOVERNANCE/EMPEROR_SEAL_LEDGER.jsonl`
   (added by DOCTR-EMPEROR-SEAL-0001).

Missing receipt = guard verdict DENY.

## §5 OBSERVER vs ENFORCED modes

- **OBSERVER** (this release, v0_1): guard runs, computes verdict, writes
  receipt, prints verdict. NEVER blocks. Owner reviews verdicts and tunes.
- **ENFORCED** (target, post DOCTR-EMPEROR-SEAL-0001 land): guard verdict
  DENY aborts the operation. Switched on by setting
  `ORGANS/_CORE_GOVERNANCE/EMPEROR/SEAL_STATUS.json:mode=ENFORCED`.

The switch from OBSERVER to ENFORCED is itself a kernel write and requires
the full §4 receipt set.

## §6 Hash-locked rule references

Every receipt MUST embed sha256 of this file at the time of the decision:

```
receipt.law_sha256 = sha256(KERNEL_BOUNDARY_CONTRACT.md)
```

This prevents undetected mutation of the contract between decision and audit.

## §7 Forbidden claims (mirror of charter §9)

With respect to the kernel boundary, the following claims are FORBIDDEN:

- "This kernel write needs no seal because the change is small."
- "OBSERVER mode means the guard verdict is advisory; ignore DENY."
  (OBSERVER means non-blocking; DENY is still a logged failure that MUST be
  investigated.)
- "This file pattern is not in the kernel list, so the file is not part of
  the kernel." (Patterns are exhaustive only for tracked paths; new kernel
  files must be added to §2 in the same commit as their creation.)
- "The guard reads no patterns; trust the LLM judgment."
  (Guard MUST parse this file. LLM judgment is never authoritative.)

## §8 Amendment procedure

This file is itself a kernel path (see §2). Amendments follow §4 receipts.
Alpha-phase amendments before EMPEROR_SEAL activation are permitted under
OWNER_MANUAL bypass with the bypass recorded in the receipt.

## §9 Provenance

```
law_id:        DOCTR.LAW.KERNEL_BOUNDARY.v1_0
authored_at:   captured at pack build (see meta/PROVENANCE.json)
base_sha:      59159278802dc37da1386ca7451eadd8b96f6f06
identity_sig:  see meta/PROVENANCE.json
```

*End of KERNEL_BOUNDARY_CONTRACT v1.0.0.*
