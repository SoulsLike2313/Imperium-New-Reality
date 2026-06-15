# CLEAN_CONTEXT_CONTINUITY_ROLE_PACK_GUARD_V0_1

Status: `CANDIDATE_V0_1`
Owner organ: `INQUISITION`

## Guard goals

- Prevent fake continuity claims.
- Prevent stale role assumptions.
- Prevent private-data leakage in role-specific handoff packs.
- Ensure role packs do not mutate continuity truth.

## Required checks

1. Continuity truth fields are role-neutral and identical across targets.
2. Role-specific files only change review posture/response contract/first-read list.
3. Private-data exclusion receipt is present in continuity bundle.
4. Stale-context audit is present and referenced by handoff receipt.
5. Global caps are not silently hidden by role-specific narrative.

## Downgrade rule

If any required check is missing, enforce at least `WARN` and attach a cap in red-team verdict.

