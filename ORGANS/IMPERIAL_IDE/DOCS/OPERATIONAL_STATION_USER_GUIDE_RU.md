# Operational Station: руководство владельца

Все команды выполняются из `E:\IMPERIUM_NEW_GENERATION_NEW_REALITY`.

## Открытие поверхностей

```powershell
python ORGANS/IMPERIAL_IDE/WORKBENCH/TUI/imperial_tui.py
python ORGANS/IMPERIAL_IDE/WORKBENCH/GUI/imperial_gui_workbench.py
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py station
```

GUI запускается как Windows-приложение и требует ручного визуального подтверждения. Его кнопки вызывают только фиксированные shell-команды; произвольный shell отсутствует.

## Задача и taskpack

```powershell
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py new-task "Моя задача"
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py task-console "Моя задача"
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py build-taskpack "Моя задача"
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py validate-taskpack
```

Результат создаётся в ignored-каталоге `ORGANS/IMPERIAL_IDE/STATION/generated_taskpacks/`. В нём должны быть шесть корневых файлов Astronomicon, SHA256 и пройденный language gate.

## Регистрация и launch card

Проверка без изменения registry:

```powershell
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py register-taskpack "Моя задача"
```

Явная локальная PC-регистрация с изменением Astronomicon registry:

```powershell
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py register-taskpack live "Моя задача"
```

Station принимает live-регистрацию только для созданного ею и повторно валидированного taskpack. Remote contour не поддерживается.

```powershell
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py launch-card "Моя задача"
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py handoff-card "Моя задача"
```

Поле `handoff_text` из JSON является copy-ready сообщением для Servitor Prime. Handoff не означает, что задача исполнена.

## Наблюдение

```powershell
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py agents
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py agent-status IMPERIAL_IDE
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py lifecycle "Моя задача"
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py reports-latest
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py receipts-latest
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py safety
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py git-closure
```

`BLOCKED` всегда сопровождается причиной. Старые unrelated unstaged-файлы показываются предупреждением и не считаются автоматически частью текущей задачи.
