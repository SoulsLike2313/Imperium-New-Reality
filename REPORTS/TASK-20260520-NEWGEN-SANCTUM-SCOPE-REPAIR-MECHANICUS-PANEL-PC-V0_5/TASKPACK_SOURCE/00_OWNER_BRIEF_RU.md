# Owner Brief RU — TASK-20260520-NEWGEN-SANCTUM-SCOPE-REPAIR-MECHANICUS-PANEL-PC-V0_5

## Почему эта задача появилась

Предыдущий V0_3 дал две ошибки:

1. **Неверный scope отчетности**  
   В финальном отчете был путь:
   `E:\IMPERIUM\ORGANS\MECHANICUS\REPORTS\TASK-20260520-SANCTUM-CLEAN-ANCHOR-SSE-LIVE-CONSOLE-PC-V0_3`

   Это старый/main контур. Owner не давал команду на слияние или перенос в main organs. Сейчас работа идет **только в `IMPERIUM_NEW_GENERATION`**.

2. **Неверная UX-форма**  
   Был сделан LIVE/terminal-like экран и дополнительные логи. Owner ожидает другое:
   - клик по узлу **Mechanicus** в мозговой карте должен открывать живую рабочую панель органа;
   - панель должна быть похожа на целевую operator console;
   - в ней Owner видит работу Mechanicus и может давать задания/команды;
   - raw terminal существует, но только как technical/raw mode.

## Главная цель

Сделать **scope repair + real New Generation Mechanicus operator panel**:

- все новые task reports/evidence: только под `E:\IMPERIUM\IMPERIUM_NEW_GENERATION\REPORTS\TASK-20260520-NEWGEN-SANCTUM-SCOPE-REPAIR-MECHANICUS-PANEL-PC-V0_5`;
- source changes: только под `E:\IMPERIUM\IMPERIUM_NEW_GENERATION\...`;
- клик по Mechanicus открывает operator panel;
- панель работает в 1366x768 без адского горизонтального/вертикального расползания;
- SSE/live status честный;
- main `ORGANS/` и main `SANCTUM/` не трогать.

## Что НЕ делать

- Не переносить main Mechanicus в New Generation.
- Не писать новые отчеты в `E:\IMPERIUM\ORGANS\...`.
- Не трогать `IMPERIUM_TEST_VERSION`, если только не read-only сравнение.
- Не активировать Throne/Custodes.
- Не объявлять PASS, если клик по Mechanicus не открывает панель.
