# SERVITOR ENTRY CONTRACT v0_1 — допуск Grok/Codex через Астру

> Орган-владелец: ASTRONOMICON. Стадия: INBOUND. Permit делегирован Трону.
> Evidence движка: E3_EXECUTED. Закон — DOCTRINARIUM.

## Правило (нерушимое)
Ни один **SERVITOR_PRIME** (сейчас активны два: **GROK**, **CODEX**) **не вправе писать**
в `E:\IMPERIUM_REALITY` (или в WARP-worktree этой задачи) **без допущенного и привязанного по
digest таск-пака**. Допуск выдаёт только вход Астры через `servitor_intake.py admit`.
Сервитор не саморазрешает.

## Обязательный первый шаг сервитора
Перед ЛЮБОЙ записью/коммитом по задаче сервитор выполняет:
```bash
python3 servitor_intake.py check <pack_dir> --servitor <GROK|CODEX> --reality-root E:\IMPERIUM_REALITY
```
- `VERDICT: WORK_PERMITTED` (exit 0) → работать вправе строго в рамках payload этого пака.
- `VERDICT: WORK_DENIED` (exit 2) → **СТОП**. Любая запись запрещена. Сначала допуск.

## Как пак получает допуск
1. Сервитор (или owner) формирует таск-пак: `TASK_MANIFEST.json` (схема
   `imperium.astra_task_pack.v0_1`) + файлы из `payload[]` реально лежат в паке.
   Идентичность сервитора — поле `servitor: GROK|CODEX` (submitted_by = `SERVITOR`).
2. Прогон входа Астры с выдачей токена:
   ```bash
   python3 servitor_intake.py admit <pack_dir> --servitor <GROK|CODEX> --reality-root E:\IMPERIUM_REALITY
   ```
   - `ADMIT` → токен `ORGANS\ASTRONOMICON\ADMISSIONS\<task_id>__<servitor>.admission.json`
     + строка в `ADMISSIONS\LEDGER.csv`. Только теперь сервитор работает.
   - `REJECT` → причины по воротам (FORM/COMPLETENESS/CORRECTNESS), токен НЕ выдан.

## Digest-binding (анти-подмена)
Токен фиксирует `payload_digest` допущенного пака. `check` пересчитывает digest текущего
пака и сравнивает. Любое изменение пака после допуска → `DENY: DIGEST_MISMATCH` → работать
нельзя, нужен новый допуск. Токен одного сервитора не подходит другому → `DENY: SERVITOR_MISMATCH`.

## Границы (что эта застава ПОКА делает и не делает)
- ДЕЛАЕТ: машинную валидацию таск-пака на входе и привязку права работы к допуску (E3).
- НЕ делает (следующие шаги): верховный permit Трона, исходящую проверку результата
  Сервитора + rework-loop, авто-интеграцию патча, аппаратный git-hook, блокирующий коммит
  без токена. Это hardening следующих шагов Фазы A.

## Честность
Никогда fake-green. Сервитор не прячет dirty-state, не выдаёт рассуждения за исполнение,
не обходит ворота. Вывод по-русски, gender-neutral.
