# ENTRY_PROTOCOL_FOR_LLM

```yaml
task_id:        DOCTR-TOOLS-0001
law_id:         DOCTR.LAW.ENTRY_PROTOCOL.v1_0
version:        1.0.0
lineage:        master 59159278802dc37da1386ca7451eadd8b96f6f06
authored_by:    NOTION_OPUS (CHAT / Opus 4.5)
target_organ:   DOCTRINARIUM
schema_version: imperium.law.v0_1
echolon:        1
status:         OBSERVER (alpha v0_1)
applies_to:     any LLM-based actor entering the Imperium repository
```

## §0 NO_LLM_IN_PIPELINE (reminder)

This protocol is itself a deterministic check. An LLM that completes the
protocol does NOT thereby gain pipeline authority; it gains only the right
to draft artifacts that other (tool-based) stages may consume.

## §1 Purpose

When a new LLM-actor (e.g. a fresh Claude / GPT / Grok session, or a new
NOTION_OPUS thread) is given write access to this repository, that actor
MUST execute the entry protocol BEFORE proposing any pack, edit, or claim.

The protocol exists to:

- Ground the actor in current canon (charters, LAWS, governance index).
- Produce an attestation that the actor read what it claims to have read.
- Establish the actor's role (LOGOS_PRIME, SERVITOR_PRIME, SPECULUM, etc.)
  before any work begins.

## §2 Mandatory read list (in this order)

```
1. ORGANS/_CORE_GOVERNANCE/CONSTITUTION/CONSTITUTION_OF_THE_IMPERIUM.md
2. ORGANS/_CORE_GOVERNANCE/EMPEROR/PASSPORT_OF_THE_EMPEROR.md
3. ORGANS/_CORE_GOVERNANCE/GOVERNANCE_INDEX.json
4. ORGANS/_CORE_GOVERNANCE/REQUIRED_9_ORGANS_V0_1.json
5. DOCTRINARIUM/CHARTERS/DOCTRINARIUM.md
6. ORGANS/DOCTRINARIUM/LAWS/KERNEL_BOUNDARY_CONTRACT.md
7. ORGANS/DOCTRINARIUM/LAWS/CANONICAL_PIPELINE.md
8. ORGANS/DOCTRINARIUM/LAWS/EMPEROR_SEAL_PLACEHOLDER.md
9. ORGANS/DOCTRINARIUM/LAWS/ROLE_REGISTRY.md
10. The charter of the organ the actor intends to operate within.
```

Reading order is significant. Constitution > Emperor > Governance Index >
Required Organs > Doctrinarium charter > LAWS > organ charter.

## §3 Mandatory attestation

After completing §2, the actor MUST emit an attestation receipt by invoking
`ORGANS/_CORE_GOVERNANCE/TOOLS/imperium_first_boot_v0_1.py` (or by hand-writing
an equivalent JSON document and submitting it for guard verification).

The attestation receipt shape:

```
{
  "schema_version": "imperium.entry_attestation.v0_1",
  "actor":          "<role_name>:<session_id>",
  "read_files":     [ <path>, ... ],
  "read_shas":      { "<path>": "<sha256>" },
  "snapshot_digest": "<sha256 of repo state at attestation time>",
  "declared_role":   "<LOGOS_PRIME|SERVITOR_PRIME|SPECULUM|...>",
  "declared_scope":  "<organ>|<task_id>|broad",
  "attested_at":     "<utc iso8601>",
  "acks": {
    "no_llm_in_pipeline":     true,
    "kernel_writes_need_seal": true,
    "forbidden_claims_known":  true
  }
}
```

The attestation is persisted at:

```
_HARNESS/_RUNS/<YYYYMMDDZ>/ENTRY_ACKS/<role>_<session_id>.json
```

Guard tools (kernel_write_guard, doctrinarium_integrity_validator) MAY refuse
to operate on behalf of an actor with no recent attestation.

## §4 Attestation freshness

- A fresh attestation MUST be produced at the start of each session.
- An attestation is stale if `attested_at` is older than 24 hours OR if any
  read_file sha256 has changed in the repo since attestation time.
- A stale attestation does NOT block ordinary reads, but DOES block pack
  authorship (stages 1, 4 of CANONICAL_PIPELINE).

## §5 Role declaration constraints

The actor MAY declare only roles that are present in ROLE_REGISTRY and that
the owner has authorized in the actor's `OFFICIO_AGENTIS/agent_registry.json`
entry. Unilateral self-promotion (e.g. an LLM declaring itself THRONE) is a
FORBIDDEN claim under DOCTRINARIUM.md §9.

During alpha v0_1, ROLE_REGISTRY and the agent_registry are partially stubbed;
the attestation tool warns rather than refuses for unknown declared roles.

## §6 What this protocol does NOT confer

- It does NOT grant kernel write authority.
- It does NOT grant push authority to master.
- It does NOT exempt the actor from CANONICAL_PIPELINE stages.
- It does NOT signify that the actor's outputs are correct, only that the
  actor has been grounded in current canon.

## §7 Forbidden claims

- "I read the charters in a prior session, so I do not need to re-attest."
- "My attestation receipt is implied by my chat reply."
- "I am LOGOS_PRIME because I am the same model that LOGOS_PRIME uses."
  (Role binding is by owner-authorized registry entry, not by model identity.)
- "The attestation tool can be skipped if I quote the read files verbatim."

## §8 Amendment

This protocol may be amended without an EMPEROR_SEAL because it does not
touch kernel paths defined in KERNEL_BOUNDARY_CONTRACT §2. Amendments DO
require a charter-admission receipt (CANONICAL_PIPELINE stage 2).

## §9 Provenance

```
law_id:        DOCTR.LAW.ENTRY_PROTOCOL.v1_0
base_sha:      59159278802dc37da1386ca7451eadd8b96f6f06
authored_at:   captured at pack build (see meta/PROVENANCE.json)
identity_sig:  see meta/PROVENANCE.json
```

*End of ENTRY_PROTOCOL_FOR_LLM v1.0.0.*
