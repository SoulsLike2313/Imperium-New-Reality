# Acceptance Gates for TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1

## Hard gates
1. OFFICIO role entry is performed before mutation; owner-facing final output is Russian.
2. Worktree state is recorded before mutation.
3. Root physical cleanup is attempted by policy, not merely documented.
4. No destructive deletion is performed.
5. Moves use git mv where possible.
6. Active core root allowlist checker exists and is run.
7. Final active root state is reported with exact remaining top-level entries.
8. ORGANS contains the 9 canonical organ homes.
9. SUPPORT exists with COMMON_IMPERIUM_SUPPORT and QUESTIONABLE_OR_QUARANTINE.
10. Obvious legacy/prototype/failed surfaces are moved out of active root or held with explicit reason.
11. Duplicate top-level organ mirrors are moved/merged/quarantined or held with explicit reason.
12. QUARANTINE_INDEX is updated for every quarantined or learning archive item.
13. Active use of quarantine is checked and must have zero violations or BLOCK.
14. Administratum address book is updated.
15. Mechanicus tool card is created/updated for migration/checker tools.
16. Strategium cost and impurity metrics are recorded.
17. Schola captures lessons from legacy pain and migration risk.
18. Custodes audits organ guarding quality.
19. Post-work bundle checker passes.
20. Commit and normal non-force push are performed if changes are accepted.

## Pass conditions
PASS is allowed only if:
- all validators run;
- quarantine active-use violations are zero;
- root impurity is either zero or every remaining impurity has HOLD_WITH_REASON;
- bundle schema passes;
- git status is clean after commit/push;
- local HEAD equals origin/master after push.

## Warning conditions
PASS_WITH_WARNINGS is allowed if:
- some items remain due to safety holds;
- root still has technical exceptions with recorded reason;
- full migration is not complete but migration queue and hold receipts are complete.

## Block conditions
BLOCK if:
- active runtime uses quarantine;
- any destructive deletion occurs;
- untracked root clutter is created without classification;
- organ homes are missing;
- bundle is incomplete;
- remote proof is missing without explicit post-push boundary note;
- Servitor claims full clean without checker proof.
