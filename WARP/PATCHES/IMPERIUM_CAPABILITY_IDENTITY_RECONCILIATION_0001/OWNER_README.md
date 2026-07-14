# IMPERIUM_CAPABILITY_IDENTITY_RECONCILIATION_0001

Узкий Patch Pack для Phase 6.

Он не обновляет хэши вслепую. До записи он доказывает:

- WARP и Reality находятся на ожидаемых HEAD;
- canonical registry digest до изменения корректен;
- ровно две ACTIVE capability имеют adapter mismatch;
- это `CORE_REPORT_BUILDER` и `CORE_VALIDATION_SUITE`;
- зарегистрированные старые хэши совпадают с ожидаемыми;
- реальные новые хэши совпадают с заранее измеренными;
- все остальные ACTIVE capability уже совпадают;
- после изменения весь registry проходит identity validation.

Затем runner выполняет `ui-action refresh_state` с пустым PATH и pinned Git/Pwsh.
`run_core_diagnostic` намеренно не запускается, чтобы сохранить Phase 6 baseline `0 -> 1`.
