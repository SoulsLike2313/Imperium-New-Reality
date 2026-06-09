# Playwright / Visual Inquisition Contract v0.1

Назначение: сделать Playwright штатным органом зрения Web Sanctum, доступным owner и агентам прямо из IDE.

## Принципы

- Evidence пишется только во внешний runtime/output контур: `E:\_LOCAL_HANDOFF\SERVITOR_OUTPUTS\MEGA_PLAYWRIGHT_AUDIT_*`.
- Source repo не используется как место хранения скриншотов, временных specs и report-sprawl.
- Действия проходят через allowlisted Web Sanctum bridge; arbitrary shell недоступен.
- По умолчанию аудит безопасный: visual/read-only + safe-actions вроде Data Atlas scan.
- PNG используется только для ключевых контрольных кадров; массовые скрины и scroll tiles пишутся в JPEG.
- CSV используется для карт навигации, действий, pain map и screenshot manifest.
- JSON остаётся machine truth: API, git truth, browser logs.
- Markdown report остаётся owner-readable summary.

## Профили

### light
Быстрый аудит: минимум visual evidence, JPEG, CSV/JSON/MD.

### balanced
Дефолт: ключевые PNG, массовые JPEG quality 76, Data Atlas capture, pain map.

### full
Глубокий протык: больше scroll tiles, DOM text snapshot, расширенный visual corpus.

## Owner-facing result

После запуска из IDE job должен показать output_root, owner_report, screenshot_manifest, pain_map и navigation_map.

## Запреты

- Не commit.
- Не push.
- Не delete.
- Не cleanup.
- Не писать screenshots/test-runners в source.
