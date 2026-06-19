# IMPERIUM — CONTEXT PACK DOCTRINE v0_1

## Закон
Администратум обязан собирать **самодостаточный** пак истории так, чтобы
**пак = 100% факта и истории** = полный вход в контекст и ориентацию по Империуму.
Гит — **лёгкая локальная страховка/чтение** (терминальный `git` для слежения за
коммитами и числом изменённых файлов), а не источник истины и не внешняя зависимость.

## Почему это понадобилось (корень дефекта)
Раньше handoff-пак нёс состояние + доктрину + часть инсталляторов, но **не нёс
исходный код исполняемого слоя** (`HARNESS\TOOLS\WARP\*.ps1` и пр.). Из-за этого
логос-оркестратор знал, *что* делает WARP, но не видел *как* — и не мог дать точные
команды без гадания. Гит-ссылка входом не является (её нельзя прочитать без
живого доступа). Вывод: пак обязан быть самодостаточным.

## Обязательная структура пака
```
IMPERIUM_CONTEXT_PACK_<stamp>/
  CONTEXT_ENTRY.md          # точка входа: порядок чтения
  MANIFEST.json             # sha256 + размер каждого файла (целостность)
  TOOLCHAIN/                # ПОЛНЫЙ исходник исполняемого слоя
    HARNESS/TOOLS/...        #   warp-start.ps1, warp-land.ps1, инсталляторы, ...
    REALITY/ORGANS/ASTRONOMICON/TOOLS/...
  HISTORY/                  # локальный терминальный git
    git_head.txt            #   rev-parse HEAD
    git_log.txt             #   лог N коммитов
    git_numstat.txt         #   что менялось (numstat)
    changed_files.txt       #   число изменённых файлов на коммит (shortstat)
    git_status.txt          #   porcelain (должно быть пусто)
    branches.txt / remotes.txt
  STATE/                    # текущее состояние
    continuity_manifest.json
    warp_active.json
  DOCTRINE/                 # FORM, законы органов
```

## Обязательные элементы (проверяются верификатором)
- Каталоги: `TOOLCHAIN`, `HISTORY`, `STATE`, `DOCTRINE`.
- Файлы: `TOOLCHAIN/HARNESS/TOOLS/WARP/warp-start.ps1`, `.../warp-land.ps1`,
  `HISTORY/git_head.txt`, `HISTORY/git_log.txt`, `HISTORY/git_status.txt`,
  `HISTORY/changed_files.txt`, `STATE/continuity_manifest.json`, `CONTEXT_ENTRY.md`.

## Контракт целостности
- `MANIFEST.json` строит ТОЛЬКО `context_pack_lib.py` (единый источник истины по хэшам).
- Верификатор `verify_context_pack.py` обязан давать `SELF_SUFFICIENT_OK` до того,
  как пак признан валидным входом. Любой `HASH_MISMATCH` / `MISSING_REQUIRED` /
  `UNTRACKED_FILE` / `HEAD_MISMATCH` = пак не передаётся.

## Роль гита (явно)
- Источник истины = пак. Гит = локальная сверка свежести и истории.
- `git_head` в манифесте сверяется с `git rev-parse HEAD` при сборке (`--expect-head`).
- GitHub-коннектор не требуется и не является зависимостью.
