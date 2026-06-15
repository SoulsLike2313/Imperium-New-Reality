# Acceptance Gates

## Admission gates

- Task starts from registered Astronomicon taskpack.
- Servitor enters role through OFFICIO_AGENTIS before mutation.
- Officio role entry receipt exists.
- Owner-facing final summary is Russian after Officio role entry.
- Machine artifacts are English UTF8 NO_BOM.
- No Ancient Empire active runtime access.

## Build gates

- Administratum post-work bundle contract exists.
- Bundle manifest schema exists.
- Organ post-work receipt schema exists.
- Bundle index card schema exists.
- Administratum post-work bundle checker exists and is runnable.
- Post-work organ ring contract exists.
- Required nine organs file exists.
- Organ receipt template exists.
- Report directory exists.

## Bundle gates

- The system can take a task_id and locate registered taskpack evidence.
- The system can index taskpack, route manifest, reports, receipts, changed files, local artifacts, git proof, and next task route.
- GitHub-safe index is separated from local heavy bundle storage.
- Missing required organ receipts must block or be marked NOT_YET_IMPLEMENTED with reason and next route.
- No PASS if Administratum bundle receipt is missing.
- No PASS if Inquisition contradiction scan is missing or explicitly out of scope without a blocker.
- No PASS if remote proof is missing after commit/push.

## Enhanced Ghost Evolve gates

- Schola receipt explains what organs learned.
- Mechanicus receipt explains new or changed tools.
- Administratum receipt explains what bundle knowledge was internalized.
- At least one reusable contract, schema, template, or checker is created for future tasks.
- Final answer must not be the only place where new rules exist.

## Closure gates

- JSON validates.
- Python checker runs or limitation is documented with exact command and reason.
- git status is explained.
- Commit is created for accepted repo changes.
- Normal non-force push is performed.
- Local HEAD equals origin/master after push.
- Final owner summary is Russian and includes path to primary report/bundle index.
