# Первый запуск

Из корня `E:\IMPERIUM_NEW_GENERATION_NEW_REALITY`:

```powershell
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py station
python ORGANS/IMPERIAL_IDE/WORKBENCH/TUI/imperial_tui.py
```

Для GUI:

```powershell
python ORGANS/IMPERIAL_IDE/WORKBENCH/GUI/imperial_gui_workbench.py
```

Безопасная цепочка задачи:

```powershell
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py new-task "Название задачи"
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py build-taskpack "Название задачи"
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py validate-taskpack
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py register-taskpack "Название задачи"
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py launch-card "Название задачи"
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py handoff-card "Название задачи"
```

Команда `register-taskpack` без слова `live` всегда dry-run. Каноническая локальная регистрация выполняется только явной командой:

```powershell
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py register-taskpack live "Название задачи"
```

Она меняет Astronomicon registry и поэтому требует осознанного запуска владельцем.
