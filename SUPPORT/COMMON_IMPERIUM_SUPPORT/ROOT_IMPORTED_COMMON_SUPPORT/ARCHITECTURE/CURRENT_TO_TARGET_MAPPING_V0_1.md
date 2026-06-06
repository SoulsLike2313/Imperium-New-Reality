# Current-to-Target Mapping V0.1

## Scope
This mapping is advisory for staged migration planning.
No physical migration is performed in this task.

## Mapping table

| Current root | Target zone | Target path candidate | Rationale | Migration risk |
|---|---|---|---|---|
| `SANCTUM_MINI/` | apps | `apps/sanctum-shell/` | runnable shell-like app surface | medium |
| `SANCTUM_VISUAL_FOUNDRY/` | apps + packages + evidence | `apps/visual-foundry-labs/`, `packages/*`, `evidence/*` | mixes UI assets, contracts, screenshots, reports | high |
| `COMMON_AGENT_CLI/` | apps + services | `apps/organ-panels/`, `services/task-registry/` | includes UI shell, policy, and runtime helpers | medium |
| `ORGAN_AGENTS/` | organs | `organs/*` | domain ownership already explicit by organ | low |
| `EXCHANGE/` | services | `services/organ-adapters/` + `services/api-gateway/` | bus and route session data transport | medium |
| `INTAKE/` | services | `services/task-registry/` | normalized intake data | low |
| `LEDGER/` | services + evidence | `services/truth-state-service/` and `evidence/audits/` | contains operational state and ledger history | medium |
| `PROTOCOLS/` | contracts | `contracts/api/`, `contracts/events/`, `contracts/schemas/` | protocol law and machine schemas | low |
| `CORE/` | contracts | `contracts/role-acks/`, `contracts/taskpacks/` | scope and write policy contracts | low |
| `TASK_CONTROL/` | contracts + services | `contracts/taskpacks/` and `services/task-registry/` | control protocol plus execution routing semantics | medium |
| `REPORTS/` | evidence | `evidence/audits/` | large archive of report artifacts | medium |
| `RECEIPTS/` | evidence | `evidence/receipts/` | receipt-only artifacts | low |
| `STRESS_TESTS/` | evidence | `evidence/audits/` | stress outputs and proof data | low |
| `TOOLS/` | tools | `tools/validators/`, `tools/builders/`, `tools/inspectors/` | reusable scripts and helper tooling | low |
| `TASKS/` | runtime/tasks | `tasks/assigned/`, `tasks/completed/`, `tasks/blocked/` | work orchestration queue/history | low |
| `RUNS/` | runtime | `runtime/ignored-runs/` | mutable operational output | low |
| `ARCHIVE/` | runtime/evidence | `runtime/ignored-runs/` + `evidence/audits/` | permanent archive payload; needs retention policy | medium |
| `RESEARCH/` | architecture/contracts | `architecture/decisions/` + `contracts/taskpacks/` | research outputs used for future decisions | low |
| `AGENT_DIRECTIVES/` | architecture/contracts | `architecture/decisions/` + `contracts/role-acks/` | strategic directives and normative guidance | low |

## Staged migration strategy (future)
1. Classify folders by canonical source vs generated/runtime evidence.
2. Move contracts first (least behavioral risk).
3. Extract shared packages from visual assets.
4. Split app surfaces from service orchestration.
5. Normalize evidence paths and retention policy.

## Explicit non-claim
This file does not claim migration completion.
It is a map for future bounded migration tasks.

