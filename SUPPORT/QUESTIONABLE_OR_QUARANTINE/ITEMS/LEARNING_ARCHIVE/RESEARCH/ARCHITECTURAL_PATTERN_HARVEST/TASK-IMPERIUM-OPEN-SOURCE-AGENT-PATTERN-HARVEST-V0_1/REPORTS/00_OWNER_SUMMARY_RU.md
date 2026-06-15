# Owner Summary RU — Architectural Pattern Harvest

## Что это такое

Это не установка чужих фреймворков и не переход на LangGraph/CrewAI/OpenHands. Это разведка архитектурных решений: мы смотрим, как сильные системы решали проблемы агентов, инструментов, памяти, маршрутов, чекпоинтов, sandbox, ролей, observability и проверок, а затем переводим полезное в собственные IMPERIUM-native contracts.

## Главный вывод

IMPERIUM не должен брать внешний framework как хозяина. IMPERIUM должен взять архитектурные паттерны и выразить их своими файлами, своими агентами, своими gates, своими receipts и своим Sanctum/CLI слоем.

## Самые ценные паттерны

| Паттерн | Откуда | Что берём для IMPERIUM |
|---|---|---|
| Tool/context boundary | MCP | Skill Bundle Protocol + Tool State Protocol |
| Checkpointed state graph | LangGraph | Route/Checkpoint Protocol |
| Subagent manifest + scoped tools/memory | Claude Code | Organ-Agent Protocol |
| Lifecycle hooks | Claude Code | Agent event ledger + start/stop receipts |
| Agent-Computer Interface | SWE-agent | Narrow CLI commands + action parser + safe execution surface |
| Trajectories / inspectors | SWE-agent | Route session traces + Sanctum trace view |
| Sandboxed end-to-end workspace | OpenHands | Workspace permission boundary, but not direct canon mutation |
| SOP team pipeline | MetaGPT | Organ SOP pipeline with typed handoffs |
| Flow manager + delegated crews | CrewAI | Sanctum route manager + controlled organ groups |
| Typed async agent network | AutoGen | Typed message bus + observability |
| Agent-as-tool + concurrency control | AutoGen | Side-effect locks and max route budgets |
| CLI visual comfort | Owner requirement | Colored readable CLI presentation layer, never fake green |

## Что не берём

- Внешний framework как host.
- Free agent chatter.
- Runtime output как canon.
- Parallel stateful agent calls by default.
- Unverified tool execution.
- Any dependency without Owner approval and evidence.

## Как это усиливает Administratum-Agent V1

Administratum должен стать не просто архивом, а первым маршрутизатором правды:

1. Принимать typed task/artifact envelopes.
2. Классифицировать repo zones.
3. Строить inventory/provenance.
4. Писать checkpoints and receipts.
5. Отличать architecture files от runtime.
6. Давать route recommendations другим органам.
7. Готовить merge preparation summary, но не сливать сам.
8. Поддерживать красивый CLI: цветные секции, таблицы, статусы, короткие summaries.
9. Никогда не превращать красивый CLI в fake green.

## Что это значит для следующей задачи

Можно дать Servitor задачу на реализацию Administratum-Agent V1 по PDF, но добавить требование: учитывать этот harvest pack как advisory pattern input. Servitor не должен устанавливать внешние фреймворки. Он должен реализовать собственные IMPERIUM contracts, используя эти паттерны как ориентиры.
