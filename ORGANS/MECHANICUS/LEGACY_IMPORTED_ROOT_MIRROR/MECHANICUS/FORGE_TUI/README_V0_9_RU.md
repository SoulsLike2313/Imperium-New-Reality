# Mechanicus Forge Client V0.9 Steampunk Patch

## Цель

Приблизить текущий read-only TUI к целевому forge-console reference:

- больше steampunk/forge ощущения;
- бронзовые/латунные рамки;
- бордо/бронза/ледяная сталь/фиолетовый дух машины;
- модульные side seals;
- минимальная зависимость от терминала;
- без bitmap, сервера и webview.

## Честное ограничение

Это всё ещё terminal TUI. Он не сможет дать настоящие текстуры, блики, рельеф, настоящие графические гербы и трубы как в сгенерированном reference.

Эта версия делает лучший terminal-native приближенный слой. Для 95% сходства нужен отдельный enhanced/webview/canvas mode.

## Запуск

```powershell
Set-Location "E:\IMPERIUM\IMPERIUM_NEW_GENERATION\MECHANICUS\FORGE_TUI"
cmd /c .\LAUNCH_MECHANICUS_FORGE_CLIENT_V0_9.cmd
```
