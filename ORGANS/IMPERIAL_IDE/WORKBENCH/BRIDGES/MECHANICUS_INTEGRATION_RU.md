# Интеграция Workbench с Механикусом

Workbench использует активный read-only/dry-run bridge:

`ORGANS/IMPERIAL_IDE/BRIDGES/mechanicus_shell_bridge.py`

Тонкий клиент `mechanicus_workbench_bridge.py` импортирует этот bridge напрямую
и не формирует произвольные subprocess-команды. Он может читать tools,
capabilities и policy, а также получать dry-run receipt.

Границы:

- неизвестный tool возвращает `BLOCKED`;
- real execution всегда заблокирован;
- unsafe shell отсутствует;
- при отсутствии live root включается явно обозначенный `SAMPLE`;
- регистрация инструментов остаётся ответственностью Механикуса.
