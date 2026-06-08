# Stage Loop Copy-Contour Bridge and Motion Fix v0.8.1

Назначение: закрыть хвосты H-review после Web Sanctum v0.8.

## Правила

1. `copytree_no_git_metadata` WARP не должен проваливать Inquisition только потому, что нет `.git` и `current_head` недоступен.
2. Для copy-contour разрешён только promotion route через patch/diff bundle. Cherry-pick недоступен.
3. `ConnectionAbortedError`, `BrokenPipeError`, `ConnectionResetError` во время `/api/jobs` polling считаются нормальным client-disconnect noise и не должны загрязнять Playwright лог traceback-ами.
4. Web Sanctum должен показывать явную motion feedback при нажатии action-кнопок: dispatching, job accepted, busy sweep, machine spirit pulse.
5. Commit/push остаются вне UI и вне bridge action registry.

## Expected verdicts

- Git worktree WARP: strict HEAD/base validation.
- Copy-contour WARP: `PASS_WITH_WARNINGS` при отсутствии forbidden generated files.
- Promotion preview для copy-contour: `PATCH_OR_DIFF_BUNDLE_REQUIRED`.

## Owner review

После применения патча проверить:

- Web Sanctum badge `V0.8.1`.
- Inquisition больше не FAIL только из-за `current_head: unknown` на copy-contour.
- Promotion Preview показывает route.
- Playwright tests/screenshots проходят без шумного traceback от закрытого клиентского соединения.
- Кнопки дают видимый premium loading/click feedback.
