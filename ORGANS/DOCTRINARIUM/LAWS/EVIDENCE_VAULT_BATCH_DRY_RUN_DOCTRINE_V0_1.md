# Evidence Vault Batch Dry-run Doctrine v0.1

Batch cleanup must pass through these gates:

1. Classification lane.
2. Owner-gated batch preview.
3. Evidence Vault pack plan.
4. Dry-run execution rehearsal.
5. Owner-approved execution patch.
6. Sealed Vault receipt.
7. Separate source cleanup proposal.

Dry-run is not execution. It may compute hashes, check file existence and build visual proof, but it must not create a Vault pack, mutate source, or write into source-controlled paths.

Trinity Plus requirement: every dry-run must produce an owner-readable proof surface showing what was checked, what is ready, what is missing and what remains blocked by owner gate.
