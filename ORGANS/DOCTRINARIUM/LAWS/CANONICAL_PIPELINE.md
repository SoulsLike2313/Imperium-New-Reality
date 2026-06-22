# CANONICAL_PIPELINE

```yaml
task_id:        DOCTR-TOOLS-0001
law_id:         DOCTR.LAW.CANONICAL_PIPELINE.v1_0
version:        1.0.0
lineage:        master 59159278802dc37da1386ca7451eadd8b96f6f06
authored_by:    NOTION_OPUS (CHAT / Opus 4.5)
target_organ:   DOCTRINARIUM
schema_version: imperium.law.v0_1
echolon:        1
status:         OBSERVER (alpha v0_1)
```

## §0 NO_LLM_IN_PIPELINE

Each pipeline stage is performed by deterministic stdlib code or by an
explicit human actor. LLM-authored prose may PROPOSE inputs; only stage
tools may PRODUCE the stage's receipt.

## §1 Purpose

CANONICAL_PIPELINE is the seven-stage shape every Imperium operation MUST
take to be admitted as canon. The pipeline binds intake to provenance and
makes "fake-green" structurally impossible: every stage produces a receipt
that the next stage consumes.

## §2 The seven stages

```
1. INTAKE        ASTRONOMICON: accept task_id, capture base_sha, manifest skeleton.
2. CHARTER       DOCTRINARIUM: confirm task is admissible against charters + LAWS.
3. BOUNDARY      DOCTRINARIUM: compute kernel-touch verdict via kernel_write_guard.
4. WRITE         MECHANICUS: emit payload, sign aggregate_sha256 + identity_sig.
5. VERIFY        INQUISITION: E3 self-test + contradiction scan + receipt audit.
6. ARCHIVE       ADMINISTRATUM: persist receipts under append-only ARCHIVE tree.
7. RECEIPT       OFFICIO_AGENTIS: produce the user-facing reply citing receipts.
```

Stages 1-7 are owned by the named organs. DOCTRINARIUM owns 2 and 3 jointly
(charter admissibility + kernel boundary). No stage may be skipped. No stage
may be merged with an adjacent stage.

## §3 Canon-admission boundaries (echo of DOCTRINARIUM.md §3)

A task crosses stage 2 (CHARTER) if and only if all six are true:

1. task_id matches the schema `<ORG>-<KIND>-NNNN`.
2. The target_organ is one of the canonical 9 (or _CORE_GOVERNANCE).
3. The pack's stated lineage `base_sha` is reachable from `origin/master`.
4. If the task touches kernel paths (§KERNEL_BOUNDARY §2), an EMPEROR_SEAL
   receipt is attached (or OWNER_MANUAL bypass is declared in the pack
   manifest).
5. The pack carries an `imperium.e3_results.v0_1` for the target organ.
6. No forbidden claim (DOCTRINARIUM.md §9) appears in any pack artifact.

A task that fails any of (1)-(6) is REFUSED at stage 2. The refusal itself
MUST produce a receipt with `verdict: REFUSE` and the list of failed checks.

## §4 Receipt chain

Every stage emits exactly one receipt. The chain is:

```
imperium.intake.v0_1         (stage 1 receipt)
imperium.charter_admission.v0_1   (stage 2)
imperium.kernel_write_guard.v0_1  (stage 3)
imperium.payload.v0_1        (stage 4)
imperium.e3_results.v0_1     (stage 5; one or more)
imperium.archive_entry.v0_1  (stage 6)
imperium.reply_card.v0_1     (stage 7)
```

Each receipt MUST reference the previous receipt by sha256 (`prior_receipt_sha256`).
The chain is verified by `doctrinarium_integrity_validator_v0_1.py`.

A broken chain = task is not canon, regardless of its master commit status.

## §5 Skip and reorder forbidden

- A pack landing without an intake receipt is non-canonical (even if it
  has all other receipts).
- A pack landing without a verify receipt is non-canonical.
- A pack landing with the receipts in a different order is non-canonical.
- A pack landing with one receipt forged (sha256 references break) is
  non-canonical AND triggers INQUISITION quarantine.

Non-canonical packs may exist on master commit history (the pre-charter
era has them); they MUST be retroactively documented in
`ADMINISTRATUM/CANON_RECEIPTS/UNCERTIFIED_v0_1.jsonl` rather than
retrofitted with synthesized receipts.

## §6 Alpha-phase concessions (v0_1)

Until DOCTR-EMPEROR-SEAL-0001 lands and OFFICIO-ROLES-0001 lands:

- Stage 1 receipts MAY be inferred from the pack's `meta/TASK_MANIFEST.json`.
- Stage 7 receipts MAY be inferred from the chat reply summary.
- Stage 4 `identity_sig` is treated as the canonical "payload receipt" until
  a dedicated `imperium.payload.v0_1` exists.

These concessions REMOVE automatically when each successor pack lands;
`doctrinarium_integrity_validator` checks for the presence of the successor
schemas and tightens its mode accordingly.

## §7 Owner / Throne / Logos relationship to the pipeline

```
OWNER_MANUAL  sovereign: may invoke any stage; sovereign bypass authority.
THRONE        gateway:   admits a sealed pack into stage 2 only with seal.
LOGOS_PRIME   author:    drafts artifacts for stages 1-7; cannot sign stages
                         3 (BOUNDARY) or 6 (ARCHIVE).
```

LOGOS_PRIME signature on stages 4, 5, 7 is permitted under v0_1 because
those stages are deterministic stdlib outputs that LOGOS_PRIME merely
orchestrates; the determinism guarantees correctness.

## §8 Forbidden claims (mirror of charter §9)

- "The pipeline is advisory." The pipeline is canon-defining.
- "Stage 5 verify may be skipped because the change is small."
- "The receipt chain is for record-keeping, not for admission."
- "An LLM signature substitutes for a tool receipt."

## §9 Amendment

This law is a kernel path (see KERNEL_BOUNDARY §2). Amendments follow
KERNEL_BOUNDARY §4 receipts. Until ENFORCED activation, OWNER_MANUAL
bypass is the only effective amendment authority.

## §10 Provenance

```
law_id:        DOCTR.LAW.CANONICAL_PIPELINE.v1_0
base_sha:      59159278802dc37da1386ca7451eadd8b96f6f06
authored_at:   captured at pack build (see meta/PROVENANCE.json)
identity_sig:  see meta/PROVENANCE.json
```

*End of CANONICAL_PIPELINE v1.0.0.*
