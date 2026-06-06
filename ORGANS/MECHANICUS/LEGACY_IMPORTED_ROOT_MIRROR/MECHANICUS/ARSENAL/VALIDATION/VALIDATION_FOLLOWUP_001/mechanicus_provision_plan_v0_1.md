# Mechanicus Provision Plan V0.1

Task: `TASK-NEWGEN-MECHANICUS-ARSENAL-VALIDATION-FOLLOWUP-PC-V0_1`
Policy: detection-first, Owner-gated provisioning, receipt-backed promotion.

## Missing tools requiring Owner gate

| Capability | Tool | Proposed command | Risk | Notes |
|---|---|---|---|---|
| CAP-TOOL-JSONSCHEMA | jsonschema | `python -m pip install jsonschema` | MEDIUM | JSON schema validation for receipts/cards/registries. |
| CODE_QUALITY_JSONSCHEMA | jsonschema | `python -m pip install jsonschema` | MEDIUM | Code quality schema-first validation dependency. |
| CAP-CQ-RUFF | ruff | `python -m pip install ruff` | MEDIUM | Fast linter/formatter candidate. |
| CODE_QUALITY_RUFF | ruff | `python -m pip install ruff` | MEDIUM | Code-quality linting lane. |
| CAP-CQ-PYRIGHT-MYPY | mypy_or_pyright | `Owner decision required: mypy (pip) vs pyright (npm/npx) route` | HIGH | Explicit Owner path decision required for type checker route. |
| CODE_QUALITY_MYPY | mypy | `python -m pip install mypy` | MEDIUM | Python static type checker. |
| CODE_QUALITY_PYRIGHT | pyright | `npm install -g pyright OR approved local npm/npx path` | HIGH | Owner should explicitly choose npm/npx provisioning path. |
| CAP-CQ-PRECOMMIT | pre-commit | `python -m pip install pre-commit` | MEDIUM | Hook runner; do not auto-enable hooks. |
| CODE_QUALITY_PRE_COMMIT | pre-commit | `python -m pip install pre-commit` | MEDIUM | Code quality hook tool card. |
| UI_FRAMEWORKS_REACT | react | `npm install react (in bounded project scope only after Owner approval)` | HIGH | No React project/prototype creation in this task. |
| UI_FRAMEWORKS_VITE | vite | `npm install -g vite OR project-local vite only after Owner approval` | HIGH | No npx vite execution in detection-only phase. |

## Present tools validated in this task

| Capability | Tool | Validation verdict | Promotion recommendation |
|---|---|---|---|
| CAP-TOOL-NODE-NPM-NPX | node_npm | PASS | PROMOTE_SANDBOX |
| CAP-VIS-PLAYWRIGHT-REGRESSION | playwright | PASS | KEEP_CANDIDATE_READINESS_ONLY |
| VISUAL_TESTING_PLAYWRIGHT | playwright | PASS | KEEP_CANDIDATE_READINESS_ONLY |

## Guardrails

- No silent installs.
- No `npm install` / `pip install` / networked `npx` without Owner approval.
- No Playwright browser install without explicit approval.
- No visual prototypes and no LLM/cloud activation in this step.
