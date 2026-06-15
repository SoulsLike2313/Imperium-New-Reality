# Task Spec - Language Authority and Mojibake Filter Spinoff

Task ID: `TASK-NEWGEN-LANGUAGE-AUTHORITY-AND-MOJIBAKE-FILTER-SPINOFF-PC-V0_1`

## Background

The Stage3.1 bootstrap hardening task fixed Astronomicon bootstrap issues and made the entry path more reliable. It also exposed a separate system risk: language and encoding contamination.

Mixed-language internal task files and ad hoc owner-facing text can produce mojibake and confuse agents, validators, document viewers, and future automation. This spinoff makes language behavior explicit and enforceable.

## Goal

Create a system-level language and encoding guardrail:

1. Officio Agentis owns runtime owner-facing language behavior.
2. Inquisition owns a global mojibake and encoding filter.
3. Astronomicon intake rejects or warns on taskpack language and encoding violations.
4. Canonical internal artifacts remain English-only and UTF-8 without BOM.
5. Russian is allowed only as runtime owner-facing output authorized by Officio, or later as controlled localization resources.

## Prime language rule

All files created by this task in the canonical repository must be English-only and UTF-8 without BOM, except explicitly Officio-authorized runtime owner-facing summaries.

Forbidden in canonical internal artifacts:
- Cyrillic characters;
- UTF-8 BOM;
- mojibake signatures;
- replacement character;
- mixed encoding artifacts;
- ad hoc Russian prose inside taskpacks, reports, policies, contracts, schemas, logs, receipts, or registries.

Allowed exceptions:
- explicit localization resources in named localization folders;
- PDF attachments if they are already present and are not parsed as canonical machine-readable text;
- runtime chat responses authorized by Officio Agentis.

## Required implementation A - Officio language authority

Add or update Officio policy files, for example:

`IMPERIUM_NEW_GENERATION/ORGANS/OFFICIO_AGENTIS/POLICIES/OFFICIO_LANGUAGE_AUTHORITY_V0_1.md`

and machine-readable contract:

`IMPERIUM_NEW_GENERATION/ORGANS/OFFICIO_AGENTIS/POLICIES/OFFICIO_LANGUAGE_AUTHORITY_V0_1.json`

They must state:
- canonical taskpacks and machine artifacts are English-only;
- JSON/MD/TXT/PY/PS1/YAML canonical artifacts must be UTF-8 without BOM;
- runtime owner-facing Russian is allowed only through Officio role settings;
- Servitor live progress may be Russian only as runtime owner-facing communication;
- internal taskpacks must not store Russian owner prose;
- future Russian UI text must live in controlled localization resources, not mixed into canonical records.

## Required implementation B - Inquisition global mojibake filter

Add:

`IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/TOOLS/inquisition_mojibake_filter_v0_1.py`

It must scan selected canonical repo paths for:
- Cyrillic characters in English-only canonical artifacts;
- UTF-8 BOM in JSON, MD, TXT, PY, PS1, YAML, YML, CSV files;
- named mojibake and encoding-corruption signatures;
- replacement character by code point;
- suspicious mixed encoding patterns;
- internal taskpack files that violate English-only policy.

It must output:
- JSON report;
- Markdown summary;
- PASS/WARN/BLOCK verdict;
- path, line, hit type, severity, owning organ where possible.

Default scan scope:
- `AGENTS.md`
- `IMPERIUM_NEW_GENERATION/ORGANS/**`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/**`
- `IMPERIUM_NEW_GENERATION/CONTEXT_SPINE/**` if present
- Astronomicon registered task/report directories
- Administratum reports related to current stage

Safe exclusions:
- PDF files;
- binary files;
- explicit localization resources with folder names such as `locales`, `i18n`, `translations`, `LOCALIZATION`;
- private or local runtime paths outside canonical repo scope.

## Required implementation C - Astronomicon admission language gate

Add or update Astronomicon intake/preflight behavior so taskpack admission can detect:
- UTF-8 BOM in required root files;
- Cyrillic in internal root files;
- mojibake signatures;
- missing language policy fields in MANIFEST.

This can be implemented directly in Astronomicon tools or by calling the Inquisition filter in taskpack mode.

Required artifacts:
- taskpack language gate receipt;
- fixture cases;
- report showing this taskpack passes the gate.

## Required implementation D - Matrix Spine updates

Add or update matrices for:
- `LANGUAGE_AUTHORITY_MATRIX`
- `ENCODING_INTEGRITY_MATRIX`
- `MOJIBAKE_DETECTION_MATRIX`
- `TASKPACK_LANGUAGE_ADMISSION_MATRIX`

Each criterion must include:
- criterion id;
- owner organ;
- evidence required;
- PASS/WARN/BLOCK logic;
- cap mapping;
- remediation path.

## Required implementation E - Fixtures

Required fixture cases:
1. clean English-only canonical file -> PASS;
2. Cyrillic in canonical markdown -> BLOCK;
3. UTF-8 BOM JSON -> BLOCK;
4. replacement character by code point -> BLOCK;
5. named mojibake signature -> BLOCK;
6. controlled localization resource -> PASS or WARN according to policy;
7. binary/PDF ignored -> PASS with exclusion note;
8. Officio-authorized runtime owner-facing summary -> WARN or PASS according to metadata;
9. taskpack root file with Cyrillic -> BLOCK;
10. taskpack root file with UTF-8 BOM -> BLOCK.

## Required implementation F - Reports and receipts

Recommended report root:

`IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/REPORTS/TASK-NEWGEN-LANGUAGE-AUTHORITY-AND-MOJIBAKE-FILTER-SPINOFF-PC-V0_1/`

Required:
- `ghost_evolve_entry_ack.json`
- `repo_truth_probe.json`
- `officio_language_authority_report.md`
- `officio_language_authority_receipt.json`
- `inquisition_mojibake_filter_report.md`
- `inquisition_mojibake_filter_report.json`
- `taskpack_language_gate_report.md`
- `taskpack_language_gate_receipt.json`
- `language_encoding_fixture_report.md`
- `language_encoding_fixture_results.json`
- `matrix_language_encoding_update_report.md`
- `canonical_artifact_language_scan_report.md`
- `GHOST_EVOLVE_LANGUAGE_ENCODING_LEARNING_BACKLOG.json`
- `GHOST_EVOLVE_LANGUAGE_ENCODING_LEARNING_BACKLOG.md`
- `NEXT_PIPELINE_HANDOFF.json`
- `efficiency_delta_receipt.json`
- `hard_red_team_verdict.json`
- `claim_ledger.jsonl`
- `capability_split_receipt.json`
- `final_owner_summary_ru.md`
- `commit_push_receipt.json`

Note:
`final_owner_summary_ru.md` is allowed only as Officio-authorized runtime owner-facing output. If created, it must carry metadata showing it is not machine policy and not taskpack instruction.

## Required closure behavior

PC Servitor must commit and push admitted canonical changes.

A final report must not end with:
- `PENDING_COMMIT`;
- `PENDING_PUSH_URL`;
- `PENDING_FINAL_GIT_CHECK`.

If changes are not admitted, Servitor must rollback or quarantine them with receipt, or stop with `BLOCKED_PENDING_OWNER_DECISION`.

## Allowed verdicts

- `LANGUAGE_AUTHORITY_FILTER_PASS_WITH_WARNINGS`
- `LANGUAGE_AUTHORITY_FILTER_PARTIAL`
- `LANGUAGE_AUTHORITY_FILTER_BLOCKED`

Clean PASS is forbidden until independent Inquisitor and Speculum review accepts the spinoff.

## Forbidden

No visual IDE.
No WARP activation.
No second micro-pilot.
No freelance or trading execution.
No broad unrelated refactor.
No private or secret scanning outside canonical safe scope.
No rewriting history.
No deleting existing evidence without receipt.
