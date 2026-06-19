# IMPERIUM ROOTS — доктрина адаптивных зон по алиасам (v0_1)

## Зачем
Скрипты Империума НЕ хардкодят `E:\IMPERIUM_*`. Зоны адресуются АЛИАСАМИ,
а реальные пути резолвятся в одном месте. Перенос на другой диск/машину =
правка одного конфига (или одной ENV), без правки скриптов.

## Канонические алиасы
- `REALITY`  — git-ствол (master), дефолт `E:\IMPERIUM_REALITY`
- `WARP`     — worktree-зона задач, дефолт `E:\IMPERIUM_WARP`
- `HARNESS`  — инструменты/память/чеки, дефолт `E:\IMPERIUM_HARNESS`
Конфиг может добавлять свои алиасы (напр. `SCRATCH`).

## Приоритет резолва (от высшего)
1. ENV `IMPERIUM_<ALIAS>` (напр. `IMPERIUM_REALITY`)
2. конфиг `imperium.roots.json` (первый найденный)
3. встроенный дефолт (`E:\IMPERIUM_<ALIAS>` для канона)

## Поиск конфига (первый существующий)
1. ENV `IMPERIUM_ROOTS` (явный путь к файлу)
2. рядом с резолвером
3. `%ProgramData%\Imperium\imperium.roots.json` (или `/etc/imperium/...`)
4. вверх от CWD: `.imperium\roots.json`

## Синтаксис алиас-пути
`@ALIAS\подпуть` или `@ALIAS/подпуть` -> `<root>\подпуть`.
Сигил `@` выбран, чтобы не путать с буквой диска (`C:`).
Путь без `@` возвращается как есть (обратная совместимость).

## API
PowerShell (`Imperium.Roots.psm1`): `Get-ImperiumRoot`, `Resolve-ImperiumPath`, `Show-ImperiumRoots`.
Python (`imperium_roots.py`): `get(alias)`, `resolve(path)`, CLI `show|get|resolve|doctor`.

## Адаптация существующих скриптов (drop-in)
PowerShell — заменить хардкод-дефолты:
```
$mod = Join-Path $PSScriptRoot 'Imperium.Roots.psm1'
if (-not (Test-Path $mod)) { $mod = 'E:\IMPERIUM_HARNESS\TOOLS\ROOTS\Imperium.Roots.psm1' }
Import-Module $mod -Force -ErrorAction SilentlyContinue
function R($a,$d){ if(Get-Command Get-ImperiumRoot -EA SilentlyContinue){Get-ImperiumRoot $a}else{$d} }
$Reality = R 'REALITY' 'E:\IMPERIUM_REALITY'
$Warp    = R 'WARP'    'E:\IMPERIUM_WARP'
$Harness = R 'HARNESS' 'E:\IMPERIUM_HARNESS'
```
Python:
```
import imperium_roots as R
REALITY, WARP, HARNESS = R.get('REALITY'), R.get('WARP'), R.get('HARNESS')
path = R.resolve('@REALITY/ORGANS/ASTRONOMICON/TOOLS/astra_gate.py')
```
Падение резолвера не ломает скрипт — дефолты сохраняются.
