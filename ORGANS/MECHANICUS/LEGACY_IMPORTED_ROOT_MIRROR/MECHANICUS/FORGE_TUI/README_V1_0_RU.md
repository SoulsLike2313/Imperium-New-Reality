# Mechanicus Forge Client V1.0 — No Fake Heraldry

## Причина

Попытки нарисовать настоящие гербы в чистом terminal TUI выглядят плохо.

V1.0 удаляет фейковые pseudo-heraldry и оставляет честный read-only TUI:
- маленькие sigil badges вместо плохих гербов;
- верхняя панель снова компактнее;
- main dashboard поднимается выше;
- вся текущая функциональность сохранена.

## Важное решение

Настоящие гербы Mechanicus / Imperium должны появиться позже только в enhanced visual mode:

- web/canvas,
- image-capable terminal,
- или отдельный графический клиент.

Этот режим должен читать ту же truth-модель, что и TUI, но не пытаться притворяться графикой внутри терминала.

## Запуск

```powershell
Set-Location "E:\IMPERIUM\IMPERIUM_NEW_GENERATION\MECHANICUS\FORGE_TUI"
cmd /c .\LAUNCH_MECHANICUS_FORGE_CLIENT_V1_0.cmd
```
