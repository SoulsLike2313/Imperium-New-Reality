# Acceptance Gates

## PASS_WITH_WARNINGS requires all

- Starting repo truth recorded.
- Ghost_Evolve V2 Entry ACK produced.
- Bootstrap preflight tool exists.
- Bootstrap repair/helper tool exists.
- Owner-facing launcher exists and does not select fixture runner as launcher.
- Preflight detects missing route template, missing start ACK template, UTF-8 BOM, invalid JSON, and route missing 8 organs.
- Repair writes UTF-8 no-BOM JSON templates.
- Fixture runner and fixture report exist.
- Astronomicon task entry launcher/TUI path is documented for Owner.
- Stage3 pending field scan exists.
- If PENDING fields remain, follow-up finalization receipt explains status without fake-green.
- Ghost_Evolve Stage3.1 learning backlog exists.
- Hard red-team verdict exists and can downgrade.
- Efficiency delta receipt exists.
- External finalization / commit-push receipts use current semantics.
- Worktree clean after push.
- Remote origin/master equals final HEAD.

## BLOCK

- Preflight tool missing.
- Repair tool missing.
- Owner launcher missing.
- UTF-8 BOM is not detected.
- Fixture runner missing or does not cover required cases.
- TUI/intake remains dependent on manual template creation.
- PENDING fields ignored.
- New feature/domain work starts.
- No positive efficiency delta.
- Commit/push fails.
- Worktree dirty after finalization.

## Required caps

- `CAP_ASTRONOMICON_BOOTSTRAP_PREFLIGHT_MISSING`
- `CAP_ASTRONOMICON_BOOTSTRAP_REPAIR_MISSING`
- `CAP_ASTRONOMICON_TEMPLATE_UTF8_BOM_NOT_DETECTED`
- `CAP_ASTRONOMICON_ROUTE_TEMPLATE_MISSING`
- `CAP_ASTRONOMICON_START_ACK_TEMPLATE_MISSING`
- `CAP_ASTRONOMICON_OWNER_LAUNCHER_MISSING`
- `CAP_ASTRONOMICON_LAUNCHER_CONFUSES_FIXTURE_RUNNER`
- `CAP_STAGE3_PENDING_FIELDS_IGNORED`
- `CAP_SECOND_MICROPILOT_STARTED_TOO_EARLY`
- `CAP_IDE_VISUAL_STARTED_TOO_EARLY`
- `CAP_WARP_CLAIMED_WITHOUT_UNLOCK`
- `CAP_NO_EFFICIENCY_DELTA`
