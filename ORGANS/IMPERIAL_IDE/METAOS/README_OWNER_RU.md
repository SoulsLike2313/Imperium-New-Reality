# IMPERIUM METAOS ORCHESTRATION — V0.1

Адаптивная, полиморфная, AI-script-first MetaOS-оркестрация.
Как получить от LLM самый точный и дешёвый ответ, снизить аппетит системы
и перенести постоянный труд в органы, а Сервитору оставить ровно задачу.

## Состав

```
IMPERIUM_METAOS_ORCHESTRATION_V0_1/
  ENGINE/
    metaos_orchestrator.py        # ПРИМЕР 1: routing + cascade + token budget + cache
    servitor_runtime.py           # ПРИМЕР 2: thin servitor + отбор контекста + летопись
    administratum_bundle_gate.py   # ПРИМЕР 3: bundle-report gate (HELD/RELEASED)
  DOCS/
    LLM_CHEAP_ACCURATE_PLAYBOOK_RU.md   # свод практик из интернета
    INTEGRATION_INTO_MECHANICUS_RU.md   # куда встраивать в Империум
  metaos_smoke.py                 # интегрированный прогон всего конвейера
  VALIDATION/validation_report.json
  README_OWNER_RU.md (этот файл)
```

## Быстрый старт

```bash
python3 metaos_smoke.py            # весь конвейер (ожидается SMOKE RESULT: PASS)
python3 ENGINE/metaos_orchestrator.py       # демо routing/cascade
python3 ENGINE/servitor_runtime.py          # демо servitor + летопись
python3 ENGINE/administratum_bundle_gate.py  # демо gate (HELD + RELEASED)
```

## Три примера — на что опираться роботу

1. **metaos_orchestrator.py** — ядро решает кодом (script-first): дешёвая модель первой, эскалация только при низкой уверенности; жёсткий бюджет токенов; кэш-префикс.
2. **servitor_runtime.py** — Сервитор видит только отобранный контекст, исполняет задачу, не плодит лишних рецептов, отчитывается органу, орган пишет летопись.
3. **administratum_bundle_gate.py** — Администратум собирает bundle; если форма неполна — НЕ ОТПУСКАЕТ Сервитора, возвращает missing_lines.

## Статус

- Проверено: py_compile всех 4 модулей, интегрированный smoke = PASS (exit 0).
- Ограничения: реальные LLM заменены детерминированными заглушками; tokenizer грубый.
- CANDIDATE_NOT_CANON — внедрять через WARP-сессию с одобрением владельца.
