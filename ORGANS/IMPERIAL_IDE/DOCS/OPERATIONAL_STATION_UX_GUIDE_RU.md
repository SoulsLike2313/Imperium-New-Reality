# Operational Station UX Guide

Статус: CANDIDATE_V0_1

## Что изменилось

Operational Station показывает human summary первым, а full JSON оставляет как отдельное действие через show-json.

Основные команды:

- show-summary - краткая человеческая сводка.
- show-json [path] - полный JSON без truncation.
- path-actions <path> - copy-ready команды для пути.
- station-ux-smoke - общий smoke и receipts.

## Границы

Real servitor execution, live LLM backend, arbitrary shell, VM2 и VM3 остаются закрыты. Handoff-ready не означает execution-done.
