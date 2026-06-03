# TOOL CAPABILITY MAP

- task_id: TASK-20260519-MECHANICUS-OSS-ARSENAL-ADMISSION-VM2-V0_1
- generated_at_utc: 2026-05-19T22:06:55.325025Z
- owner_organ: MECHANICUS_AGENT
- policy: no random installs; admission by evidence only.

## git
- owner: ADMINISTRATUM_AGENT
- consumers: ALL
- status: AVAILABLE_BOTH (pc=AVAILABLE_PC, vm2=AVAILABLE_VM2)
- purpose: repository state, diffs, commits, push/pull, provenance
- command: git --version

## ripgrep
- owner: INQUISITION_AGENT
- consumers: INQUISITION_AGENT, MECHANICUS_AGENT, ADMINISTRATUM_AGENT, SERVITOR
- status: AVAILABLE_BOTH (pc=AVAILABLE_PC, vm2=AVAILABLE_VM2)
- purpose: fast repo search, scope checks, forbidden-pattern detection
- command: rg --version

## ruff
- owner: MECHANICUS_AGENT
- consumers: MECHANICUS_AGENT, SERVITOR
- status: AVAILABLE_VM2 (pc=NOT_FOUND_ON_PC, vm2=AVAILABLE_VM2)
- purpose: Python linting and formatting checks
- command: ruff --version

## pytest
- owner: MECHANICUS_AGENT
- consumers: MECHANICUS_AGENT, SCHOLA_IMPERIALIS_AGENT, SERVITOR
- status: AVAILABLE_PC (pc=AVAILABLE_PC, vm2=NOT_FOUND_ON_VM2)
- purpose: Python tests and regression suite
- command: python3 -m pytest --version

## jsonschema
- owner: DOCTRINARIUM_AGENT
- consumers: DOCTRINARIUM_AGENT, OFFICIO_AGENTIS_AGENT, MECHANICUS_AGENT
- status: AVAILABLE_VM2 (pc=NOT_FOUND_ON_PC, vm2=AVAILABLE_VM2)
- purpose: validate JSON artifacts, contracts, policies
- command: python3 -m jsonschema --version

## jq
- owner: ADMINISTRATUM_AGENT
- consumers: ADMINISTRATUM_AGENT, MECHANICUS_AGENT, SERVITOR
- status: AVAILABLE_BOTH (pc=AVAILABLE_PC, vm2=AVAILABLE_VM2)
- purpose: inspect and transform JSON on CLI
- command: jq --version

## yq
- owner: ADMINISTRATUM_AGENT
- consumers: ADMINISTRATUM_AGENT, DOCTRINARIUM_AGENT, SERVITOR
- status: AVAILABLE_BOTH (pc=AVAILABLE_PC, vm2=AVAILABLE_VM2)
- purpose: inspect YAML and config files
- command: yq --version

## gitleaks
- owner: INQUISITION_AGENT
- consumers: INQUISITION_AGENT, CUSTODES_LATER, SERVITOR
- status: KNOWN_NOT_INSTALLED (pc=NOT_FOUND_ON_PC, vm2=NOT_FOUND_ON_VM2)
- purpose: detect possible secrets before commit/admission
- command: gitleaks version

## semgrep
- owner: INQUISITION_AGENT
- consumers: INQUISITION_AGENT, MECHANICUS_AGENT, SERVITOR
- status: KNOWN_NOT_INSTALLED (pc=NOT_FOUND_ON_PC, vm2=NOT_FOUND_ON_VM2)
- purpose: static analysis and policy pattern scanning
- command: semgrep --version

## bandit
- owner: INQUISITION_AGENT
- consumers: INQUISITION_AGENT, MECHANICUS_AGENT
- status: KNOWN_NOT_INSTALLED (pc=NOT_FOUND_ON_PC, vm2=NOT_FOUND_ON_VM2)
- purpose: Python security lint checks
- command: bandit --version

## pip-audit
- owner: INQUISITION_AGENT
- consumers: INQUISITION_AGENT, MECHANICUS_AGENT
- status: AVAILABLE_PC (pc=AVAILABLE_PC, vm2=NOT_FOUND_ON_VM2)
- purpose: Python dependency vulnerability audit
- command: pip-audit --version

## uv
- owner: MECHANICUS_AGENT
- consumers: MECHANICUS_AGENT, SERVITOR
- status: AVAILABLE_BOTH (pc=AVAILABLE_PC, vm2=AVAILABLE_VM2)
- purpose: Python package/project environment management
- command: uv --version

## duckdb
- owner: ADMINISTRATUM_AGENT
- consumers: ADMINISTRATUM_AGENT, STRATEGIUM_AGENT, SCHOLA_IMPERIALIS_AGENT
- status: KNOWN_NOT_INSTALLED (pc=NOT_FOUND_ON_PC, vm2=NOT_FOUND_ON_VM2)
- purpose: query reports, ledgers, CSV/JSON data
- command: duckdb --version

## playwright
- owner: MECHANICUS_AGENT
- consumers: SANCTUM_LATER, INQUISITION_AGENT, SERVITOR
- status: KNOWN_NOT_INSTALLED (pc=NOT_FOUND_ON_PC, vm2=NOT_FOUND_ON_VM2)
- purpose: browser UI checks, screenshots, trace evidence
- command: npx --no-install playwright --version

## node
- owner: MECHANICUS_AGENT
- consumers: MECHANICUS_AGENT, SANCTUM_LATER
- status: AVAILABLE_BOTH (pc=AVAILABLE_PC, vm2=AVAILABLE_VM2)
- purpose: support frontend tooling and JS-based checks
- command: node --version

## npm
- owner: MECHANICUS_AGENT
- consumers: MECHANICUS_AGENT, SANCTUM_LATER
- status: AVAILABLE_BOTH (pc=AVAILABLE_PC, vm2=AVAILABLE_VM2)
- purpose: support frontend package scripts when admitted
- command: npm --version
