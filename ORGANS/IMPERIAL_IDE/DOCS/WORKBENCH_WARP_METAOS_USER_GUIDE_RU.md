# Workbench, WARP и MetaOS: руководство владельца

## Imperial IDE shell

```powershell
& .\ORGANS\IMPERIAL_IDE\run_imperial_ide.ps1 --smoke
```

## Workbench

```powershell
& .\ORGANS\IMPERIAL_IDE\run_imperial_workbench.ps1 -Surface smoke
& .\ORGANS\IMPERIAL_IDE\run_imperial_workbench.ps1 -Surface tui
```

GUI запускается через `-Surface gui`, но остаётся Windows candidate до ручного
owner smoke. Live mode означает только чтение текущего repo/bridge. Без root
Workbench честно показывает `SAMPLE`.

## WARP

```powershell
& .\ORGANS\IMPERIAL_IDE\run_warp_zone.ps1 -Command smoke
& .\ORGANS\IMPERIAL_IDE\run_warp_zone.ps1 -Command status
```

WARP пишет только в ignored runtime. Release создаёт manifest, но не меняет
kernel.

## MetaOS

```powershell
& .\ORGANS\IMPERIAL_IDE\run_metaos_smoke.ps1
```

MetaOS работает на deterministic stub runners. Реальный LLM и реальный
Сервитор не включены.

## Shell-команды

Используйте `tasks`, `reports`, `receipts`, `tools`, `dry-run-tool`, а также
`workbench-*`, `warp-*` и `metaos-*`. Неизвестный tool блокируется Механикусом.
