# Симуляция взаимодействия Servitor с органами (Wave 1)

Task: `TASK-20260524-NEWGEN-CORE-ORGAN-FORM-TUI-WAVE1-VM3-V0_1`

## 1. Doctrinarium

Вопрос Servitor: «Какие законы и гейты применяются к этой задаче?»

Ответ органа:
- verdict: `PASS`
- применены read-first/evidence/no-generic-pass границы
- обязательные действия: preflight до правок, scoped verdict
- запреты: overclaim Important Six, production autonomy
- Owner Verdict нужен только если требуется выход за границы Wave 1

## 2. Officio Agentis

Вопрос Servitor: «Какие role/language/response правила обязательны?»

Ответ органа:
- verdict: `PASS`
- применены role-ack/language/scoped-verdict/stop-condition правила
- обязательные действия: role ack до правок, только scoped verdict pattern
- запреты: generic PASS, игнор Owner Verdict Needed
- Owner Verdict нужен при попытке override scope/contract

## 3. Mechanicus

Вопрос Servitor: «Какие инструменты/возможности нужны и в каком они состоянии?»

Ответ органа:
- verdict: `PASS`
- подтверждена обязательная Wave1 capability: `rich`
- зафиксированы registry + receipt пути в `MECHANICUS/TOOLS_REGISTRY`
- запреты: claim visual pass без Rich, uncontrolled install
- Owner Verdict нужен, если Rich нельзя установить/верифицировать

## 4. Administratum

Вопрос Servitor: «Какая регистрация/история/гигиена репозитория обязательна?»

Ответ органа:
- verdict: `PASS`
- применены continuity/evidence-package/hygiene/sequence gates
- обязательные действия: финальный report+closure receipt, проверка clean/sync
- запреты: скрывать грязь, заявлять pass без smoke evidence
- Owner Verdict нужен при попытке scope/sequence исключений

## Итого

Симуляция доказывает, что Servitor может спросить 4 Wave1 органа и получить полезный структурированный ответ с verdict/actions/forbidden/evidence и условиями для Owner Verdict.
