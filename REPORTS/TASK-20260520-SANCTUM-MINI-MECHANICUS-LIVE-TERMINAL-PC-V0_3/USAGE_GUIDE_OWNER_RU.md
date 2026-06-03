# USAGE_GUIDE_OWNER_RU

## Запуск

`powershell
cd E:\IMPERIUM
python IMPERIUM_NEW_GENERATION\SANCTUM_MINI\server.py --host 127.0.0.1 --port 8765
`

Открыть: http://127.0.0.1:8765/

## Как работать в V0.3

1. По умолчанию центр открыт во вкладке LIVE.
2. Слева нажимайте кнопки действий Mechanicus: результат идёт в LIVE-поток.
3. Внизу LIVE введите allowlisted-команду вручную:
   - status, 	ools, check, identity, where, help, aw, screenshot, clear
4. Для превью screenshot используйте вкладку EVIDENCE.
5. Пути/отчёты смотрите во вкладке REPORTS.
6. Raw payload смотрите во вкладке RAW JSON.
7. Историю выполненных/заблокированных действий смотрите во вкладке ACTION HISTORY.

## Безопасность

- Любая команда вне allowlist блокируется как BLOCKED_NOT_ALLOWLISTED.
- Произвольный shell из браузера/API не допускается.
