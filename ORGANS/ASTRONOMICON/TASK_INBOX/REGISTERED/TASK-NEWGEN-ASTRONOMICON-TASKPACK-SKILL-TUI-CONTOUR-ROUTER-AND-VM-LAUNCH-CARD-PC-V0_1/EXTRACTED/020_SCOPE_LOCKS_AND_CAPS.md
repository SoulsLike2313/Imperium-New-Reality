# Scope Locks And Caps

## Allowed

- Build a minimal Astronomicon Taskpack Registration Skill.
- Implement a text TUI or menu-driven CLI under Astronomicon.
- Support PC contour registration.
- Support VM3 contour transfer, sync, intake, resolver and VM launch-card terminal if route is available.
- Support VM2 contour through route config and live path if route is available; otherwise produce a clear route-missing receipt.
- Add receipts, schemas, tests and validation.
- Add admission regression fixtures learned from recent manual attempts.
- Commit and push if all gates pass.

## Forbidden

- Full IDE visual release.
- WARP runtime.
- Browser automation runtime.
- AdsPower or other product API runtime actions.
- Freelance or trading readiness claims.
- Unsafe automatic merge-conflict resolution in registries.
- Silent stash/pop or overwrite behavior without receipts.
- Claiming VM2/VM3 live success if the route was only simulated.
- Moving truth source into IDE.

## Carried caps

- CAP_STAGE1_WITH_WARNINGS_ONLY.
- CAP_NO_IDE_VISUAL_RELEASE_YET.
- CAP_NO_WARP_RUNTIME.
- CAP_DIRTY_START_OWNER_APPROVED_CONTINUATION.

## Expected verdict ceiling

PASS_WITH_WARNINGS is acceptable. Clean PASS is not expected unless all carried caps are explicitly resolved by existing repo policy.
