# Первый запуск Workbench

Из корня репозитория выполните безопасный smoke:

```powershell
& .\ORGANS\IMPERIAL_IDE\run_imperial_workbench.ps1 -Surface smoke
```

Интерактивный TUI:

```powershell
& .\ORGANS\IMPERIAL_IDE\run_imperial_workbench.ps1 -Surface tui
```

Candidate GUI на Windows:

```powershell
& .\ORGANS\IMPERIAL_IDE\run_imperial_workbench.ps1 -Surface gui
```

Workbench обнаруживает текущий репозиторий через `IMPERIUM_ROOT` или поиск
корня. Если live bridge не найден, режим явно обозначается как `SAMPLE`.

Реальный запуск инструментов, постоянный supervisor и внешние команды в этой
задаче заблокированы. Капсулы показывают только dry-run модель состояния.
