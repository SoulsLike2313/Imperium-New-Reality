# OWNER_ANSWER_LOCK_V0_1

Status: `OWNER_LOCKED_PROSE`
Admission: `DIRECT_REALITY_BY_OWNER`
Pack: `IMPERIUM-OWNER-FOUNDATION-DOCS-REALITY-0001`
Generated UTC: `2026-06-29T08:07:47.533447+00:00`
Validation: `PENDING_WARP_VALIDATORS`

## 0. Назначение

Этот документ фиксирует решения Owner-а после первой большой анкеты по будущей описи Империума. Он не является валидатором и не утверждает техническую полноту системы. Его задача — закрепить волю, чтобы следующие WARP-патчи могли строить схемы, валидаторы и receipts уже против ясной формы.

Ключевой принцип: **сначала фиксируем форму, затем через WARP рождаем валидаторы, затем валидаторы доказывают документы, затем документы получают техническое доверие.**

---

## A. Трон

### A1. Каноническое размещение

Решение Owner-а: Трон должен стать реальным органом.

Принятая архитектура:

```text
ORGANS/THRONE/                    # будущий канонический физический коронный орган
ORGANS/_CORE_GOVERNANCE/THRONE/   # существующий governance gateway / исторический слой / alias-зона
ORGANS/_CORE_GOVERNANCE/OWNER_DECISIONS/ # текущие owner-lock документы
```

Пока `ORGANS/THRONE/` не создаётся этим этапом как полноценный орган. Это будет зона `THRONE_CROWN_ORGAN_FOUNDATION`. Текущий документ только фиксирует решение.

### A2. Статус Трона

Трон — `CROWN_ORGAN`, коронный орган.

Он не входит в счёт 9 как обычный орган. Он держит, измеряет, валидирует и защищает форму ядра, но сам не может заявлять полноту ядра без 9 органов.

Закон взаимной полноты:

```text
CORE_COMPLETENESS = THRONE_COMPLETENESS × GREAT_NINE_COMPLETENESS
```

Если 9 органов неполны, Трон не имеет права заявить полное ядро. Если Трона нет, 9 органов не являются защищённым и самоописанным ядром.

### A3. Право блокировки

Астрономикон может заблокировать запуск рабочего цикла на входе, если входящий pack не имеет допустимой формы.

Трон выполняет финальную тронную валидацию после органных проверок. Его валидаторы должны быть строже, тоньше и глубже органных. Расхождение между organ verdict и Throne verdict считается источником обучения органа.

### A4. Начальный режим

Начальный режим Трона:

```text
THRONE_MODE = MEASURE_ONLY
```

Трон сначала показывает дыры, разрыв, боль, зоны риска и численную картину. Он не рубит систему сразу.

Путь усиления:

```text
MEASURE_ONLY → WARN → WARP_ONLY → BLOCK_LAND → BLOCK_CYCLE
```

### A5. Override

Финальный verdict Трона может отменить только Owner.

Custodes не отменяет verdict Трона. Custodes собирает trust evidence для Трона и отвечает на вопрос: можно ли верить органам, их валидаторам, receipts и матрицам.

Owner override допускается только через интервью/разбор:

```text
OWNER_OVERRIDE_INTERVIEW
  - почему verdict спорный;
  - какой валидатор мог ошибиться;
  - какие receipts неполны;
  - какой риск принимает Owner;
  - временный ли override;
  - какой follow-up patch обязан исправить причину спора.
```

Идеальная цель: Трон должен быть настолько доказательным, чтобы Owner почти никогда не хотел отменять его verdict.

---

## B. 9 органов

Финальный список 9 органов:

```text
ASTRONOMICON
ADMINISTRATUM
DOCTRINARIUM
MECHANICUS
INQUISITION
CUSTODES
STRATEGIUM
SCHOLA_IMPERIALIS
OFFICIO_AGENTIS
```

Каждый орган должен иметь одинаковый обязательный набор organ slots. Дополнительные уникальные слоты разрешены, но должны быть заявлены, объяснены и валидированы.

Каждый орган должен иметь собственные валидаторы по своему направлению. Работа строится не как хаотичный многопоток, а как контролируемый последовательный конвейер.

TUI должен быть матрёшкой:

```text
Imperium TUI
  → Throne view
  → Organ view
  → Task execution view
  → Receipt/export/archive view
```

---

## C. README / паспорт органа

README органа — главный человекочитаемый паспорт.

`ORGAN_CARD.json` — главный машиночитаемый паспорт, максимально понятный для LLM и валидаторов.

`MANIFEST.json` должен описывать все файлы органа с классификацией важности, статуса, владельца и риска. Не только важные формы: мусор и хвосты тоже должны быть видимы.

README обязан содержать:

```text
declared mission
declared identity
declared functions
declared tools
declared validators
declared receipts
declared matrices
declared forbidden scope
known gaps
negative lessons
maximal desired form
actual-vs-declared interpretation
```

Каждый орган должен широко описывать, что он НЕ делает. Это нужно для защиты от расползания функций и для корректного routing-а запросов.

---

## D. Перепись населения

Населением Империума считается всё, что живёт внутри контролируемых территорий:

```text
files
directories
organs
sub-organs
tools
validators
schemas
matrices
receipts
verdicts
roles
servitors
reports
task packs
patch packs
lessons
negative examples
WARP artifacts
garbage
quarantine
archives
dashboards
TUI entries
Eyes data exports
```

Каждый житель должен получить `imperium_id`.

Мёртвые, архивные, negative example, garbage и quarantine формы тоже считаются населением, но с особыми статусами: `ARCHIVE`, `NEGATIVE_EXAMPLE`, `ROGUE`, `GARBAGE`, `QUARANTINE`, `READY_FOR_REMOVAL`.

Для каждого жителя требуется provenance:

```text
откуда появился
каким task/patch/land создан
кто владелец
где canonical home
когда последний раз валидировался
какой validator/receipt доказывает состояние
```

---

## E. Task pack / patch pack / цикл

Task pack — это задача для сервитора / кодового исполнителя.

Сервитор получает:

```text
task_id
micro_prompt
указание обратиться в Administratum за контекстом
pass criteria
границы исполнения
ожидаемые receipts
fix-loop policy
```

Patch pack — это ручная/chat-agent delta, которую Owner и Logos Prime собирают в диалоге, а Owner внедряет руками. Patch pack не обязательно является задачей для CLI-сервитора.

Общий закон:

```text
любой task/patch сначала живёт в WARP;
после проверки WARP либо squash + land, либо abort;
fix loop оформляется как child task/patch pack.
```

Раздел task/patch pack требует отдельной подготовки после фундамента governance + mechanics, потому что родилось правило → должен родиться validator.

---

## F. Валидация и КПД

Вводятся все основные метрики. Начальная рыночная неразбериха допустима, потому что расширенная матрица параметров даст более чистую систему после стабилизации.

Шкала для органов и зон: `0–100`.

PASS: диапазон `80–90`.

`100` — предельная форма / clean candidate / путь к Core v1.0.

BLOCK для land должны вызывать:

```text
отсутствие README
отсутствие schema
отсутствие validator
отсутствие receipt
validator без receipt
receipt без регистрации
```

`declared_vs_actual_gap` не блокируется на раннем этапе. Наоборот, это основной датчик разрыва между желаемой формой и реальностью.

Это становится базой `CORE_LEVELING_SYSTEM`: ядро растёт как RPG-система от хаотичных файлов к clean Core v1.0.

Инквизиция обязана ловить любую грязь, даже микроскопическую, если она способна помешать работе.

---

## G. Видимость

Первым видимым инструментом должен стать TUI Трона / Imperium TUI.

Dashboard должен двигаться к управляемому canvas-like отображению. На раннем этапе допустимы markdown/json/html, но направление — интерактивная управляемая панель.

Eyes presence разрешена только как data export/status feed для стабильного viewer. Visual refit заморожен.

Трон должен показывать всю боль сразу:

```text
красные gaps
сегменты боли
принадлежность к органам/зонам
самоанализ
области внимания
метрическую рекомендацию следующей области работы
```

Трон не должен автоматически навязывать конкретный patch, но должен рекомендовать область внимания, где выгоднее всего приложить силы.

---

## H. Land policy

Текущий owner-lock этап допускает прямое помещение документов в Reality, потому что это фиксация решения Owner-а.

Для дальнейших этапов базовая политика:

```text
документ → validator → organ assignment → receipt → review → land
```

Документ не land-ится, пока его validator не одобрил, кроме явно owner-authorized foundation documents.

Validator не land-ится без receipt.

Органный README можно land-ить даже при фактической полноте органа ниже 50%, если README честно показывает gap, а validator подтверждает корректность измерения.

Все будущие этапы сначала держатся в WARP до команды land или abort.

В споре между полнотой описания и минимально рабочим validator приоритет имеет строгий, скриптовый, беспристрастный validator.
