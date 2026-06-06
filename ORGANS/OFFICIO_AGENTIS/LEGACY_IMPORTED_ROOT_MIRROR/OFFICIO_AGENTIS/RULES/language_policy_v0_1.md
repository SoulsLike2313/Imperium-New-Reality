# Language Policy V0.1

## Owner-Facing Communication

- Progress comments: Russian preferred.
- Final owner summary: Russian required.

## Technical Surfaces

- JSON keys, code, paths, commands: English-safe.
- Encoding: UTF-8.
- No mojibake.

## Bilingual Foundation

Owner-facing application surfaces must be RU/EN ready from foundation.
For this task, contracts and TUI labels are English-safe with RU-capable comments.

## Violation Handling

- Missing Russian owner summary: `FAIL`.
- Minor mixed technical English in code/path context: `WARN`.
