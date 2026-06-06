# OSS Admission Report V0.1

## Purpose
- Record OSS candidate status for Administratum without installation or vendoring.
- Enforce detect-only policy and explicit admission lifecycle.

## Policy result
- `oss_auto_install_performed`: `false`
- `detection_only`: `true`
- `vendoring_performed`: `false`

## Candidate status snapshot
| tool_id | purpose | status | detected_availability | fallback |
|---|---|---|---|---|
| `rich` | terminal panels and tables | `admitted_if_available` | available | stdlib renderer |
| `jsonschema` | schema validation | `candidate_for_admission` | unavailable | `python -m json.tool` parse-level checks |
| `reportlab` | direct Python PDF generation | `candidate_for_pdf_backend` | unavailable | browser headless print-to-pdf |
| `weasyprint` | HTML/CSS to PDF | `sandbox_candidate_due_to_weight` | unavailable | browser headless print-to-pdf |
| `pillow` | evidence/image helpers | `candidate_for_evidence_helpers` | available | no image processing path |
| `pytest` | regression tests | `candidate_for_test_gate` | available | direct command smoke tests |
| `ruff` | lint/static checks | `future_candidate` | unavailable | no lint gate in this slice |
| `playwright` | browser screenshots/tests | `future_heavy_adapter` | available | no mandatory browser capture |
| `duckdb` | analytics/indexing | `future_candidate` | unavailable | stdlib/json index path |
| `sqlite3` | local index | `stdlib_allowed` | available | n/a |

## PDF backend detection
- Browser backend used for Owner PDF:
  - preferred: `edge_headless`
  - fallback: `chrome_headless`
- Environment detection in this run found local browser backend available.

## Risks
- `reportlab` and `weasyprint` unavailable in current environment.
- Heavy tools (`playwright`, `duckdb`) are not part of core admission for this task.

## Admission verdict
- `WARN` (non-blocking unavailable optional candidates).
- Dossier flow remains operational with available backend fallback path.

