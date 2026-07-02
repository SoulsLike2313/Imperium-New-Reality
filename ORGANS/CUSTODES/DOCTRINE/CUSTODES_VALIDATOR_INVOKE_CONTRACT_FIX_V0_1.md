# CUSTODES VALIDATOR INVOKE CONTRACT FIX V0.1

patch_id: `CUSTODES-ASTRONOMICON-VALIDATION-INVOKE-CONTRACT-FIX-0001`

## Prosecutor law

Custodes is a prosecutor, not a green rubber stamp.

But a prosecutor must not fabricate an indictment from a wrong calling convention.

If a validator exits with code `2`, Custodes must treat this as possible invocation-contract mismatch and try the validator's declared compatible attempts.

Only after all compatible attempts fail may Custodes indict the validator.

## Why this patch exists

`validate_patch_pack_lifecycle_validation_foundation.py` failed under Custodes with exit code `2`.

That is most likely an argparse/invocation contract problem, not automatically proof that Astronomicon is lying.

## Boundary

Custodes validation is not Throne verdict.
