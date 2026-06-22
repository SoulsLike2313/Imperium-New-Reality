# EMPEROR_SEAL_PLACEHOLDER

```yaml
task_id:        DOCTR-TOOLS-0001
law_id:         DOCTR.LAW.EMPEROR_SEAL_PLACEHOLDER.v1_0
version:        1.0.0
lineage:        master 59159278802dc37da1386ca7451eadd8b96f6f06
authored_by:    NOTION_OPUS (CHAT / Opus 4.5)
target_organ:   DOCTRINARIUM
schema_version: imperium.law.v0_1
echolon:        1
status:         PLACEHOLDER (alpha v0_1)
supersession:   DOCTR-EMPEROR-SEAL-0001 will replace this file with the
                operational EMPEROR_SEAL_CONTRACT.md
```

## §0 What this file is

This file is a deliberate stub. It declares the SHAPE of EMPEROR_SEAL so that
downstream tools (kernel_write_guard, doctrinarium_integrity_validator,
canon_admission boundary check) can be authored against a stable contract
before the full seal mechanism is implemented.

While this placeholder is in effect, `kernel_write_guard_v0_1.py` runs in
OBSERVER mode (see KERNEL_BOUNDARY_CONTRACT §5). It logs verdicts but does
NOT block. Kernel writes during alpha proceed under OWNER_MANUAL sovereign
bypass with the bypass recorded.

## §1 EMPEROR_SEAL_v0_1 contract (target shape)

A seal is a tuple of factors signed against a specific operation. The target
shape is:

```
SEAL_v0_1 = {
  "factor_a_ed25519":    "<ed25519 signature over operation digest>",
  "factor_b_passphrase": "<argon2id hash, salted with operation digest>",
  "factor_c_hwid_lock":  "<hwid hash bound to authorized hardware list>",
  "operation_digest":    "<sha256 of the operation manifest>",
  "ttl_seconds":         3600,
  "issued_at":           "<utc iso8601>",
  "expires_at":          "<utc iso8601>"
}
```

## §2 Threshold rules

- **Normal kernel write**: 2-of-3 factors required.
- **EMPEROR_SEAL rotation** (re-keying factor_a or replacing factor_c hardware
  list): 3-of-3 factors required.
- **OWNER_MANUAL bypass**: 0-of-3 factors required but bypass MUST be declared
  in the operation manifest BEFORE the operation runs. Post-hoc declaration
  is forbidden.

A seal with fewer factors than the threshold is INVALID even if every present
factor verifies.

## §3 TTL and one-shot

- Default TTL: 3600 seconds (60 minutes).
- Each seal is consumed by exactly one operation. Re-use of a seal for a
  second operation, even within TTL, is INVALID.
- A seal binds to the operation digest computed at seal-issuance time. If the
  operation manifest changes by even one byte, the seal no longer applies.

## §4 Ledger

Every seal verification (ALLOW or DENY, valid or invalid) MUST append a row
to:

```
ORGANS/_CORE_GOVERNANCE/EMPEROR_SEAL_LEDGER.jsonl
```

Ledger row schema (subject to DOCTR-EMPEROR-SEAL-0001 final spec):

```
{
  "schema_version":   "imperium.emperor_seal_ledger.v0_1",
  "ledger_seq":       <monotonic integer>,
  "operation_digest": "<sha256>",
  "verdict":          "ALLOW|DENY|INVALID",
  "factors_present":  ["factor_a", "factor_b"],
  "threshold":        "2_of_3",
  "verified_at":      "<utc iso8601>",
  "verifier":         "kernel_write_guard_v0_1"
}
```

The ledger is append-only. It MUST NEVER be edited in place. Rotations of
the ledger file (e.g. yearly archive) require an EMPEROR_SEAL rotation
operation.

## §5 Forbidden Claims until EMPEROR_SEAL operational

During v0_1 alpha, the following are FORBIDDEN:

- Asserting that a pack carries a valid EMPEROR_SEAL.
- Producing a synthetic seal that imitates the §1 shape.
- Claiming that OWNER_MANUAL bypass is the same as a seal.
- Skipping the OWNER_MANUAL bypass declaration on a kernel-touching pack.

## §6 Successor pack

`DOCTR-EMPEROR-SEAL-0001` will:

- Replace this placeholder with the operational EMPEROR_SEAL_CONTRACT.md.
- Add tools for seal issuance (`emperor_seal_issue_v0_1.py`) and verification
  (`emperor_seal_verify_v0_1.py`).
- Add the ledger schema as a kernel path.
- Switch `kernel_write_guard` from OBSERVER to ENFORCED.

Until then, this placeholder remains the source of truth for seal SHAPE.

## §7 Amendment

Amendment to this placeholder is permitted under OWNER_MANUAL bypass with
the bypass recorded in the pack receipt. After DOCTR-EMPEROR-SEAL-0001 land,
this file is removed and amendments target EMPEROR_SEAL_CONTRACT.md instead.

## §8 Provenance

```
law_id:        DOCTR.LAW.EMPEROR_SEAL_PLACEHOLDER.v1_0
base_sha:      59159278802dc37da1386ca7451eadd8b96f6f06
authored_at:   captured at pack build (see meta/PROVENANCE.json)
identity_sig:  see meta/PROVENANCE.json
```

*End of EMPEROR_SEAL_PLACEHOLDER v1.0.0.*
