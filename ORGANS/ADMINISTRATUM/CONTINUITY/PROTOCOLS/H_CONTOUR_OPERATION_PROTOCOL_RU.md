# H-CONTOUR OPERATION PROTOCOL RU

## Hard rule

`E:/IMPERIUM_NEW_GENERATION_NEW_REALITY_H` — ручная H-зона варпа: patch ZIP, smoke, визуальный poke, acceptance.

`E:/IMPERIUM_NEW_GENERATION_NEW_REALITY` — main/canonical repo: только принятие уже проверенного H-коммита, smoke в main и push.

## Chain

```text
H patch ZIP -> APPLY_PATCH.ps1 in H -> H smoke -> H visual -> owner acceptance
-> IMPERIUM_H commit -> cherry-pick/merge to main -> main smoke -> push -> next task
```

## Logos Prime obligations

- Сначала проверить `git worktree list`, H path, branch, HEAD, `origin/master`.
- Не давать команды применения H-патча в main.
- Если continuity pack неполный, сначала чинить continuity, а не начинать следующий task.
- Не вытягивать скрытые рассуждения прошлого чата; работать только по owner-visible artifacts.
- Не включать live LLM, unsafe shell, real servitor execution, live trading/order placement.
