# Next Task Improvement Report

1. SSH matrix ownership: keep primary ownership in Mechanicus; later mirror to Administratum address book as read-only sync.
2. First alias promotions: `imperium-vm2`, `imperium-vm3`, `imperium-throne-core` with explicit offline warnings.
3. Unsafe action types without rollback: `ORGAN_DIALOGUE_PACKET_WRITE`, `SCOPE_MERGE_MUTATION`, and any `DANGEROUS_ACTION` without owner contract.
4. Minimal next negative/mutation test: attempt blocked dangerous action without owner contract and assert `DANGEROUS_ACTION_BLOCKED` receipt.
5. Strategic PDF value: useful as compass (Truth->Rollback->Negative-test chain), low noise in this bounded scope.
6. Context fit: yes, remained within <=256k with scoped reading.
