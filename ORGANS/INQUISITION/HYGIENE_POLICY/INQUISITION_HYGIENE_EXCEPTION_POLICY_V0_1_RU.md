# Inquisition Hygiene Exception Policy V0.1

Статус: рабочая политика классификации.

Цель: не прятать грязь, а отличать настоящую грязь от системных зон, защищённых runtime registry и detector self-hits.

## Правила

1. `ORGANS/_CORE_GOVERNANCE` и `ORGANS/_POST_WORK_RING` считаются `SYSTEM_ZONE`, пока владелец не решит иначе.
2. `E:/IMPERIUM_LOCAL_HANDOFF/WARP_RUNS/_registry` не является TTL-мусором. Это protected runtime registry.
3. Inquisition scripts may contain mojibake markers as detector literals. Такие срабатывания должны становиться `ENCODING_MARKER_LITERAL_ALLOWED`, а не `ENCODING_MOJIBAKE`.
4. Source cleanup разрешён автоматически только для generated cache: `__pycache__`, `.pyc`, `.pyo`, `.pytest_cache`.
5. Архивы, screenshots/evidence в source, unknown folders и no passport не удаляются автоматически. Они идут в owner-reviewed lanes.
6. TTL-48 для local handoff выполняется через quarantine first, не через прямое удаление.

## Следующий смысл

Data Atlas должен показывать не просто risk, а refined lifecycle:
- system zone
- protected registry
- true mojibake
- detector literal
- source cache
- owner-review archive
- owner-review evidence
- Mechanicus passport backlog
