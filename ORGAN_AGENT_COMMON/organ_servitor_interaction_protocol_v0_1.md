# ORGAN <-> SERVITOR INTERACTION PROTOCOL V0.1

## Scope

Wave 1 protocol for:
- `DOCTRINARIUM`
- `OFFICIO_AGENTIS`
- `MECHANICUS`
- `ADMINISTRATUM`

## Request Contract

Servitor sends:
- `task_id`
- `organ_id`
- `question`
- optional `mode` (`SERVITOR_QUERY` default)

## Response Contract

Organ must return `newgen_organ_verdict_v0_1` payload with:
- `verdict`
- `applied_rules`
- `required_actions`
- `forbidden_actions`
- `evidence_required`
- `not_proven`
- `evidence_refs`
- optional `owner_question`

## Verdict Semantics

- `PASS`: safe to continue in current scope.
- `WARN`: continue allowed but risk/attention required.
- `BLOCK`: stop until required actions/evidence complete.
- `OWNER_VERDICT_NEEDED`: stop and wait for Owner answer.

## Owner-Verdict Escalation

When `OWNER_VERDICT_NEEDED` is returned:
1. include reason and question for Owner (RU);
2. include allowed answers (`approve|reject|revise_scope|pause`);
3. mark execution blocked until answer.

## Evidence Discipline

Every critical response must include:
- at least one `evidence_required` item;
- one or more `evidence_refs` paths where possible.

## Smoke Contract

Each organ must support:
- query script sample call;
- TUI `--smoke` call;
- machine-readable mode (`--plain-json`).
