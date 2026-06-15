# Stage Checkpoint Examples V0.1

## Example status flow

1. Stage `S1_DESIGN` creates schemas and control docs.
2. Stage `S2_BUILDERS` creates CLI scripts and skeleton checkpoint JSON.
3. Stage `S3_VALIDATE` runs py_compile/help/smoke validation.
4. Stage `S4_REPORT` writes reports and receipts.

If S3 fails validation:
- checkpoint_status becomes NEEDS_FIX or BLOCKED;
- owner decision should be REQUEST_FIX or STOP.

If all checks pass:
- checkpoint_status can be READY_FOR_REVIEW;
- owner decision may be ACCEPT or CONTINUE_WITH_NOTES.
