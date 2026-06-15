# Доктрина TRINITY_HYGIENE v0_1

Подчиняется Конституции §9 (cleanup = классификация + staging, НЕ удаление) и §12 (security).

## 1. Принцип
Гигиена НЕ удаляет. Она классифицирует и при явном разрешении владельца ПЕРЕМЕЩАЕТ
лишнее в quarantine-staging с restore-манифестом (откат).

## 2. Режимы
- dry-run (по умолчанию): только ledger, НОЛЬ перемещений.
- quarantine (--apply-quarantine --owner-approve): перемещает только stage_quarantine.

## 3. Категории
- clutter: регенерируемый мусор (__pycache__, *.pyc, *.tmp, *.bak, .DS_Store и т.д.).
- unknown: неизвестная зона → owner_review, БЛОКИРУЕТ автоматику.
- keep: известное хорошее / protected.

## 4. Гейты (Custodes)
- protected_prefixes (.git, _CORE_GOVERNANCE …) НИКОГДА не двигаются автоматически.
- любой unknown (blocked_unknown>0) → авто-quarantine запрещён, пока владелец не классифицирует.
- перемещение требует --owner-approve + restore-манифест.

## 5. Порядок работы
1. dry-run → читаешь ledger.
2. разбираешь unknown вручную (или расширяешь политику).
3. когда blocked_unknown=0 и ты одобрил — запуск quarantine.
4. проверяешь, коммитишь в H.
