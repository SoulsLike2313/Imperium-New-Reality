# ⚠️ Анти-паттерн: раздутый таскпак (негативный пример)

**Оригинал (был в ядре):** SUPPORT/COMMON_IMPERIUM_SUPPORT/ROOT_IMPORTED_COMMON_SUPPORT/TASKS/VM3_ASSIGNED/TASK-20260520-NEWGEN-MECHANICUS-PANEL-LUXURY-NEURO-TEXTURE-PRESSURE-VM3-V0_3
**Длинных путей (>240) было:** 26
**Полная форма (архив):** E:\\IMPERIUM_HARNESS\\ARCHIVE\\BAD_EXAMPLES\\TASK-20260520-NEWGEN-MECHANICUS-PANEL-LUXURY-NEURO-TEXTURE-PRESSURE-VM3-V0_3\\

## Почему это плохо
- Имя задачи продублировано в папке и в вложенном TASKPACK_* (два сегмента по ~100 символов).
- Глубокая вложенность → пути >240 символов → ломают git/инструменты, плодят грязь.

## Урок
- Таскпаки именовать коротким слагом; не дублировать имя; глубина <= 3.

_Сохранено как назидание (20260616-162353)._