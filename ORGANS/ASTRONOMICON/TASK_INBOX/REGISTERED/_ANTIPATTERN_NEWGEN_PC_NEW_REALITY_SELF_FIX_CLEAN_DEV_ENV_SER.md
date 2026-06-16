# ⚠️ Анти-паттерн: раздутый таскпак (негативный пример)

**Оригинал (был в ядре):** ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/TASK-NEWGEN-PC-NEW-REALITY-SELF-FIX-CLEAN-DEV-ENV-SERVITOR-CONTROL-MECHANICUS-SKILL-ARSENAL-AND-REPO-STERILIZATION-PC-V0_1
**Длинных путей (>240) было:** 11
**Полная форма (архив):** E:\\IMPERIUM_HARNESS\\ARCHIVE\\BAD_EXAMPLES\\TASK-NEWGEN-PC-NEW-REALITY-SELF-FIX-CLEAN-DEV-ENV-SERVITOR-CONTROL-MECHANICUS-SKILL-ARSENAL-AND-REPO-STERILIZATION-PC-V0_1\\

## Почему это плохо
- Имя задачи продублировано в папке и в вложенном TASKPACK_* (два сегмента по ~100 символов).
- Глубокая вложенность → пути >240 символов → ломают git/инструменты, плодят грязь.

## Урок
- Таскпаки именовать коротким слагом; не дублировать имя; глубина <= 3.

_Сохранено как назидание (20260616-162353)._