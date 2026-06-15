# Mechanicus Forge Client V0.5 RU Index

## Что это

Русский индексный слой для Mechanicus Forge Client.

Цель: Owner должен понимать, что означает каждая категория, статус, surface и socket, но машинные ID должны сохраняться.

## Принцип

Формат отображения:

`РУССКОЕ НАЗВАНИЕ / MACHINE_ID`

Примеры:

- `ИНСТРУМЕНТЫ / TOOLS`
- `ПЕСОЧНИЦА / SANDBOX`
- `КАНДИДАТ / CANDIDATE`

## Почему так

Полностью заменить ID на русский нельзя: Servitor, Mechanicus registry, Evidence Index и scope packs должны сохранять стабильные машинные ключи.

Поэтому V0.5 добавляет понятный русский слой, но не ломает машинную адресацию.

## Запуск

```powershell
Set-Location "E:\IMPERIUM\IMPERIUM_NEW_GENERATION\MECHANICUS\FORGE_TUI"
cmd /c .\LAUNCH_MECHANICUS_FORGE_CLIENT_V0_5_RU.cmd
```

## Зависимость

V0.5 импортирует V0.4/V0.3, поэтому предыдущие файлы должны оставаться в папке.
