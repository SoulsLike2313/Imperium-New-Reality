# СХЕМА ИНТЕГРАЦИИ MetaOS В ИМПЕРИУМ

## 1. Куда класть

```
ORGANS/IMPERIAL_IDE/
  METAOS/                      <- этот пакет
    ENGINE/
      metaos_orchestrator.py   (routing + cascade + token budget)
      servitor_runtime.py      (thin servitor + organ chronicle)
      administratum_bundle_gate.py (bundle-report gate)
    metaos_smoke.py
```

Ядро (`KERNEL/`) НЕ трогаем. MetaOS садится ПОВЕРХ ядра как слой IDE-оркестрации.

## 2. Как связать с существующими органами

| Компонент MetaOS | Куда встраивается |
|------------------|-------------------|
| `MetaOSOrchestrator` | Ядро/IDE: точка входа любой задачи (перед WARP-сессией) |
| `Organ` + `Servitor` | Каждый из 9 органов (ASTRONOMICON, MECHANICUS …) получает экземпляр `Organ` и общий `Servitor` |
| `Organ.chronicle` | Летопись дела — пишется в WARP/runtime/<id>/events.jsonl |
| `Administratum` | Орган ADMINISTRATUM: вызывается на стадии WARP GATE |

## 3. Поток работы (как органы/Сервитор/ядро работают в варпе)

```
[ты ставишь задачу]
      |
      v
MetaOSOrchestrator.route()      <- ядро решает кодом: какой tier, какой бюджет
      |
      v
Organ.select_context()          <- орган отбирает ТОЛЬКО нужный контекст
      |
      v
Servitor.execute()              <- исполняет ровно задачу (внутри WARP-сессии)
      |
      v
Organ.record(report)            <- летопись дела
      |
      v
Administratum.release_or_hold() <- BUNDLE; HELD если форма неполная
      |
   RELEASED -> продукт выходит из WARP (ядро чистое)
   HELD     -> Сервитор дозаполняет missing_lines и повторяет
```

## 4. Подключение реального LLM

В `metaos_orchestrator.py` и `servitor_runtime.py` есть точка `runner(system, user) -> {answer, confidence}`.
Замени заглушки на реальный вызов (с prompt-caching на системном префиксе):

```python
def my_runner(system, user):
    resp = client.messages.create(
        model="<твоя дешёвая модель>",
        system=[{"type":"text","text":system,
                 "cache_control":{"type":"ephemeral"}}],  # КЭШ
        messages=[{"role":"user","content":user}],
        max_tokens=512,
    )
    return {"answer": resp.content[0].text,
            "confidence": parse_confidence(resp)}
```

## 5. Границы и безопасность

- Ядро — read-only baseline для Сервитора. Прямой записи в KERNEL нет.
- Всё исполнение — в WARP-сессии; отходы остаются в WARP/runtime, не в ядре.
- Bundle-gate = анти-fake-green: нет доказательств → нет выпуска.
