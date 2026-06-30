# Evidence requirements — TASK-NEWGEN-COMMIT-36DF325-CLEANUP-HARDENING-PC-V0_1

The final bundle/report must include:

1. Starting HEAD and ending HEAD.
2. Starting and ending `git status --short`.
3. List of documents read first.
4. Classification manifest with file paths and decisions.
5. List of deleted runtime junk paths.
6. List of quarantined generated paths.
7. List of kept source/backend seed paths.
8. Remaining warnings with exact reasons.
9. Checks run and results.
10. Commit hash and push result.

## Required machine-readable files

- `cleanup_classification_manifest.json`
- `tracked_artifact_hygiene_report.json`
- `closure_receipt.json`

## Required human-readable file

- `FINAL_REPORT.md`

## Owner comment language

Owner-facing summary in final chat must be Russian.
Repo machine-readable files should be English / UTF-8-safe.
