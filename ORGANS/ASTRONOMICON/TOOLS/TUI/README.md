# IMPERIUM TUI — личный лаунчер Трона + органы

Единая точка входа для оркестрации империума. Работает в любом терминале (вкл. терминал IDE),
рядом с другими CLI-агентами (Codex / Grok).

## Состав
- `imperium_textual.py` — **Rich/Textual backend** (макс. красота: truecolor, живые панели, формы, спарклайн, fade-in). Опционален.
- `throne_tui.py`  — TUI Трона на curses (оркестрация, верховный permit, вход в органы).
- `organ_tui.py`  — TUI одного органа (универсально для всех 9).
- `imperium_tui_core.py` — ядро: backend + UI (curses / текстовый fallback) + формы.
- `imperium.ps1`  — лаунчер (команда `imperium`); авто-выбор Rich ↔ curses.
- `install_rich.ps1` — установка textual+rich + selftest.
- `requirements-rich.txt` — зависимости Rich-бэкенда.
- `imperium_tui.config.json` — локальный конфиг машины (пути reality/inbox/receipts + движки).
- `banner.txt` (опционально) — твой арт; подхватывается вместо дефолтного баннера.

## ✨ Rich/Textual backend (максимальная красота)
Опциональный слой поверх того же backend — truecolor-тема (золото/багрянец), скруглённые
панели с заголовками, **живой авто-рефреш** данных (раз в 2с), спарклайн активности органов,
fade-in баннера, часы в шапке и форма создания пака в одном окне с выпадающими списками.
```powershell
# 1) поставить (один раз), затем selftest
.\install_rich.ps1
#    или вручную:  pip install "textual>=0.50" rich

# 2) запуск (лаунчер сам подхватит Rich, если установлен)
imperium
imperium -Rich      # принудительно Rich
imperium -Curses    # принудительно curses-fallback
```
Если textual не установлен — лаунчер молча уходит в проверенный curses-вариант (переносимость сохраняется).

### Управление в Rich-режиме
- `↑↓` + `Enter` — навигация по меню слева; мышь поддерживается.
- `d` — войти в орган · `b` — назад к Трону · `p` — permit · `n` — новый пак · `v` — валидация · `c` — цикл (dry) · `r` — обновить · `q` — выход.
- Форма нового пака: `Tab`/`↑↓` между полями, `←→` на списках, кнопки «Создать»/«Отмена», `ESC` — отмена.
- selftest без TTY:  `python imperium_textual.py --selftest`

## Запуск
```powershell
# Трон
python throne_tui.py
# Орган напрямую
python organ_tui.py MECHANICUS
# Через лаунчер
.\imperium.ps1                 # Трон
.\imperium.ps1 MECHANICUS      # орган
```

## Команда `imperium` из любого терминала
Добавь функцию в PowerShell-профиль (один раз):
```powershell
$tui = 'E:\IMPERIUM_HARNESS\TOOLS\TUI'
if (-not (Test-Path $PROFILE)) { New-Item -ItemType File -Path $PROFILE -Force | Out-Null }
Add-Content $PROFILE "`nfunction imperium { & '$tui\imperium.ps1' @args }"
. $PROFILE
```
Теперь в любом терминале: `imperium` (Трон) или `imperium MECHANICUS` (орган).

## Управление
- `↑↓` или `j/k` — выбор, `Enter` — ок, `q` — назад/выход.
- В формах ввода: печатай, `Enter` — подтвердить, `ESC` — отмена.
- Без `curses` (стоковый Windows Python) — автоматически текстовое меню.
  Для полноэкранного: `pip install windows-curses`.

## Модель власти
- Только **Трон** выдаёт `throne_permit = GRANTED`.
- Орган по умолчанию `DENIED`: может валидировать и dry-run, но **не land**.
- APPLY/полный цикл — только после ADMIT (Astra) и GRANTED (Трон).

## Базовые формы органа (ультрабазовые — каркас под будущую органную обработку)
- 📦 Паки в очереди
- 📝 Новый таск-пак (форма → создаёт скелет пака в inbox + автовалидация)
- 🔎 Валидация · ⚙ Цикл dry-run · 🚀 Цикл APPLY (требует GRANTED)
- 📡 Последние данные (git HEAD/status + содержимое органа + рецепты)
- 🧾 Рецепты

## Связка с терминальными агентами
Типовой цикл: в Троне/органе «Новый таск-пак» → отдаёшь папку пака сервитору
(Codex/Grok) на наполнение `files/`+payload → возврат → валидация → (Throne GRANTED) → цикл APPLY.

## selftest (без TTY)
```powershell
python throne_tui.py --selftest
python organ_tui.py MECHANICUS --selftest
```
