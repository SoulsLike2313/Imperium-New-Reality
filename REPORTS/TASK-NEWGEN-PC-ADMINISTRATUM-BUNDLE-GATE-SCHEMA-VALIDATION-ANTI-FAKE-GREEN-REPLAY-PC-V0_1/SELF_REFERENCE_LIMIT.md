# Self Reference Limit

Task ID: `TASK-NEWGEN-PC-ADMINISTRATUM-BUNDLE-GATE-SCHEMA-VALIDATION-ANTI-FAKE-GREEN-REPLAY-PC-V0_1`

`task_report_bundle.zip`, final hash files, and final git/remote proof receipts
cannot all be both inside the bundle and also prove the exact final bundle
commit. Administratum V0.2 records these files in `adjacent_receipts_manifest.json`
and verifies the bundle gate before creating the zip.

Final `origin/master == HEAD` and clean-worktree proof must be live-checked after
the last push without rewriting this report folder.
