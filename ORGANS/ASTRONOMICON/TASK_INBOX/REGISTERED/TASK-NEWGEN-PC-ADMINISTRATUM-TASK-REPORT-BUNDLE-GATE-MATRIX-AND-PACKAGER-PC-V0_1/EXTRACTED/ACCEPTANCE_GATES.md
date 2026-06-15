# Acceptance Gates

## Hard scope gates

- Active root must resolve to New Reality.
- All writes must stay inside `E:/IMPERIUM_NEW_GENERATION_NEW_REALITY`.
- Ancient Empire must not be mutated.
- No VM2 or VM3 sync.
- No external tool installation.
- No uncontrolled mass rewrite.

## Administratum bundle gate acceptance

PASS requires:

1. Administratum bundle gate contract exists.
2. Bundle composition matrix exists.
3. Python checker exists and runs.
4. Python packager exists and runs.
5. Required schemas exist.
6. Complete fixture returns `BUNDLE_COMPOSITION_PASS`.
7. Missing fixture returns `BUNDLE_COMPOSITION_BLOCK` and writes a missing-items request.
8. Packager refuses to create final bundle after BLOCK.
9. Packager creates final `task_report_bundle.zip` only after PASS.
10. A real recent report folder is checked or an explicit substitution receipt is written.
11. `administratum_bundle_composition_receipt.json` is written.
12. `bundle_file_inventory.json` is written.
13. `sha256sums.txt` exists and covers the bundle path at minimum.
14. Final response includes exact bundle path and SHA256.

## Git/remote closure gates

- Local commit created.
- Push to `origin/master` succeeds.
- `origin/master == HEAD` verified.
- Worktree clean after closure, except for unavoidable self-reference files explicitly recorded.

## Language gates

- Machine artifacts are English / UTF-8 / no BOM.
- Owner-facing final answer is Russian through Officio runtime authority.
- Do not place Russian text inside canonical machine bundle unless an explicit Officio localization exception is recorded.

## Allowed verdicts

- `PASS`
- `PASS_WITH_SELF_REFERENCE_LIMIT`
- `PASS_WITH_WARNINGS`
- `BLOCK`

Do not claim clean semantic admission. V0.1 checks bundle composition only.
