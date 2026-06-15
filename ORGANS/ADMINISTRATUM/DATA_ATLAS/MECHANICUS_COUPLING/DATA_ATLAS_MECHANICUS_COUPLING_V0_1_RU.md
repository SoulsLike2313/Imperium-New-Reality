# Data Atlas / Mechanicus Coupling V0.1

## Purpose

Data Atlas must not only show files. It must show engineering meaning:

- which files are tools;
- which language they use;
- which organ owns them;
- whether they have a Mechanicus passport;
- whether they have validation recipes;
- whether they are registered actions;
- whether they are runtime/generated/source;
- whether they need cleanup, archive, or passport work.

## New Atlas concepts

```text
tool_entity
language_entity
validation_recipe
registered_action
tool_passport_coverage
unregistered_script
language_distribution
operational_power_gap
```

## Coupling rule

If Data Atlas finds an executable/script-like file and Mechanicus has no passport for it, Atlas should mark it as:

```text
cleanup_lane: passport_needed
owner_summary: executable or tool-like entity without Mechanicus passport
```

## Next implementation steps

1. Data Atlas scanner reads Mechanicus seed tool passports.
2. Data Atlas computes registered vs unregistered script coverage.
3. Web Sanctum Data Atlas adds cards:
   - Language Distribution
   - Tool Passport Coverage
   - Unregistered Scripts
   - Validation Coverage
4. Mechanicus room shows first operational power report.
