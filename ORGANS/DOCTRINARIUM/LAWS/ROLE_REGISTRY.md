# ROLE_REGISTRY

```yaml
task_id:        DOCTR-TOOLS-0001
law_id:         DOCTR.LAW.ROLE_REGISTRY.v1_0
version:        1.0.0
lineage:        master 59159278802dc37da1386ca7451eadd8b96f6f06
authored_by:    NOTION_OPUS (CHAT / Opus 4.5)
target_organ:   DOCTRINARIUM
schema_version: imperium.law.v0_1
echolon:        1
status:         OBSERVER (alpha v0_1)
supersession:   OFFICIO-ROLES-0001 will turn this registry into an
                operational schema with per-role permissions matrix.
```

## §0 Purpose

ROLE_REGISTRY enumerates the actor roles recognized inside Imperium, their
pipeline authority, and their declared status. It is the index that
ENTRY_PROTOCOL_FOR_LLM §5 consults when validating a `declared_role`.

## §1 Canonical role list (v0_1)

| Role            | Status   | Pipeline authority                                | Notes                                              |
|-----------------|----------|---------------------------------------------------|----------------------------------------------------|
| OWNER_MANUAL    | ACTIVE   | Sovereign on all stages; sovereign bypass.        | One natural person. Identity in EMPEROR passport.  |
| THRONE          | ACTIVE   | Stage 2 gate when EMPEROR_SEAL_v0_1 valid.        | Activated by DOCTR-EMPEROR-SEAL-0001.              |
| LOGOS_PRIME     | ACTIVE   | Stages 1, 4, 5, 7 author + signer.                | Currently bound to NOTION_OPUS chat actor.         |
| SPECULUM        | DORMANT  | Stage 6 audit; cross-pack contradiction scanning. | Activated by SPECULUM organ tools pack.            |
| SERVITOR_PRIME  | ACTIVE   | Stage 4 executor (CODEX / GROK). No stage signing.| Owner-mediated execution of plans from LOGOS_PRIME.|
| ROGUE_TRADER    | PLANNED  | Stage 1 intake from external sources.             | Activated by ROGUE_TRADER pack.                    |
| FREE_ARCHITECT  | PLANNED  | Stage 4 author for non-canonical exploration.     | Sandboxed scope; cannot push to master.            |

DORMANT = role recognized but no actor bound. PLANNED = role not yet
recognized in canon (schema slot reserved). ACTIVE = role recognized and at
least one actor bound.

## §2 Binding mechanism

An actor is BOUND to a role when:

1. ROLE_REGISTRY contains the role in §1.
2. `OFFICIO_AGENTIS/agent_registry.json` contains an entry mapping the actor
   identifier to the role.
3. The agent_registry entry was authored by OWNER_MANUAL (signature verified
   by OFFICIO-ROLES-0001 tools when that pack lands; under v0_1, trust the
   git commit author).

During alpha v0_1 the agent_registry is partially stubbed. Binding is
verified by `doctrinarium_integrity_validator` in advisory mode.

## §3 Role authority matrix (v0_1 stub)

```
                      INTAKE  CHARTER  BOUNDARY  WRITE  VERIFY  ARCHIVE  RECEIPT
OWNER_MANUAL            S       S        S        S       S       S        S
THRONE                  -       G        -        -       -       -        -
LOGOS_PRIME             A       -        -        A       A       -        A
SPECULUM                -       -        -        -       AUD     AUD      -
SERVITOR_PRIME          -       -        -        X       -       -        -
ROGUE_TRADER            A       -        -        -       -       -        -
FREE_ARCHITECT          -       -        -        A       -       -        -
```

Legend: S=sovereign sign, G=gate, A=author+sign, X=execute (no sign),
AUD=audit (no sign), -=no authority.

This matrix is operationalized by OFFICIO-ROLES-0001; in v0_1 it is
documentation only.

## §4 Identity boundaries (forbidden patterns)

The following bindings are FORBIDDEN:

- An LLM-only actor BOUND to THRONE. THRONE binding requires factor_c hwid
  lock on owner-controlled hardware (see EMPEROR_SEAL_PLACEHOLDER §1).
- An LLM-only actor BOUND to OWNER_MANUAL. OWNER_MANUAL is one natural
  person and never an LLM.
- The same actor BOUND to both LOGOS_PRIME and SPECULUM in the same
  attestation window. Drafting and auditing are separated roles.
- An actor BOUND to a role with status PLANNED. The role must be ACTIVE.

## §5 Promotion / demotion

A role change for an actor requires:

- A pack signed by OWNER_MANUAL with `target_organ: OFFICIO_AGENTIS`.
- The pack updates `OFFICIO_AGENTIS/agent_registry.json` atomically.
- The pack carries a CANONICAL_PIPELINE receipt chain.

Self-promotion by an LLM actor (declaring a different role in a fresh
attestation than was previously bound) triggers an integrity warning and
a DOCTRINARIUM admonition.

## §6 Successor pack obligations

`OFFICIO-ROLES-0001` will:

- Turn §3 matrix into a JSON schema enforced by tools.
- Add `agent_registry.json` schema and validator.
- Add binding-attestation receipts to CANONICAL_PIPELINE stage 1.

Until then, ROLE_REGISTRY is documentation that informs ENTRY_PROTOCOL §5
advisory checks.

## §7 Forbidden claims

- "I act as LOGOS_PRIME because the prior session did."
  (Role binding persists in agent_registry, not in session memory.)
- "OWNER_MANUAL authorized this role change in chat."
  (Authorization is by signed pack landing, not by chat.)
- "This role is implied by my charter knowledge."
  (Roles are explicit registry entries.)

## §8 Amendment

Amendment to §1 or §3 requires CANONICAL_PIPELINE charter-admission +
OFFICIO_AGENTIS countersign (when active). Amendment to §2 binding mechanism
requires the same. Until OFFICIO-ROLES-0001 lands, OWNER_MANUAL bypass is
the effective amendment authority.

## §9 Provenance

```
law_id:        DOCTR.LAW.ROLE_REGISTRY.v1_0
base_sha:      59159278802dc37da1386ca7451eadd8b96f6f06
authored_at:   captured at pack build (see meta/PROVENANCE.json)
identity_sig:  see meta/PROVENANCE.json
```

*End of ROLE_REGISTRY v1.0.0.*
