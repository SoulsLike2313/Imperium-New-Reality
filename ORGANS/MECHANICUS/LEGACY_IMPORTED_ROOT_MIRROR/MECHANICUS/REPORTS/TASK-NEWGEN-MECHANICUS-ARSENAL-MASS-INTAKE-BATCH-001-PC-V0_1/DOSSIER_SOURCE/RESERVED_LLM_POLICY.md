# Reserved LLM / Cloud Adapter Policy

This task must not deeply integrate LOCAL_LLM or CLOUD_LLM_ADAPTERS.

Allowed:
- create reserved/candidate cards;
- create prompt patterns and future policy requirements;
- record Owner questions.

Forbidden:
- install local model runners;
- configure cloud API routes;
- touch secrets/API keys;
- claim cloud adapters are CANON;
- claim local LLMs are usable without validation.

Required labels:
- RESERVED
- CANDIDATE_ONLY
- FUTURE_DEDICATED_TASK_REQUIRED

Future promotion requires:
- secret policy;
- privacy policy;
- cost policy;
- route policy;
- receipt model;
- Owner approval gate.
