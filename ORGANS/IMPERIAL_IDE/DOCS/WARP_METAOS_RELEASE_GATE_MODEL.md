# WARP and MetaOS Release Gate Model

WARP isolates artifacts and records evidence. MetaOS may prepare candidate
chronicles and structured bundle fields. Administratum evaluates the bundle.

- `HELD`: mandatory fields are missing or evidence is below `E3`.
- `RELEASED`: the bundle is complete and may produce a release manifest.
- `RELEASED` never applies the manifest to the kernel.
- Kernel promotion requires a separate future owner-approved implementation.

The adapter records evidence level, missing fields, release scope, and the
fact that `automatic_kernel_promotion` is false.
