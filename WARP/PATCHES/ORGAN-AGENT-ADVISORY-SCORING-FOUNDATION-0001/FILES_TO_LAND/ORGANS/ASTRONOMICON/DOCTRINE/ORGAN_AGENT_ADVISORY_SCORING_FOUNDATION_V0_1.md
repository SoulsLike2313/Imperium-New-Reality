# ORGAN AGENT ADVISORY SCORING FOUNDATION V0.1

patch_id: `ORGAN-AGENT-ADVISORY-SCORING-FOUNDATION-0001`

## Purpose

Give organs a conversational advisory layer without turning them into uncontrolled agents.

The organ-agent may:

```text
- indicate attention zones;
- show evidence and gaps;
- explain why a zone matters;
- recommend where attention should go next;
- speak in the organ's own profile domain.
```

The organ-agent must not:

```text
- command concrete actions;
- execute;
- mutate files;
- claim trust;
- claim Throne verdict;
- replace Owner intent;
- speak outside its organ profile.
```

## Mathematical basis

Every advisory item must carry a `future_step_success_score` from 0 to 100.

The score is a weighted combination of:

```text
evidence_strength
validator_availability
authority_clarity
scope_clarity
dependency_readiness
reversibility
risk_control
operator_clarity
```

The advisory layer does not say:

```text
do this command
```

It says:

```text
attention zone: <zone>
why: <evidence>
success score: <number>
profile organ: <organ>
```

## Owner law

The user wants talkative organs, but not fake agency.

So the voice may be helpful and explanatory, while the output remains machine-checkable.
