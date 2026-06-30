# CHARTER OF THE DOCTRINARIUM ORGAN

- **task_id:** DOCTR-CHARTER-0001
- **version:** 1.0.0
- **lineage:** master d8027a81598f007a46cc85dcdf3cbc73b76b05b3 (after INQ-TOOLS-0001 land)
- **target_organ:** DOCTRINARIUM (this document is stored inside DOCTRINARIUM)
- **canonical_organ:** DOCTRINARIUM
- **echelon:** 1 (Astronomicon → Administratum → Mechanicus → Inquisition → **Doctrinarium**)
- **schema_version:** imperium.charter.v0_1

---

## §0. NO_LLM_IN_PIPELINE (global principle for all 9 organs)

Doctrinarium is a **script-first AI**. LLM calls inside `doctrinarium_*.py`, `imperium_first_boot_*.py`, `kernel_write_guard_*.py` and any other tools of this organ are **FORBIDDEN**. AI ≠ LLM. Decisions about admission / canon / PASS / WARN / BLOCK / E-level are made **using deterministic logic only**:

- file existence checks on disk;
- sha256 content comparison;
- regex matching against KERNEL_PATTERNS;
- JSON Schema validation (JSON-Schema-2020-12 or pure-python jsonschema with no network calls);
- tabular comparison of evidence_level → permitted authority;
- receipt-chain counting.

Any attempt to invoke an LLM from Doctrinarium tools is a `DOCTR_FAILED_CLOSED` incident. It is logged in `_HARNESS/_NEGATIVE_EXPERIENCE/`.

LLM outputs happen **only outside** the organ — on the side of pack signers (NOTION_OPUS / CODEX / GROK). Inside the Doctrinarium: zero LLM, zero network, zero non-determinism.

---

## §1. Mission

The Doctrinarium is the **repository of execution laws and the canon of the Imperium**. This is not a runtime check of code (that is Mechanicus) and not a semantic check of content (that is Inquisition). It is the **upper layer**: what has the right to become Imperium canon at all, what execution laws the Imperium operates under, and which claims are forbidden without corresponding evidence.

### §1.1. Seven zones of responsibility

1. **Execution law** — authored law documents under `LAWS/`. Existing layer: clean-and-honest, evidence-vault batch (dry-run/plan/execution/receipt), trinity-related (patch, hygiene, plus-bilingual), repo-hygiene-lane, storage-index, intelligence-pack, ghost-evolve-v2, owner-gated-hygiene, h-contour-patch-backup. New layer from `DOCTR-TOOLS-0001`: kernel-boundary, canonical-pipeline, entry-protocol-for-llm, emperor-seal-placeholder, role-registry.
2. **Canon admission** — matrices `MATRICES/CANON_ADMISSION_MATRIX.{json,md}`. They define: what → `CANON_ACTIVE`, what → `CANDIDATE_V0_1`, what → `BLOCK`.
3. **Forbidden claims** — registry of statements that an organ, actor or task-pack must not assert. Examples: runtime authority without an E3+ replay, throne permit without an active gateway, kernel-write without Emperor Seal, fake-green without receipts.
4. **Evidence levels (E0–E6)** — Doctrinarium is the owner-of-record for tables mapping `evidence_level → permitted authority`. E0 = claim only. E1 = file exists. E2 = self-test declaration. E3 = reproducible replay via `_HARNESS/RUNNER/e3_runner.py`. E4–E6 — multi-actor counter-signs + temporal locks (reserved for future echelons).
5. **Role registry doctrine** — registry of Imperium actor roles and their permitted mandates. As of v1.0.0: OWNER_MANUAL (sovereign), THRONE (gateway), LOGOS_PRIME (strategic planner, currently NOTION_OPUS), SPECULUM (DORMANT — fork reserve), SERVITOR_PRIME (executor, currently CODEX + GROK), ROGUE_TRADER + FREE_ARCHITECT (PLANNED for echelons 4+).
6. **Kernel boundary** — the `KERNEL_PATTERNS` specification: glob patterns for files that are untouchable without Emperor Seal. The exact list is in `LAWS/KERNEL_BOUNDARY_CONTRACT_V0_1.md` (arrives in `DOCTR-TOOLS-0001`).
7. **Canonical pipeline** — a formal 7-stage contract for the pack lifecycle: PACK_AUTHORED → SHAKEDOWN_LOCAL → PR_OR_BUNDLE → INQUISITION_RED_TEAM → MECHANICUS_TOOL_VALIDATE → THRONE_PERMIT_OR_OBSERVER → LAND_TO_MASTER. Details are in `LAWS/CANONICAL_PIPELINE_V0_1.md` (arrives in `DOCTR-TOOLS-0001`).

---

## §2. What the Doctrinarium DOES NOT do

To keep organ boundaries clean:

- It **does not own runtime tools** for Mechanicus / Inquisition / Custodes. Each has its own toolchain.
- It **does not issue Throne permits**. The Throne is a gateway ABOVE the 9 organs (see `ORGANS/_CORE_GOVERNANCE/THRONE/THRONE_GATEWAY_CONTRACT_V0_1.md` and `REQUIRED_9_ORGANS_V0_1.json:throne_scope`).
- It **does not decide on specific task-packs**. That is the competence of: Inquisition (red-team), Mechanicus (tool/receipt validation), Astronomicon (admission), Officio_Agentis (final response discipline).
- It **does not modify** Constitution / Passport / GOVERNANCE_INDEX. Any amendment to kernel documents requires Emperor Seal (`DOCTR-EMPEROR-SEAL-0001`, a separate echelon 1 pack).
- It **has no write access outside `clone\`** (active root). AGENTS.md root contract states: "Read/write/mutate only inside this root". No Ancient / VM2 / VM3 / quarantine.
- It **does not assess actor trust-scores**. Trust-score belongs to Inquisition (see `ORGANS/INQUISITION/TRUST/authors.json`).

---

## §3. What counts as canon (admission boundaries)

A document becomes `CANON_ACTIVE` when **ALL** of the following hold:

1. It lives inside `clone\` (active root), not in Ancient / VM2 / VM3 / quarantine / SUPPORT.
2. It has passed an E3+ self-test via `_HARNESS/RUNNER/e3_runner.py --organ <name>`.
3. It has a receipt in `_HARNESS/_RUNS/<utc>/RESULTS.json` with status PASS (schema `inq.e3_results.v0_1`).
4. It is signed by a valid actor from ROLE_REGISTRY with a non-empty trust-score (not BANNED by Inquisition).
5. It does not contain secrets / PI-markers / fake-green markers (`inq_secrets`, `inq_pi_scan`, `inq_audit` all PASS).
6. It is recorded in `GOVERNANCE_INDEX.json:documents[].status = "CANON_ACTIVE"` OR mentioned in the relevant organ's `ORGAN_CARD.json` under `validators` / `owned_matrices` / `owned_metrics`.

A document remains `CANDIDATE_V0_1` when only conditions 1–4 hold but not 5–6. **A candidate has no authority** until promotion. Any reference to a candidate as canon is a fake-green incident.

---

## §4. File structure of DOCTRINARIUM

After `DOCTR-CHARTER-0001` + `DOCTR-TOOLS-0001` land, the organ structure looks like:

```
ORGANS/DOCTRINARIUM/
├── ORGAN_CARD.json                              # canonical, edit-merge via DOCTR-TOOLS-0001
├── ORGAN_CONTRACT.md                            # canonical, edit-merge
├── READ_FIRST_GHOST_EVOLVE_PACKET.md            # canonical
├── LAWS/
│   ├── (22 existing law documents)
│   ├── KERNEL_BOUNDARY_CONTRACT_V0_1.md         # from DOCTR-TOOLS-0001
│   ├── CANONICAL_PIPELINE_V0_1.md               # from DOCTR-TOOLS-0001
│   ├── ENTRY_PROTOCOL_FOR_LLM_V0_1.md           # from DOCTR-TOOLS-0001
│   ├── EMPEROR_SEAL_PLACEHOLDER_V0_1.md         # from DOCTR-TOOLS-0001
│   └── ROLE_REGISTRY_V0_1.json                  # from DOCTR-TOOLS-0001
├── MATRICES/
│   ├── (4 existing matrices with .json + .md mirrors)
│   └── KPD_METRIC_SPEC_V0_1.{md,json}           # from DOCTR-TOOLS-0001 (doctrinal spec)
├── SCHEMAS/                                     # NEW directory (from DOCTR-TOOLS-0001)
│   └── role_registry.schema.json
├── TOOLS/                                       # NEW directory (from DOCTR-TOOLS-0001)
│   └── doctrinarium_integrity_validator_v0_1.py
├── TESTS/                                       # NEW directory
│   ├── test_doctr_charter_e3.py                 # from this pack (DOCTR-CHARTER-0001)
│   └── test_doctr_tools_e3.py                   # from DOCTR-TOOLS-0001
├── BLOCK/                                       # canonical, unchanged
└── TASK_PARTICIPATION/                          # edit-merge ORGAN_TOOL_AND_RECEIPT_INVENTORY.json
```

In `DOCTR-TOOLS-0001` the following also go into the core zone:

```
ORGANS/_CORE_GOVERNANCE/
├── SCHEMAS/
│   ├── entry_protocol_ack.schema.json           # NEW
│   └── kernel_integrity_snapshot.schema.json    # NEW
└── TOOLS/
    ├── imperium_first_boot_v0_1.py              # NEW
    └── kernel_write_guard_v0_1.py               # NEW (OBSERVER mode v0_1)
```

---

## §5. Link to GOVERNANCE_INDEX (authority order)

The Doctrinarium **subordinates itself** to the existing chain from `GOVERNANCE_INDEX.json:authority_order`:

1. **Emperor Passport** (rank 1) — above the Doctrinarium. Amendments only through Emperor Seal.
2. **Constitution of the Imperium** (rank 2) — above the Doctrinarium. Amendments only through Emperor Seal.
3. **AGENTS.md** (rank 3) — boot-law entrypoint for every executor. The Doctrinarium reads it first.
4. **Organ contracts and read-first files** (rank 4) — this is where the Doctrinarium's LAWS/ live.
5. **Astronomicon taskpacks** (rank 5) — current task execution.
6. **Tool cards and validators** (rank 6) — Mechanicus territory.
7. **Reports and receipts** (rank 7) — Inquisition + Administratum territory.

The Doctrinarium **does not compete** with this chain; it formalizes it via `LAWS/ROLE_REGISTRY_V0_1.json`, `LAWS/KERNEL_BOUNDARY_CONTRACT_V0_1.md`, `LAWS/CANONICAL_PIPELINE_V0_1.md`.

---

## §6. Links to the other 8 organs of the Imperium

**Gives:**

- → **Officio_Agentis**: ROLE_REGISTRY (for role routing and owner-facing language authority).
- → **Strategium**: KPD_METRIC_SPEC (doctrinal spec of the metric; Strategium implements tools).
- → **Inquisition**: KERNEL_PATTERNS (to detect unauthorized kernel writes).
- → **Astronomicon**: CANONICAL_PIPELINE (for admission and route manifests).
- → **Mechanicus**: ENTRY_PROTOCOL_FOR_LLM (for tool-invocation discipline).
- → **Custodes**: ORGAN_LIFE_ZONE granular rules (via core CONTRACT references).
- → **Schola_Imperialis**: reusable lesson templates (already partly via `LAWS/CLEAN_AND_HONEST_SYSTEM_LAW_V0_1.md`).
- → **Administratum**: evidence-vault doctrines (most existing LAWS are already about this).

**Receives:**

- ← **Inquisition**: red verdicts if a pack violates doctrine. The Doctrinarium reads `inq_*` reports as input to admission decisions.
- ← **Mechanicus**: receipts with evidence_level. The Doctrinarium tabulates level → authority.
- ← **Astronomicon**: taskpack identity + route manifest. The Doctrinarium checks admission.
- ← **Administratum**: continuity packs + closure receipts.

---

## §7. KERNEL_PATTERNS (kernel boundary, brief)

Full specification: `LAWS/KERNEL_BOUNDARY_CONTRACT_V0_1.md` (from DOCTR-TOOLS-0001). Short list of paths that cannot be written without Emperor Seal:

- `ORGANS/_CORE_GOVERNANCE/CONSTITUTION/*` (the whole folder)
- `ORGANS/_CORE_GOVERNANCE/EMPEROR/*`
- `ORGANS/_CORE_GOVERNANCE/GOVERNANCE_INDEX.json`
- `ORGANS/_CORE_GOVERNANCE/REQUIRED_9_ORGANS_V0_1.json`
- `ORGANS/_CORE_GOVERNANCE/CORE_*_CONTRACT_V*.md`
- `ORGANS/_CORE_GOVERNANCE/ORGAN_LIFE_ZONE_CONTRACT_V*.md`
- `ORGANS/_CORE_GOVERNANCE/QUARANTINE_USE_BAN_CONTRACT_V*.md`
- `ORGANS/_CORE_GOVERNANCE/SUPPORT_ZONE_CONTRACT_V*.md`
- `AGENTS.md` (root)
- `DOCTRINARIUM/CHARTERS/*` (this file and its siblings)

`kernel_write_guard_v0_1.py` (OBSERVER mode at v0_1) detects write attempts into these paths and logs them under `_HARNESS/LEDGERS/`. BLOCKING mode activates only after `DOCTR-EMPEROR-SEAL-0001`.

---

## §8. Canonical pipeline (7 stages, brief)

Full specification: `LAWS/CANONICAL_PIPELINE_V0_1.md` (from DOCTR-TOOLS-0001). Brief description of stages:

1. **PACK_AUTHORED** — LOGOS_PRIME (NOTION_OPUS) assembles the pack from payload files + build script + signature.
2. **SHAKEDOWN_LOCAL** — `python3 _HARNESS/RUNNER/e3_runner.py --organ <NAME>` passes locally, RESULTS.json has status PASS.
3. **PR_OR_BUNDLE** — the pack is delivered to OWNER_MANUAL either via PR or as an ops-bundle .zip.
4. **INQUISITION_RED_TEAM** — `inq_pi_scan`, `inq_secrets`, `inq_audit` run on payload files. All three PASS.
5. **MECHANICUS_TOOL_VALIDATE** — every new tool has a tool card, a schema validation, and a command-policy entry.
6. **THRONE_PERMIT_OR_OBSERVER** — at echelon 1 (no Emperor Seal) the Throne operates in OBSERVER mode, issuing `throne_permit_receipt.v0_1` with status=OBSERVER.
7. **LAND_TO_MASTER** — squash-merge into master with the commit message in the golden template (task / branch / base / landed / Authored-by / identity_sig).

Each stage produces one receipt in `_HARNESS/_RUNS/<utc>/`.

---

## §9. Forbidden claims (detailed)

Forbidden assertions that every actor must check before approval:

- **"Runtime authority confirmed"** without an E3+ self-test receipt. At E1 (file exists) the authority is NOT runtime; it is only structural.
- **"Throne permit granted"** without an active gateway. At echelon 1 it is OBSERVER, not PERMIT.
- **"Canon updated"** without a record in `GOVERNANCE_INDEX.json:documents[]`.
- **"All tests passing"** without RESULTS.json showing status=PASS and a non-empty `tests[]` array.
- **"Kernel document updated"** without an Emperor Seal receipt.
- **"Actor trust-score confirmed"** without a record in `ORGANS/INQUISITION/TRUST/authors.json`.
- **"Multi-actor counter-sign"** without at least 2 ECDSA/Ed25519 signatures in provenance.

Any such claim without the corresponding receipt is a **fake-green** incident. The Doctrinarium is the author of fake-green-detection doctrine; the Inquisition is the runtime enforcer.

---

## §10. Provenance & E3 test plan

This charter is covered by `ORGANS/DOCTRINARIUM/TESTS/test_doctr_charter_e3.py`. Coverage (at least 12 tests):

| T#  | Test                                                                  |
|-----|-----------------------------------------------------------------------|
| T01 | `DOCTRINARIUM/CHARTERS/DOCTRINARIUM.md` exists                        |
| T02 | `DOCTRINARIUM/CHARTERS/DOCTRINARIUM.en.md` exists                     |
| T03 | RU contains all sections §0–§11                                       |
| T04 | EN contains all sections §0–§11 (parallel structure)                  |
| T05 | RU header contains `DOCTR-CHARTER-0001`                               |
| T06 | RU header contains `version: 1.0.0`                                   |
| T07 | RU header contains `imperium.charter.v0_1`                            |
| T08 | RU header references real master sha (`d8027a8`)                     |
| T09 | RU §0 and EN §0 contain "NO_LLM_IN_PIPELINE"                         |
| T10 | EN file contains English markers ("Mission", "Authority")             |
| T11 | RU file contains ≥ 30% Cyrillic letters                               |
| T12 | RU and EN sizes are within reasonable bounds                          |

Invocation: `python3 _HARNESS/RUNNER/e3_runner.py --organ DOCTRINARIUM --select test_doctr_charter_e3.py`.

Provenance:

- **task_id:** DOCTR-CHARTER-0001
- **branch:** warp/DOCTR-CHARTER-0001
- **base:** d8027a81598f007a46cc85dcdf3cbc73b76b05b3
- **authored_by:** NOTION_OPUS (CHAT / Opus 4.5)
- **lineage:** after INQ-TOOLS-0001 land
- **evidence_level on land:** E3 (e3_runner replay)
- **throne_status:** OBSERVER (Emperor Seal not activated at echelon 1)

---

## §11. Future amendments

- **Amendments to this charter** — through `DOCTR-CHARTER-0002+` packs. Each amendment bumps version (1.0.0 → 1.1.0 for additions, 1.0.0 → 2.0.0 for breaking changes).
- **Amendments to Constitution / Passport** — NOT through charter, but through `DOCTR-EMPEROR-SEAL-0001` (pack 0002 of this echelon) and subsequently the `EMPEROR_SEAL_ACTIVATION` task.
- **Adding a 10th organ** — bumps `REQUIRED_9_ORGANS_V0_1.json` → `REQUIRED_10_ORGANS_V0_2.json` and requires Emperor Seal.
- **Activating SPECULUM** (currently DORMANT) — through an owner decision against `GOVERNANCE_INDEX.json:owner_decisions_required_for_final_canon[]` item "Confirm whether SPECULUM becomes a baseline organ or remains a candidate organ".

---

*End of DOCTRINARIUM Charter v1.0.0.*
