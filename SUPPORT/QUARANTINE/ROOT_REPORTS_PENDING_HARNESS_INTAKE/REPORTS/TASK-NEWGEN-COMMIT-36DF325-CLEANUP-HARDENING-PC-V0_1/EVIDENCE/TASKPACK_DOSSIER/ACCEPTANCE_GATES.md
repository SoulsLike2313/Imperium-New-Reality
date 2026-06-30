# Acceptance gates — TASK-NEWGEN-COMMIT-36DF325-CLEANUP-HARDENING-PC-V0_1

## PASS gates

PASS is allowed only if all are true:

1. Doctrinarium synthesis files are present in:
   `IMPERIUM_NEW_GENERATION/DOCTRINARIUM/DOCTRINES/`
2. Servitor read-first compliance is recorded in the final report.
3. `36df325` artifacts are classified into KEEP / QUARANTINE / DELETE / REWRITE_REQUIRED / UNKNOWN.
4. Runtime junk is removed from tracked source where safe.
5. Generated evidence burst is quarantined or explicitly justified as curated evidence.
6. No backend/action source seed is destroyed.
7. No cockpit visual rewrite is attempted.
8. No Mechanicus Arsenal foundation is started.
9. Hygiene report exists and names any remaining runtime/generated tracked artifacts.
10. Work is committed and pushed.
11. Final Owner-facing response is in Russian and uses the 4-part Servitor form.

## WARN gates

WARN is required if:

- some generated artifacts remain because they are curated final evidence;
- some unknown files require later Owner/Speculum review;
- any checker could not be run due to missing local dependencies;
- git tree is clean after commit but a non-blocking hygiene warning remains.

## BLOCKED gates

BLOCKED is required if:

- repository HEAD is not safe to build on;
- unrelated dirty files exist before work and cannot be isolated;
- cleanup would require deleting source files without clear evidence;
- required reports cannot be written;
- push fails.
