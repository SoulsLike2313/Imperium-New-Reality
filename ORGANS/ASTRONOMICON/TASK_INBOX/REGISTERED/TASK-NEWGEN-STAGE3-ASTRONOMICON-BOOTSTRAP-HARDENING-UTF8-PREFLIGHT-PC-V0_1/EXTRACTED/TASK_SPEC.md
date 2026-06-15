# Task Spec — Astronomicon Bootstrap Hardening UTF-8 Preflight

Task ID: `TASK-NEWGEN-STAGE3-ASTRONOMICON-BOOTSTRAP-HARDENING-UTF8-PREFLIGHT-PC-V0_1`

## Background

Stage3 first real-use micro-pilot succeeded at commit `9b421cabc2cf781a47bf90d31c233fe96e6d8fbd`.

But Stage3 required manual bootstrap repair before Astronomicon intake could register the taskpack:
- route manifest template was missing;
- start ACK template was missing or unproven;
- PowerShell UTF-8 template contained BOM;
- Python JSON read failed with `Unexpected UTF-8 BOM`;
- owner-facing launcher search confused fixture runners with launchers;
- Stage3 bundle had PENDING/finalization fields that require follow-up semantics.

## Goal

Make Astronomicon intake self-checking and Owner-usable before the second micro-pilot.

## Required implementation

### A. Bootstrap preflight tool

Add:

`IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TOOLS/astronomicon_bootstrap_preflight_v0_1.py`

Must check:
- route manifest template exists;
- start ACK template exists;
- both are UTF-8 without BOM;
- both parse as JSON with normal `utf-8`;
- route template has all 8 required organs and read_order;
- start ACK template has required fields;
- emits JSON receipt with PASS/WARN/BLOCK.

### B. Bootstrap repair/helper

Add:

`IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TOOLS/astronomicon_bootstrap_repair_v0_1.py`

Must create missing templates and rewrite templates as UTF-8 no-BOM. Must preserve before hash when rewriting. Do not overwrite without `--force` unless missing.

### C. Owner-facing launcher

Add:

`IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/LAUNCHERS/launch_astronomicon_task_entry_v0_1.ps1`

and/or:

`IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TOOLS/astronomicon_owner_launcher_v0_1.py`

Must run bootstrap preflight before intake/TUI, must not auto-pick fixture runners, and must tell Owner how to repair if preflight blocks.

### D. Fixtures

Add:

`IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TOOLS/run_astronomicon_bootstrap_preflight_fixtures_v0_1.py`

Required cases:
1. missing route template -> BLOCK;
2. missing start ack template -> BLOCK;
3. route template UTF-8 BOM -> BLOCK with explicit BOM cap;
4. invalid JSON -> BLOCK;
5. route missing one organ -> BLOCK;
6. valid template pair -> PASS/PASS_WITH_WARNINGS;
7. repair missing files -> creates no-BOM templates;
8. repair BOM file with force -> rewrites no-BOM and records before hash.

### E. Stage3 pending/finalization cleanup

Scan Stage3 report bundle for `PENDING_COMMIT`, `PENDING_PUSH_URL`, `PENDING_FINAL_GIT_CHECK`, or equivalent unresolved finalization fields.

If present, create a follow-up clarification artifact:
- do not rewrite history;
- identify `9b421cabc2cf781a47bf90d31c233fe96e6d8fbd` as subject Stage3 commit;
- current task/finalization commit is follow-up closure;
- produce `stage3_followup_finalization_receipt.json`.

If none found, produce scan report.

## Required reports

Recommended root:

`IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/REPORTS/TASK-NEWGEN-STAGE3-ASTRONOMICON-BOOTSTRAP-HARDENING-UTF8-PREFLIGHT-PC-V0_1/`

Required:
- `ghost_evolve_entry_ack.json`
- `repo_truth_probe.json`
- `astronomicon_bootstrap_preflight_report.md`
- `astronomicon_bootstrap_preflight_receipt.json`
- `astronomicon_bootstrap_repair_receipt.json`
- `bootstrap_fixture_report.md`
- `bootstrap_fixture_results.json`
- `owner_launcher_report.md`
- `stage3_pending_field_scan_report.md`
- `stage3_followup_finalization_receipt.json`
- `GHOST_EVOLVE_STAGE3_1_LEARNING_BACKLOG.json`
- `GHOST_EVOLVE_STAGE3_1_LEARNING_BACKLOG.md`
- `NEXT_PIPELINE_HANDOFF.json`
- `efficiency_delta_receipt.json`
- `hard_red_team_verdict.json`
- `claim_ledger.jsonl`
- `capability_split_receipt.json`
- `final_owner_summary_ru.md`
- `commit_push_receipt.json`

## Allowed verdicts

- `BOOTSTRAP_HARDENING_PASS_WITH_WARNINGS`
- `BOOTSTRAP_HARDENING_PARTIAL`
- `BOOTSTRAP_HARDENING_BLOCKED`

Clean PASS is forbidden until independent review accepts this follow-up.

## Forbidden

No visual IDE, WARP activation, second micro-pilot, freelance/trading execution, broad unrelated rewrites, mass legacy receipt migration, private/secrets, Throne/Custodes scope.
