# USAGE_GUIDE_OWNER_RU

## Запуск

`powershell
cd E:\IMPERIUM
python IMPERIUM_NEW_GENERATION\SANCTUM_MINI\server.py --host 127.0.0.1 --port 8765
`

Открыть: http://127.0.0.1:8765/

## Проверка LIVE terminal

1. Убедитесь, что вкладка по умолчанию: LIVE.
2. Введите в центре команду status или 	ools.
3. Проверьте, что вывод появляется в центре LIVE (не в боковой панели).
4. Нажмите кнопку действия слева (Run visual-status и т.п.) и проверьте, что результат тоже идёт в LIVE-поток.
5. Введите git status — должен вернуться BLOCK (BLOCKED_NOT_ALLOWLISTED).
6. Перейдите во вкладку EVIDENCE для screenshot-preview.

## Безопасность

Разрешены только команды allowlist:
status, tools, check, identity, where, help, raw, screenshot, clear.
