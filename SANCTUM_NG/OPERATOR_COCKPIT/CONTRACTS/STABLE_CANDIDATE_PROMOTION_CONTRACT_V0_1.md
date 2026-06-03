# STABLE CANDIDATE PROMOTION CONTRACT V0.1

## Scope

This contract governs promotion from `candidate` cockpit track to `stable` cockpit track for:

- `IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.*` (stable)
- `IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_candidate.*` (candidate)

Claim boundary: UI/operator-shell promotion only. No production orchestration or autonomy claim.

## Promotion Preconditions

Promotion is allowed only if all conditions are true:

1. `operator_cockpit_sc_validator_report.json` verdict is `PASS` or explicit `WARN` with documented non-blocking reasons.
2. `operator_cockpit_sc_smoke_report.json` produces both stable and candidate screenshots.
3. `stable_candidate_comparison.json` confirms:
   - mandatory cockpit zones are still present;
   - required truth fields remain visible;
   - no fake-green evidence gaps.
4. Worktree is clean before promotion and after promotion checks.
5. Research dossier and evidence links are present in final report.
6. Owner-facing review comment exists in final report package.

## Mandatory Promotion Evidence

Required artifacts:

- `screenshot_matrix.json`
- `stable_candidate_comparison.json`
- `operator_cockpit_sc_validator_report.json`
- `operator_cockpit_sc_smoke_report.json`
- `FINAL_REPORT.md`
- `closure_receipt.json`

## Promotion Steps

1. Rebuild cockpit state with current task ID.
2. Run stable/candidate smoke and validator.
3. Review screenshot comparison and anti-acceptance gates.
4. If all gates pass, either:
   - copy candidate assets into stable entry files, or
   - keep stable entry fixed and update stable link target explicitly.
5. Re-run smoke for stable URL after promotion action.
6. Record promotion decision and resulting HEAD in report package.

## Rollback Rule

Rollback is mandatory when any blocking gate appears after promotion.

Rollback method:

- restore previous stable files from git history;
- rerun stable smoke;
- produce rollback note in report bundle.

## Never Claim

Do not claim:

- production autonomy;
- live multi-contour orchestration;
- backend capability that is not supported by receipts.
