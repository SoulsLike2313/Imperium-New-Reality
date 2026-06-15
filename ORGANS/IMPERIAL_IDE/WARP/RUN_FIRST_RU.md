# Первый запуск WARP

Проверка изоляции, fake-green и release manifest:

```powershell
& .\ORGANS\IMPERIAL_IDE\run_warp_zone.ps1 -Command smoke
```

Просмотр статуса:

```powershell
& .\ORGANS\IMPERIAL_IDE\run_warp_zone.ps1 -Command status
```

Явное создание локальной сессии:

```powershell
& .\ORGANS\IMPERIAL_IDE\run_warp_zone.ps1 -Command open `
  -Task 'candidate task' -Kind THIRD_PARTY
```

Runtime хранится в `ORGANS/IMPERIAL_IDE/WARP/runtime/` и игнорируется Git.
Autostart не зарегистрирован. Verdict `RELEASE` создаёт только manifest и не
продвигает изменения в kernel.
