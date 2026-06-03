# NEWGEN Architecture Map V0.1

## Task context
- Task: `TASK-20260521-NEWGEN-ARCHITECTURE-SKILL-SPINE-PC-V0_1`
- Scope: architecture and skill spine foundation only
- Non-goal: no full migration, no broad refactor, no runtime claims

## Current bounded reality
`IMPERIUM_NEW_GENERATION` already contains strong domain assets (organ agents, visual foundry, reports, protocols), but structure is history-heavy and mixes:
- canonical source and historical reports;
- runtime-like archives and active topology;
- contracts and implementation assets.

This map defines a stable target architecture language for future staged migration.

## Target architecture zones

### 1) Apps
Purpose: executable entry surfaces and user/operator interaction shells.
Planned roots:
- `apps/sanctum-shell/`
- `apps/organ-panels/`
- `apps/visual-foundry-labs/`

Current candidates:
- `SANCTUM_MINI/`
- `SANCTUM_VISUAL_FOUNDRY/`
- `COMMON_AGENT_CLI/`

### 2) Organs (domain modules)
Purpose: organ-bound domain logic, role contracts, operating rules, and manifests.
Planned root:
- `organs/`

Current candidate:
- `ORGAN_AGENTS/`

### 3) Packages (shared frontend systems)
Purpose: shared token, primitive, widget, and motion packages decoupled from apps.
Planned roots:
- `packages/visual-tokens/`
- `packages/ui-primitives/`
- `packages/imperium-widgets/`
- `packages/motion-system/`
- `packages/truth-components/`

Current candidates:
- `SANCTUM_VISUAL_FOUNDRY/TOKENS/`
- `SANCTUM_VISUAL_FOUNDRY/TEXTURES/`
- `SANCTUM_VISUAL_FOUNDRY/MOTION/`
- `SANCTUM_VISUAL_FOUNDRY/COMPONENTS/`

### 4) Services (backend/API/adapters)
Purpose: routing, registries, bus exchange, adapters, and state services.
Planned roots:
- `services/api-gateway/`
- `services/organ-adapters/`
- `services/task-registry/`
- `services/evidence-registry/`
- `services/truth-state-service/`

Current candidates:
- `EXCHANGE/`
- `INTAKE/`
- `LEDGER/`
- `TOOLS/agent_cli/` (partially service-like orchestration)

### 5) Contracts (schemas and protocol law)
Purpose: machine contracts separated from implementations and reports.
Planned roots:
- `contracts/schemas/`
- `contracts/api/`
- `contracts/events/`
- `contracts/receipts/`
- `contracts/role-acks/`
- `contracts/taskpacks/`

Current candidates:
- `PROTOCOLS/`
- `CORE/`
- `TASK_CONTROL/`
- selected `SCHEMAS/` in organ/app zones

### 6) Evidence (receipts/reports/audits)
Purpose: all proof artifacts, run receipts, screenshots, and post-run reports.
Planned roots:
- `evidence/screenshots/`
- `evidence/playwright/`
- `evidence/receipts/`
- `evidence/audits/`

Current candidates:
- `REPORTS/`
- `RECEIPTS/`
- `STRESS_TESTS/`
- app-local report folders

### 7) Tools (validators/builders/inspectors)
Purpose: reusable tooling for truth checks, validators, and controlled generation.
Planned roots:
- `tools/validators/`
- `tools/builders/`
- `tools/inspectors/`

Current candidates:
- `TOOLS/`
- validator and helper scripts embedded inside organ/app trees

### 8) Runtime and ignored outputs
Purpose: isolate mutable run outputs from canonical source.
Planned roots:
- `runtime/ignored-runs/`
- `tasks/assigned/`
- `tasks/completed/`
- `tasks/blocked/`

Current candidates:
- `RUNS/`
- `TASKS/`
- `ARCHIVE/`
- some report-generated runtime folders

## Ownership and policy baseline
Each target root must carry:
- owner domain;
- purpose statement;
- allowed file types;
- write/read boundaries;
- evidence expectations;
- common failure risks;
- validator coverage status.

## Known unknowns
- Exact cut line between `services/*` and `tools/*` for agent CLI orchestration.
- How much historical `REPORTS/` should be normalized into `evidence/*`.
- Whether visual package extraction should occur before or after organ-level contract normalization.
- Final policy for run output retention horizon and archive compaction.

## Migration stance for this task
No directory migration is executed in this task.
This task defines architecture intent, mapping, contracts, and validation only.

