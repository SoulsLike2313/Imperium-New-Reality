# Evidence Vault Batch Receipt Verification Doctrine v0.1

A Vault pack is not considered operationally useful until it is verified and registered.

Required sequence:

1. Verify required sidecars.
2. Verify `EVIDENCE_PACK.zip` SHA256.
3. Open ZIP and verify payload hashes against `SHA256SUMS.txt`.
4. Verify manifest, machine receipt, file index and SQLite counts agree.
5. Emit Data Atlas registration artifact.
6. Keep source cleanup blocked until a separate owner-gated cleanup proposal.

This doctrine follows Trinity Plus: the owner must see a visual proof surface, not only machine JSON.
