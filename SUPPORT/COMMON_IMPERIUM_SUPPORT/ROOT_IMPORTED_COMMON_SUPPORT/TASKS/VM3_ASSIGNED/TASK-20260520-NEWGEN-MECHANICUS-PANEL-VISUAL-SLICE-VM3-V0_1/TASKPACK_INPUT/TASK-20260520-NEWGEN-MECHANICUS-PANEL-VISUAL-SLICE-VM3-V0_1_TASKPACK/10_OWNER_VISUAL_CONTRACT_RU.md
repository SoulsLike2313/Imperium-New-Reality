# OWNER VISUAL CONTRACT (RU)

## Главная цель

Нужно доказать, что IMPERIUM может не только строить backend/truth/topology, но и собирать **сильную визуальную форму** быстро, адресно и без скатывания в generic-dashboard.

## Что именно делаем сейчас

Не весь Sanctum.  
Не весь фронт.  
Не все органы.

Сейчас делаем **один concrete slice**: `SANCTUM.RIGHT_CONTEXT_DOCK.MECHANICUS_PANEL`.

Это должна быть **изолированная, красивая, owner-reviewable форма**, которую потом можно интегрировать в общий Sanctum shell.

## Принимаемая художественная линия

- sci-fi / warhammer / holograph / neuro-second-mind form
- не flat SaaS
- не bootstrap-шаблон
- не “обычные карточки”
- форма должна ощущаться как операторская техно-капсула / часть мозга Sanctum
- справа рождается панель Механикус
- это именно **панель органа**, не просто окно с текстом

## Что должно чувствоваться

- темная глубина / металл / стекло / красные forge-акценты / холодные cyan-индикаторы
- ощущение machine intelligence
- аккуратная иерархия
- зона миссии / статуса / команд / инструментов / evidence
- сильный контур и композиция
- видно, что это орган Механикус, а не generic admin panel

## Ключевые запреты

1. Нельзя делать generic bootstrap/SaaS панель.
2. Нельзя врать про backend truth.
3. Нельзя ставить `CONNECTED/PASS/READY`, если источник не доказан.
4. Нельзя забивать панель сплошной кашей текста.
5. Нельзя делать просто список карточек без визуальной идеи.
6. Нельзя делать белые/серые офисные таблицы.
7. Нельзя рушить читабельность ради красоты.
8. Нельзя строить весь Sanctum вместо одного slice.
9. Нельзя трогать запрещенные roots.
10. Нельзя подменять unknown/stub fake success-статусом.

## Что можно и нужно

- можно использовать included asset references как визуальный ориентир
- можно делать собственную композицию, если она сильнее текущей
- можно брать target-shell язык из референса и адаптировать его к Sanctum panel slice
- можно делать анимации, но дешевые и отключаемые
- можно делать `UNKNOWN / STUB / LOCKED` элегантно
- можно делать pane transitions / soft pulse / holograph accents

## Минимальная функциональная структура slice

Панель должна иметь 5 смысловых зон:

1. Header / Identity
   - Mechanicus sigil / title
   - mission line / short description
   - truth pills / state chips

2. Current Activity / Work Zone
   - короткий список текущих вещей
   - item → state mapping
   - ясно что сейчас главное

3. Command / Operator Palette
   - важные operator actions only
   - `status`, `tools`, `check`, `where`, `help`, `raw`
   - без избыточной кнопочной мусорности

4. Tool Registry / Capability Overview
   - компактный реестр
   - counts / health / availability
   - можно partial/stub, но честно

5. Footer / Evidence / Mission Focus
   - latest report / latest receipt / trust note / warning note
   - коротко, не перегружено

## Смысл acceptance

Owner должен открыть screenshots и сказать:
“Вот, это уже не generic-bredyatina, это реальная форма Mechanicus panel внутри IMPERIUM.”
