# GHOST_EVOLVE Stage1 Learning Backlog

## L001 — ASTRONOMICON
- Source problem: Astronomicon resolver currently synthetic and not production transport-backed.
- Why it matters: Task-entry reliability for real intake is not yet guaranteed.
- Improvement: Build signed task inbox + resolver with provenance check.
- Blocks: `REAL_USE_PILOT`
- Script-first: `true`
- Next task: `TASK-NEWGEN-ASTRONOMICON-RESOLVER-HARDENING-V0_1`

## L002 — INQUISITION
- Source problem: Hard red-team output still depends on manual claim attack quality.
- Why it matters: Manual-only red-team can miss optimistic overclaims.
- Improvement: Add structured red-team checker enforcing mandatory attack list.
- Blocks: `STAGE2`
- Script-first: `true`
- Next task: `TASK-NEWGEN-INQUISITION-REDTEAM-CHECKER-V0_1`

## L003 — ADMINISTRATUM
- Source problem: Legacy receipt producers remain partially unmigrated.
- Why it matters: External finalization semantics can be inconsistent across old paths.
- Improvement: Run repo-wide producer migration with schema enforcement.
- Blocks: `STAGE2`
- Script-first: `true`
- Next task: `TASK-NEWGEN-LEGACY-RECEIPT-MIGRATION-STAGE2-V0_1`

## L004 — MECHANICUS
- Source problem: Task-entry checker is candidate and not canon-admitted.
- Why it matters: Stage1 proof exists but tool lifecycle is incomplete.
- Improvement: Promote checker via tool card + negative fixtures + Inquisition review.
- Blocks: `NONE`
- Script-first: `true`
- Next task: `TASK-NEWGEN-MECHANICUS-TASK-ENTRY-CHECKER-ADMISSION-V0_1`

## L005 — OFFICIO_AGENTIS
- Source problem: Owner-facing RU/EN lane is policy-backed but not globally auto-checked.
- Why it matters: Language drift can degrade owner trust and contract compliance.
- Improvement: Introduce final bundle language lane guard.
- Blocks: `NONE`
- Script-first: `true`
- Next task: `TASK-NEWGEN-OFFICIO-LANGUAGE-LANE-GUARD-V0_1`
