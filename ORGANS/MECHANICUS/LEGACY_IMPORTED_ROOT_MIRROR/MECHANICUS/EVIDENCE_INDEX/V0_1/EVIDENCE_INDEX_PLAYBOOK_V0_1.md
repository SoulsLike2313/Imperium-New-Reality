# EVIDENCE INDEX PLAYBOOK V0.1

## Purpose
Provide a repeatable way to rebuild and query NewGen evidence index artifacts.

## Build
```powershell
python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_evidence_index_builder_v0_1.py `
  --repo-root E:\IMPERIUM `
  --output-root IMPERIUM_NEW_GENERATION/MECHANICUS/EVIDENCE_INDEX/V0_1 `
  --report-root IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-EVIDENCE-INDEX-FOUNDATION-PC-V0_1
```

## Query Smoke
```powershell
python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_evidence_query_runner_v0_1.py `
  --repo-root E:\IMPERIUM `
  --output-root IMPERIUM_NEW_GENERATION/MECHANICUS/EVIDENCE_INDEX/V0_1 `
  --report-root IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-EVIDENCE-INDEX-FOUNDATION-PC-V0_1
```

## Checker
```powershell
python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_mechanicus_evidence_index_v0_1.py `
  --repo-root E:\IMPERIUM `
  --output-root IMPERIUM_NEW_GENERATION/MECHANICUS/EVIDENCE_INDEX/V0_1 `
  --report-root IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-EVIDENCE-INDEX-FOUNDATION-PC-V0_1 `
  --py-compile-status PASS `
  --ruff-status PASS `
  --mypy-status WARN `
  --json-parse-status PASS `
  --query-smoke-status PASS
```

## Guardrails
- Index only `IMPERIUM_NEW_GENERATION` scoped files from this task contract.
- Never include private/local external context paths.
- Keep reports compact (`raw_dump_status=COMPACT_ONLY`).
- Use report receipts for PASS claims.
