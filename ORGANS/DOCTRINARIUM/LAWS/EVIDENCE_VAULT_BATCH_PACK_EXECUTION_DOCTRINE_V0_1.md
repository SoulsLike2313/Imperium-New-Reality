# Evidence Vault Batch Pack Execution Doctrine v0.1

## Law

Evidence Vault batch execution may copy and pack owner-approved candidates into the Evidence Vault, but it must not delete, move, or rewrite source files.

## Required sequence

1. Classification lane exists.
2. Batch preview exists.
3. Pack plan exists.
4. Dry-run proves source files exist and hashes can be computed.
5. Owner explicitly approves copy/pack with a token.
6. Execution writes Vault pack, manifest, index, receipt, SHA256 sums and Trinity Plus proof.
7. Source cleanup remains blocked until a separate owner-gated proposal.

## Trinity Plus proof

Every execution must provide owner-visible evidence:

- how many files were packed;
- how many bytes were packed;
- where the Vault pack lives;
- pack SHA256;
- confirmation that source deletion/move/rewrite did not occur;
- next recommended gate.
