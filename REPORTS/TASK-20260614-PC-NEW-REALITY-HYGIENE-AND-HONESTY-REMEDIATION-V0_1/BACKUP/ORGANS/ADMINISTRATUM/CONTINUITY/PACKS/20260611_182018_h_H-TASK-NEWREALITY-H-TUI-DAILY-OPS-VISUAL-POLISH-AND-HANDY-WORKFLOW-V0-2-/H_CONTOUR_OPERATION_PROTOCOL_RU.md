# H-CONTOUR OPERATION PROTOCOL RU

## Канон

- Main repo candidate: `E:/IMPERIUM_NEW_GENERATION_NEW_REALITY`
- H repo candidate: `E:/IMPERIUM_NEW_GENERATION_NEW_REALITY_H`
- H-зона — ручная изолированная зона варпа для patch ZIP, smoke, визуального poke и acceptance.
- Main/master — каноническая чистая зона. UI/UX polish туда не применяется напрямую.

## Правильная цепочка

```text
H patch ZIP -> APPLY_PATCH.ps1 in *_H -> smoke in H -> visual review in H -> owner acceptance
-> commit by IMPERIUM_H -> cherry-pick/merge to main -> smoke in main -> push -> next task
```

## Запреты для Logos Prime

- Не давать команды применения H-патча в main, если owner явно не приказал.
- Не считать `repo_root` из manifest рабочей зоной H-polish, если есть H-contour rule.
- Не восстанавливать скрытые рассуждения прошлого чата.
- Не включать real servitor execution, live LLM, unsafe shell, автокоммит или autopush.
- Не путать departments и organs: Freelance/Trading — departments; Mechanicus/etc — organs.
