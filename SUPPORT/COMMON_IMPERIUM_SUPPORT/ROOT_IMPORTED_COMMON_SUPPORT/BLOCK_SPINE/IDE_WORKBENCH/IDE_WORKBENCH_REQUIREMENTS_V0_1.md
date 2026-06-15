# IDE_WORKBENCH_REQUIREMENTS_V0_1

Status: CANDIDATE_NOT_CANON
Owner organ: MECHANICUS
Support organs: STRATEGIUM, OFFICIO_AGENTIS, INQUISITION, ASTRONOMICON

## Scope

Design contracts only. No desktop app build. No runtime API integration.

## Core workbench concepts

- Central interactive chamber for task execution visibility.
- Left block and repository explorer.
- Right tool and API arsenal panel.
- Launch card surface for PC, VM2, VM3 contours.
- Visible workbench mode for transparent execution.
- Fog backend mode for background operations with explicit receipts.

## Required technical candidates

- Frontend candidate: TypeScript + React.
- Desktop shell primary candidate: Tauri + Rust.
- Desktop shell fallback candidate: Electron.

## Required governance contracts

- Tool chamber surface contract.
- Resource governor requirements.
- Visible and fog mode contract.
- Local validator offload policy for compile, lint, and type checks.
- Candidate-only adapter cards for future tool integrations.

## Forbidden in this stage

- IDE implementation.
- Browser automation runtime implementation.
- AdsPower runtime integration.
- External API key usage.
