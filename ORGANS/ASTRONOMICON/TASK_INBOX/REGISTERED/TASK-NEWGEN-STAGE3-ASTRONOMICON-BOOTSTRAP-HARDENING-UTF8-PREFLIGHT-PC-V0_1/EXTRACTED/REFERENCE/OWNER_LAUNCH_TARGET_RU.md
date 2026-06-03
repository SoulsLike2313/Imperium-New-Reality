# Целевая форма запуска после hardening

1. Запустить owner-facing launcher Астрономикона.
2. Launcher сам делает bootstrap preflight.
3. Если templates missing/BOM/invalid — launcher говорит, что делать или запускает repair.
4. Потом открывает task entry TUI.
5. Owner указывает ZIP.
6. Астрономикон регистрирует task и показывает task_id.
7. Owner даёт Servitor только:
   TASK_ID: ...
   start task
