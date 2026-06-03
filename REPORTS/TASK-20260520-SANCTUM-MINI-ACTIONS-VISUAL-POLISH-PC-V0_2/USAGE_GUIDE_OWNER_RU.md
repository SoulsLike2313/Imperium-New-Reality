# SANCTUM MINI V0.2 - Инструкция владельцу (RU)

## Как запустить

1. cd E:\IMPERIUM
2. python IMPERIUM_NEW_GENERATION\SANCTUM_MINI\server.py --host 127.0.0.1 --port 8765
3. Открыть http://127.0.0.1:8765/

## Что изменено

- В центре теперь приоритетно показывается visual viewport активного органа.
- Для MECHANICUS_AGENT используется последний self-captured screenshot через /api/mechanicus/screenshot/latest.
- Сырые данные, пути и отчётные детали вынесены во вторичные вкладки (Overview/Paths/Receipts/Raw JSON).
- Левая панель действий теперь рабочая через allowlisted API actions.

## Как проверить быстро

1. Нажмите Механикус visual-status.
2. Нажмите Запустить visual-check.
3. В центре должен остаться визуальный viewport, а не сырой текстовый дамп.
4. Переключайте вкладки внизу центральной панели для путей/квитанций/raw.

## Важно

- Произвольные команды из UI/API не выполняются.
- Если у вас нет свежего скриншота, центральная зона покажет честный fallback-текст и предложит обновить screenshot action.
