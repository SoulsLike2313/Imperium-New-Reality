# Skill Bundle Protocol Draft

## Purpose

Turn loose scripts/tools into inspected, receipt-backed IMPERIUM skills.

## Required files

```text
skill_manifest.json
input_schema.json
output_schema.json
side_effects.md
README.md
run.py or adapter.*
TESTS/
RECEIPTS/
```

## Rules

- No skill executes without a manifest.
- No skill writes outside allowed scope.
- No skill claims PASS without receipt.
- No skill is canon until verified.
- Tool descriptions cannot override policy.
