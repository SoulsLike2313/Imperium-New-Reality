
# OWNER APPROVED TOOLS NORMALIZATION REPORT

## Task
- TASK-NEWGEN-MECHANICUS-OWNER-APPROVED-TOOLS-REGISTRY-NORMALIZATION-PC-V0_1

## Result Summary
- Normalized: 4/4 owner-approved IDs.
- Wave 001 coverage: 4/4 included.
- Install actions: none.

## Decisions
| owner_approved_id | canonical_capability_id | action_taken | note_ru |
|---|---|---|---|
| UTILITIES_7_ZIP | UTILITIES_7_ZIP | already_present | Канонический ID уже совпадал. |
| MARKDOWNLINT_CLI | MARKDOWNLINT_CLI | canonical_card_created | Создана canonical card под owner-approved CLI. |
| CHECK_JSONSCHEMA_CLI | CHECK_JSONSCHEMA_CLI | canonical_card_created | Создан CLI-specific canonical ID; legacy jsonschema cards сохранены как related. |
| YAMLLINT_CLI | YAMLLINT_CLI | canonical_card_created | Добавлена canonical card для lint-пайплайна YAML. |

## Related Existing Cards (for traceability)
- CODE_QUALITY_JSONSCHEMA
- CAP-TOOL-JSONSCHEMA

## Safety Statement
- No installs executed.
- No package manager commands executed.
- Normalization only.
