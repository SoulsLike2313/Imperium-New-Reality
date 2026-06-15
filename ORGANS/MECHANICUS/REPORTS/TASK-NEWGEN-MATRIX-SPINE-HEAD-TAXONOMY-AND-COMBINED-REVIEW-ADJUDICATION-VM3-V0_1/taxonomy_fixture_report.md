# Taxonomy Fixture Report — TASK-NEWGEN-MATRIX-SPINE-HEAD-TAXONOMY-AND-COMBINED-REVIEW-ADJUDICATION-VM3-V0_1

Timestamp (UTC): 2026-05-30T17:25:32Z

## Summary
- Fixtures checked: 10
- Contains failure fixtures: true
- Contains pass fixtures: true
- Failure fixture detected by checker: true
- Pass fixture detected by checker: true
- All expected detections: true

## Results
- HTA01 missing artifact_bundle_head triggers cap: detected
  - caps_triggered: CAP_ARTIFACT_BUNDLE_HEAD_MISSING
  - warnings: combined review merged verdict is still PENDING
  - expected_caps: CAP_ARTIFACT_BUNDLE_HEAD_MISSING
  - notes: artifact_bundle_head is empty
- HTA02 declared target unfetchable triggers cap: detected
  - caps_triggered: CAP_DECLARED_TARGET_UNFETCHABLE
  - warnings: combined review merged verdict is still PENDING
  - expected_caps: CAP_DECLARED_TARGET_UNFETCHABLE
  - notes: declared target head is not in fetchable_heads set
- HTA03 hash typo mismatch triggers cap: detected
  - caps_triggered: CAP_REVIEW_TARGET_TYPO_OR_HASH_MISMATCH, CAP_DECLARED_TARGET_UNFETCHABLE
  - warnings: combined review merged verdict is still PENDING
  - expected_caps: CAP_REVIEW_TARGET_TYPO_OR_HASH_MISMATCH
  - notes: head taxonomy review_target_head is not a full 40-char hash | review_target_manifest.review_target_head is not a full 40-char hash | declared_target_head is not a full 40-char hash | declared target head is not in fetchable_heads set | combined review receipt review_target_head is not a full 40-char hash
- HTA04 reviewers used different taxonomy paths: detected
  - caps_triggered: CAP_REVIEWERS_USED_DIFFERENT_HEAD_TAXONOMY
  - warnings: combined review merged verdict is still PENDING
  - expected_caps: CAP_REVIEWERS_USED_DIFFERENT_HEAD_TAXONOMY
  - notes: inquisitor and speculum taxonomy paths diverge
- HTA05 head taxonomy manifest missing: detected
  - caps_triggered: CAP_HEAD_TAXONOMY_MANIFEST_MISSING
  - warnings: combined review merged verdict is still PENDING
  - expected_caps: CAP_HEAD_TAXONOMY_MANIFEST_MISSING
  - notes: head_taxonomy_manifest is missing or not an object
- HTA06 combined adjudication receipt missing: detected
  - caps_triggered: CAP_COMBINED_REVIEW_ADJUDICATION_MISSING
  - warnings: none
  - expected_caps: CAP_COMBINED_REVIEW_ADJUDICATION_MISSING
  - notes: combined_review_adjudication_receipt is missing or not an object
- HTA07 review_target_head must stay single: detected
  - caps_triggered: CAP_REVIEW_TARGET_NOT_SINGLE, CAP_REVIEW_TARGET_TYPO_OR_HASH_MISMATCH, CAP_DECLARED_TARGET_UNFETCHABLE
  - warnings: combined review merged verdict is still PENDING
  - expected_caps: CAP_REVIEW_TARGET_NOT_SINGLE
  - notes: head taxonomy review_target_head is missing or non-single | review_target_manifest.review_target_head is missing or non-single | declared_target_head is not a full 40-char hash | declared target head is not in fetchable_heads set | combined review receipt review_target_head is missing or non-single
- HTA08 warp claim remains locked: detected
  - caps_triggered: CAP_WARP_CLAIMED_WITHOUT_UNLOCK
  - warnings: combined review merged verdict is still PENDING
  - expected_caps: CAP_WARP_CLAIMED_WITHOUT_UNLOCK
  - notes: warp runtime is claimed while warp is locked
- HTA09 single valid taxonomy passes: detected
  - caps_triggered: none
  - warnings: combined review merged verdict is still PENDING
  - expected_caps: none
- HTA10 fallback review head allowed only with warning: detected
  - caps_triggered: none
  - warnings: combined review merged verdict is still PENDING
  - expected_caps: none
