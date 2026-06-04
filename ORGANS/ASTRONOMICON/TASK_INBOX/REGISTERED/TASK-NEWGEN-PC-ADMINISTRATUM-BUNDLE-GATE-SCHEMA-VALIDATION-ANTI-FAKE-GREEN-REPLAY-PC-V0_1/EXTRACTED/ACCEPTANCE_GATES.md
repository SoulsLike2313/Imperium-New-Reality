# Acceptance Gates

## Gate 1 - New Reality scope

- Active root resolves to `E:/IMPERIUM_NEW_GENERATION_NEW_REALITY`.
- Ancient Empire is not mutated.
- Task is registered by New Reality native Astronomicon, not Ancient bridge.

## Gate 2 - Administratum V0.2 artifacts

Required artifacts exist under Administratum Bundle Gate area:

- V0.2 contract document.
- Schema matrix document.
- V0.2 checker script.
- V0.2 packager script.
- JSON schemas for required receipt classes.
- Positive and negative fixtures.
- README or usage document.

## Gate 3 - Composition plus schema validation

The checker must prove:

- Complete fixture passes.
- Incomplete fixture blocks.
- Malformed JSON blocks.
- Missing required fields block or warn according to matrix severity.
- Wrong task ID blocks.
- Wrong active root blocks.
- Missing adjacent manifest blocks when adjacent proof files are required.

## Gate 4 - Administratum authority boundary

Receipts and docs must explicitly state that Administratum V0.2 checks report bundle composition/schema only. It must not claim semantic truth, Custodes admission, or complete no-fake-green purity.

## Gate 5 - Replay on real reports

Replay V0.2 against at least latest 3 available real report folders. Produce a replay summary with PASS/WARN/BLOCK per folder and reasons.

## Gate 6 - Report bundle packager

The packager must create `task_report_bundle.zip` only after Administratum gate PASS for this task report folder. If gate fails, packager must produce a missing/invalid request instead of a final bundle.

## Gate 7 - Final proof closure

- Commit and push to `https://github.com/SoulsLike2313/Imperium-New-Reality.git`.
- Prove local HEAD equals `origin/master`.
- Prove worktree clean after push.
- Record final bundle path and SHA256.
- Record self-reference limitation honestly if adjacent receipts are needed.

## Gate 8 - Final response contract

Final response must use the 4-part format:

1. Step name.
2. Step verdict.
3. Commit links / commit identifiers with labels.
4. 3-4 short Owner comments in Russian.

The final response must include exact report bundle path and SHA256.
