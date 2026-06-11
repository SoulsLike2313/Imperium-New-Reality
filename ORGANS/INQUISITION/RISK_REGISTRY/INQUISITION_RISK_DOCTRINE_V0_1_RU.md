# Inquisition Risk Doctrine V0.1

Инквизиция — read-only орган диагностики. Её задача не чистить и не удалять, а видеть беды, классифицировать риски, объяснять причину и выдавать рекомендации для владельца, Data Atlas и Mechanicus.

## Основной закон

- Не удалять.
- Не перемещать.
- Не чинить автоматически.
- Сначала доказательство, потом классификация, потом owner-visible отчёт.

## Триада наблюдения

- Data Atlas: что существует и где лежит.
- Mechanicus: чем система умеет работать и какие инструменты паспортизированы.
- Inquisition: что опасно, грязно, устарело, непонятно или не готово к promotion.

## Классы бед

- ENCODING_MOJIBAKE: битая кодировка, смешение UTF-8/CP1251/CP866, сломанные glyph/emoji labels.
- SOURCE_RUNTIME_LEAK: runtime/output/local handoff следы внутри source tree.
- GENERATED_ARTIFACT_IN_SOURCE: generated/cache/report artifacts в source tree.
- PYTHON_CACHE_IN_SOURCE: __pycache__ или .pyc рядом с source.
- ARCHIVE_REVIEW_REQUIRED: ZIP/архив внутри source требует жизненного решения.
- LEGACY_MIRROR_CONTAMINATION: legacy mirror занимает боевое пространство без паспорта/изоляции.
- NO_TOOL_PASSPORT: tool-like script есть, но Mechanicus не знает его как инструмент.
- NO_OWNER: файл или инструмент не имеет владельца/органа.
- NO_VALIDATION_RECIPE: инструмент нельзя уверенно проверить.
- ACTION_REGISTRY_DRIFT: action registry расходится с фактическими tool/passport/action файлами.
- WRITE_ACTION_WITHOUT_SAFETY: действие может писать, но safety/allowed roots не очевидны.
- VERSION_DRIFT: UI/API/package/docs показывают разные версии.

## Severity

- CRITICAL: может сломать работу, исказить данные, записать не туда или загрязнить source runtime-артефактами.
- WARNING: мешает управлению, усложняет навигацию, снижает доверие к отчётам.
- INFO: технический долг или классификационный пробел.

## Promotion gate

Если есть CRITICAL findings, promotion в main должен требовать owner review. Если есть WARNING, promotion допустим только с явным отчётом и планом следующего шага.
