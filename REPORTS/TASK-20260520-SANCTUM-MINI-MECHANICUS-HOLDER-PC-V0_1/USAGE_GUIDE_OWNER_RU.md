# Руководство владельца (RU)

Задача: `TASK-20260520-SANCTUM-MINI-MECHANICUS-HOLDER-PC-V0_1`

## Запуск

```powershell
cd E:\IMPERIUM
python IMPERIUM_NEW_GENERATION\SANCTUM_MINI\server.py --host 127.0.0.1 --port 8765
```

Открыть в браузере:
- `http://127.0.0.1:8765/`

## Что есть в V0.1

- Верхняя шапка: статус сервера, API, HEAD, dirty/clean, активный орган.
- Левая панель: кнопки-действия владельца.
- Центр: 10 карточек органов + детальная панель выбранного органа.
- Правый блок истины: агрегаты connected/placeholder/locked, warnings/errors/blockers, пути к последним evidence.
- Нижний микро-лог: события сборки состояния.

## Важное ограничение V0.1

Кнопки в левой зоне не запускают команды ОС напрямую.
Они показывают/копируют команду или путь (safe display mode).

## API

- `/api/health`
- `/api/state`
- `/api/organs`
- `/api/mechanicus`
- `/api/mechanicus/screenshots`
- `/api/mechanicus/reports`
- `/api/actions`

## Язык интерфейса

- Переключатель RU/EN в шапке.
- Машинные артефакты/API-ключи оставлены на английском.
