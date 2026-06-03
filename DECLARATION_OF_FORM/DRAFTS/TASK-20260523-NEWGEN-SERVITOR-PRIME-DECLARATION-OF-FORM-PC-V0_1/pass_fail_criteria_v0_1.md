# PASS / FAIL CRITERIA V0.1 (DRAFT)

> Статус: `DRAFT / FOR OWNER+LOGOS CORRECTION`

## 1. Назначение

Этот документ задает рабочие критерии для будущих задач NewGen, чтобы:

1. прекратить generic PASS;
2. удерживать claim boundary;
3. блокировать fake-green;
4. измерять реальное усиление IMPERIUM.

## 2. PASS criteria (обязательный минимум)

Задача может получить PASS только если выполнены все условия:

1. `scope_truth`: все измененные пути находятся в заранее объявленном allowed scope.
2. `evidence_truth`: каждый ключевой claim ссылается на существующие evidence artifacts.
3. `verdict_scope`: verdict сформулирован как scoped (`PASS_FOR_<X>_ONLY`), не как абстрактный `PASS`.
4. `uncertainty_honesty`: не proven зоны явно помечены (`UNKNOWN`, `FOUNDATION_ONLY`, `NOT_PROVEN`, `PARTIAL`).
5. `operational_delta`: есть измеримый прирост управляемости (control/observability/safety/continuity), а не только новые документы.
6. `repo_closure`: финальный `git status --short` чистый или содержит только заранее согласованный bounded runtime output.

## 3. FAIL criteria (мгновенный провал)

Задача должна получить FAIL/BLOCK, если есть хотя бы один пункт:

1. выход за scope (`forbidden path touched`);
2. PASS-claim без доказательств;
3. скрытая неопределенность или подмена `FOUNDATION_ONLY` как production;
4. claim о live/prod/autonomy без подтверждающих артефактов;
5. несоответствие декларации touched paths и фактического diff;
6. отсутствие обязательных выходных артефактов задачи.

## 4. Fake-green criteria (отдельный блокер)

`FAKE_GREEN` фиксируется, если:

1. UI/отчет показывает “green”, а evidence refs отсутствуют или битые.
2. `UNKNOWN/MISSING/PARTIAL/FOUNDATION_ONLY` визуально/текстово подаются как success.
3. “готово” заявлено при read-only или preview-only механике без рабочего канала действия.
4. “production-ready” вывод сделан на основе demo/synthetic/route-only доказательств.
5. метрика “успеха” опирается на объем отчетов, а не на owner-visible control.

## 5. WARN criteria (не блокирует, но останавливает расширение)

WARN ставится, если:

1. выход есть, но часть связей еще `FOUNDATION_ONLY`;
2. evidence есть, но freshness/актуальность спорная;
3. operational delta ниже ожидаемого, но честно описан;
4. есть частичная приемка (`PARTIAL_ACCEPTED`) с явными ограничениями.

Правило: WARN-задача не открывает право на broad next step, пока WARN не закрыт или не принят Owner как осознанный риск.

## 6. Контрольные PASS-сигналы для NewGen Core

Для clean core progression должны быть видны такие сигналы:

1. `CURRENT_TRUTH` согласован с текущим `HEAD`.
2. Operator Cockpit показывает актуальный task/blocker/next step в одном окне.
3. Owner questions видны и имеют bounded decision path.
4. Action layer сохраняет request/result receipts и rollback semantics.
5. Organs влияют на исполнение не только описательно, но и через required checks/veto logic.
6. Repo hygiene отделяет current core от historical/runtime шума.

## 7. Минимальный формат verdict в финальных отчетах

Обязательная форма:

1. `OVERALL_VERDICT`: scoped verdict.
2. `PROVED`: список доказанных claims.
3. `NOT_PROVEN`: список недоказанных claims.
4. `NOT_RUN`: что не запускалось.
5. `KNOWN_LIMITATIONS`: границы применимости результата.

Пример:

`PASS_FOR_OPERATOR_COCKPIT_L1_READ_ONLY_OVERVIEW_ONLY`

## 8. Набор BLOCK-кодов для унификации

Рекомендуемые коды:

1. `BLOCK_SCOPE_BOUNDARY_VIOLATION`
2. `BLOCK_EVIDENCE_MISSING`
3. `BLOCK_FAKE_GREEN_RISK`
4. `BLOCK_PRODUCTION_OVERCLAIM`
5. `BLOCK_REQUIRED_OUTPUT_MISSING`
6. `BLOCK_OWNER_DECISION_REQUIRED`
7. `BLOCK_REPO_HYGIENE_UNCLASSIFIED`

