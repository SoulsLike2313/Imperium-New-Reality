# DOCTRINARIUM Organ Contract V1.0

```yaml
organ_id:       DOCTRINARIUM
version:        1.0.0
lineage:        master 59159278802dc37da1386ca7451eadd8b96f6f06
status:         ACTIVE_CORE_ORGAN_V0_1
schema_version: imperium.organ_contract.v0_1
supersedes:     DOCTRINARIUM Organ Contract V0.1 (Phase O auto-stamp, 20260618-202356)
authored_by:    NOTION_OPUS (CHAT / Opus 4.5)
authored_at:    captured at pack build (see meta/PROVENANCE.json)
identity_sig:   see meta/PROVENANCE.json
```

## §0 NO_LLM_IN_PIPELINE

This contract is enforced by deterministic stdlib code paths
(`doctrinarium_integrity_validator_v0_1.py`, `kernel_write_guard_v0_1.py`)
and by the charters under `DOCTRINARIUM/CHARTERS/`. No LLM-only signature
produces or rescinds any duty in this contract.

## §1 Purpose

DOCTRINARIUM is the organ of LAW: it defines canon boundaries, the kernel
perimeter, the pipeline shape, and the forbidden claims that no actor may
utter. It produces no runtime artifacts; it defines what may be admitted as
runtime and what must be refused.

This contract supersedes the V0.1 Phase O auto-stamp (which existed as a
pre-charter skeleton). It is bound to `DOCTRINARIUM.md` v1.0 and the LAWS
landed in DOCTR-TOOLS-0001.

## §2 Allowed authority

- Author and own LAWS, doctrines, charters, and matrices under
  `DOCTRINARIUM/` and `ORGANS/DOCTRINARIUM/`.
- Define canon-admission boundaries (CANONICAL_PIPELINE stage 2 checks).
- Define kernel-boundary perimeter (KERNEL_BOUNDARY_CONTRACT).
- Maintain the ENTRY_PROTOCOL for LLM-actor sessions.
- Define the KPD doctrine (operationalization owned by STRATEGIUM).
- Own the integrity validator (`doctrinarium_integrity_validator_v0_1.py`)
  and co-own the kernel-write guard with _CORE_GOVERNANCE.

## §3 Forbidden claims

- DOCTRINARIUM MUST NOT claim runtime capability (no execution, no push, no
  database mutation).
- DOCTRINARIUM MUST NOT issue an EMPEROR_SEAL.
- DOCTRINARIUM MUST NOT bypass evidence levels (E1-E6).
- DOCTRINARIUM MUST NOT sign CANONICAL_PIPELINE stage 4 (WRITE) or stage 6
  (ARCHIVE).
- DOCTRINARIUM MUST NOT publish a charter or LAW that contradicts a higher
  governance layer (Constitution > Emperor passport > governance index).

## §4 Required receipts

DOCTRINARIUM operations produce or reference these receipts:

- `imperium.canon_admission.v0_1`        (stage 2 CHARTER)
- `imperium.kernel_write_guard.v0_1`     (stage 3 BOUNDARY)
- `imperium.doctrinarium_integrity.v0_1` (organ self-validation)
- `imperium.entry_attestation.v0_1`      (per-actor session)

A pack that targets DOCTRINARIUM MUST attach `doctrinarium_integrity.v0_1`
with `overall: PASS` or `overall: WARN` (FAIL refuses admission).

## §5 LAWS owned by this organ

v1.0.0 set (landed by DOCTR-TOOLS-0001):

1. `ORGANS/DOCTRINARIUM/LAWS/KERNEL_BOUNDARY_CONTRACT.md` (kernel paths,
   authorized actors, OBSERVER vs ENFORCED mode).
2. `ORGANS/DOCTRINARIUM/LAWS/CANONICAL_PIPELINE.md` (7-stage pipeline + 6
   canon-admission boundaries + receipt chain).
3. `ORGANS/DOCTRINARIUM/LAWS/ENTRY_PROTOCOL_FOR_LLM.md` (mandatory read list,
   attestation tool, role declaration constraints).
4. `ORGANS/DOCTRINARIUM/LAWS/EMPEROR_SEAL_PLACEHOLDER.md` (target shape of
   EMPEROR_SEAL_v0_1; superseded by DOCTR-EMPEROR-SEAL-0001).
5. `ORGANS/DOCTRINARIUM/LAWS/ROLE_REGISTRY.md` (canonical role list, binding
   mechanism, role-authority matrix v0_1 stub).

## §6 Tools and schemas

- Tool: `ORGANS/DOCTRINARIUM/TOOLS/doctrinarium_integrity_validator_v0_1.py`
- Schema: `ORGANS/DOCTRINARIUM/SCHEMAS/imperium.doctrinarium_integrity.v0_1.schema.json`
- Tool (co-owned with _CORE_GOVERNANCE):
  `ORGANS/_CORE_GOVERNANCE/TOOLS/kernel_write_guard_v0_1.py`
- Schema (co-owned):
  `ORGANS/_CORE_GOVERNANCE/SCHEMAS/imperium.kernel_write_guard.v0_1.schema.json`
- Tool (co-owned):
  `ORGANS/_CORE_GOVERNANCE/TOOLS/imperium_first_boot_v0_1.py`
- Schema (canon admission, co-owned):
  `ORGANS/_CORE_GOVERNANCE/SCHEMAS/imperium.canon_admission.v0_1.schema.json`

## §7 Relations to other organs

- INQUISITION runs `doctrinarium_integrity_validator_v0_1.py` as part of E3
  self-tests; FAIL blocks land. WARN does not block.
- MECHANICUS writes payload; before pushing warp, runs
  `kernel_write_guard_v0_1.py` over the file set; OBSERVER verdict is
  recorded in `meta/`.
- ADMINISTRATUM archives the receipts under append-only paths.
- STRATEGIUM operationalizes the KPD doctrine per `MATRICES/KPD_METRIC_SPEC.md`.
- OFFICIO_AGENTIS binds roles per `LAWS/ROLE_REGISTRY.md`.

## §8 Successor pack obligations

- `DOCTR-EMPEROR-SEAL-0001` replaces `EMPEROR_SEAL_PLACEHOLDER.md` with the
  operational seal contract and switches `kernel_write_guard` to ENFORCED.
- `OFFICIO-ROLES-0001` operationalizes `ROLE_REGISTRY.md`.
- `STRATEGIUM-KPD-0001` operationalizes `KPD_METRIC_SPEC.md`.
- `ADMIN-EYES-0001` / `ADMIN-MEMORY-0001` add the append-only archive for
  pipeline receipts.

## §9 Amendment

Amendments to LAWS at §5 follow KERNEL_BOUNDARY §4 receipts. Amendments to
this contract require CANONICAL_PIPELINE charter admission + a fresh
integrity receipt with `overall: PASS`.

## §10 Provenance

```
organ_id:      DOCTRINARIUM
contract_id:   imperium.organ_contract.DOCTRINARIUM.v1_0
landed_in:     DOCTR-TOOLS-0001
base_sha:      59159278802dc37da1386ca7451eadd8b96f6f06
authored_at:   captured at pack build (see meta/PROVENANCE.json)
identity_sig:  see meta/PROVENANCE.json
```

*End of DOCTRINARIUM Organ Contract V1.0.*
