# Acceptance Gates

## PASS_WITH_WARNINGS requires all

- Starting repo truth recorded.
- Ghost_Evolve V2 Entry ACK produced.
- All new canonical/internal files created by this task are English-only and UTF-8 without BOM.
- Officio language authority policy exists in Markdown and JSON or justified equivalent.
- Inquisition mojibake filter tool exists.
- Mojibake filter detects Cyrillic in canonical artifacts.
- Mojibake filter detects UTF-8 BOM.
- Mojibake filter detects replacement character by code point.
- Mojibake filter detects named mojibake signatures without embedding non-English glyph examples in taskpack files.
- Safe exclusions are implemented for PDF, binary files, and explicit localization folders.
- Astronomicon taskpack language gate exists or is wired to Inquisition filter.
- Fixture runner and fixture reports exist.
- Matrix Spine language and encoding matrices are created or updated.
- Current canonical scan report exists.
- Any existing violations are classified as CLEAN, WARN, BLOCK, LEGACY_TO_REMEDIATE, or ALLOWED_LOCALIZATION.
- Ghost_Evolve language and encoding learning backlog exists.
- Hard red-team verdict exists and can downgrade.
- Efficiency delta receipt exists.
- Commit and push are performed for admitted changes.
- Worktree is clean after push.
- Remote origin/master equals final HEAD.

## BLOCK

- New internal taskpack or canonical files contain Cyrillic without an explicit Officio-authorized runtime-output exception.
- New text files contain UTF-8 BOM.
- Mojibake filter is missing.
- Officio language authority is missing.
- Astronomicon language gate is missing and no justified alternate route exists.
- Fixture coverage is missing for Cyrillic, BOM, replacement character, and clean file cases.
- Existing violations are ignored instead of classified.
- Final report contains PENDING commit or push fields while claiming pass.
- No positive efficiency delta.
- Commit or push fails.
- Worktree remains dirty after finalization.

## Required caps

- `CAP_LANGUAGE_AUTHORITY_MISSING`
- `CAP_MOJIBAKE_FILTER_MISSING`
- `CAP_UTF8_BOM_NOT_DETECTED`
- `CAP_CANONICAL_ARTIFACT_CONTAINS_CYRILLIC`
- `CAP_NON_ENGLISH_TASKPACK_INTERNAL_TEXT`
- `CAP_OWNER_LANGUAGE_NOT_ROUTED_THROUGH_OFFICIO`
- `CAP_ASTRONOMICON_ADMISSION_LANGUAGE_GATE_MISSING`
- `CAP_REPLACEMENT_CHARACTER_NOT_DETECTED`
- `CAP_MOJIBAKE_SIGNATURE_NOT_DETECTED`
- `CAP_LOCALIZATION_EXCEPTION_UNCONTROLLED`
- `CAP_PENDING_COMMIT_PUSH_FIELDS_LEFT_OPEN`
- `CAP_NO_EFFICIENCY_DELTA`
