# Validation Policy V0.1

## No uncontrolled install

This task may detect installed tools and validate internal capabilities.

It must not install new tools unless Owner explicitly grants approval during the task.

## Safe validation commands

Allowed by default:

- version checks;
- Python import checks;
- read-only repository checks;
- JSON parse/schema checks;
- temp in-memory SQLite/FTS check;
- py_compile on selected Mechanicus scripts.

Forbidden without Owner approval:

- network install;
- package manager install;
- browser install;
- cloud/API use;
- secret access;
- broad filesystem scan outside NewGen;
- mutating commands outside report/receipt outputs.

## Promotion rules

- CANDIDATE can remain candidate.
- CANDIDATE can become SANDBOX after local validation receipt.
- SANDBOX can become CANON only with strong evidence and bounded usage contract.
- Missing tool remains candidate and gets Owner question.
- LLM/cloud remains reserved/candidate-only.
