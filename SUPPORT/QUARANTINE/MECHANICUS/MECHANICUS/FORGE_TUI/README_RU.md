# Mechanicus Forge Client V0.2

## Что изменилось после V0.1

V0.1 печатал Rich-снимок прямо в PowerShell. Он работал, но PowerShell прокручивался вверх/вниз.

V0.2 — это личный Textual-клиент Механикуса:

- работает внутри отдельного TUI-приложения;
- не печатает длинный отчёт в историю PowerShell;
- поддерживает фокус по зонам;
- показывает категории, capability registry, detail, receipts;
- добавляет панель `MECHANICUS_FOLDERS / FRESHNESS`;
- оставляет future action sockets под будущие кнопки;
- остаётся строго read-only.

## Запуск

Самый простой запуск двойным кликом:

`LAUNCH_MECHANICUS_FORGE_CLIENT_V0_2.cmd`

Или из PowerShell/cmd:

```powershell
Set-Location "E:\IMPERIUM\IMPERIUM_NEW_GENERATION\MECHANICUS\FORGE_TUI"
cmd /c .\LAUNCH_MECHANICUS_FORGE_CLIENT_V0_2.cmd
```

## Клавиши

- `q` — выход;
- `r` — reload;
- `c` — фокус на категории;
- `t` — фокус на таблицу;
- `f` — фокус на папки.

## Dependency

Нужны Python packages:

- `rich`
- `textual`

Установка не выполняется молча. Если dependency отсутствует, запусти явно:

```powershell
py -3 -m pip install --user rich textual
```

## Read-only guarantee

Клиент только читает:

- capability cards;
- receipts;
- approval queue;
- git state;
- folder freshness.

Он не меняет registry, receipts, evidence index, scope packs.
