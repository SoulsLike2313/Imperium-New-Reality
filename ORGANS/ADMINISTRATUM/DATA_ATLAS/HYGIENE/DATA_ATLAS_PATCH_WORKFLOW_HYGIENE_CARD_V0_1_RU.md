# Data Atlas — Patch Workflow Hygiene Card v0.1

## Что показывает карта

Эта карта делает видимой проблему, которую раньше можно было заметить только глазами в `git show`: локальные backup/handoff/smoke зоны могут случайно попасть в source commit.

## Owner-facing вопрос

> Этот patch commit содержит только source/policy/index/gate изменения, или он протащил операторский мусор?

## Health fields

- `forbidden_tracked_files_total`
- `missing_gitignore_patterns_total`
- `staged_backup_deletions_total`
- `blocking_gate`

## PASS condition

- `.imperium_patch_backups/` не tracked;
- `_LOCAL_HANDOFF/` не tracked;
- smoke vaults не tracked;
- `.gitignore` содержит managed local-only block;
- H commit не содержит backup payload как source.

## Next architecture implication

Перед `Imperium Intelligence Pack Builder` нужно требовать такую же hygiene proof: lightweight handoff pack должен доказывать, что он не является crude repo dump и не включает local-only мусор.
