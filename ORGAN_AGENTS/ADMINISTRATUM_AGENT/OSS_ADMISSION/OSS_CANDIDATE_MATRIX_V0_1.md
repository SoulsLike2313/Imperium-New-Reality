# OSS Candidate Matrix V0.1

| Tool | Purpose | Initial status | Risk | Fallback |
|---|---|---|---|---|
| rich | terminal panels, live status, tables | admitted_if_available | low | stdlib renderer |
| jsonschema | JSON schema validation | candidate_for_admission | low | json parse + key checks |
| reportlab | direct Python PDF generation | candidate_for_pdf_backend | medium | edge/chrome headless print |
| weasyprint | HTML/CSS to PDF | sandbox_candidate_due_to_weight | high_weight | edge/chrome headless print |
| pillow | image/evidence processing | candidate_for_evidence_helpers | low | text-only evidence |
| pytest | regression test runner | candidate_for_test_gate | low | inline subprocess tests |
| ruff | lint/static quality | future_candidate | low | py_compile + targeted checks |
| playwright | browser screenshots/UI tests | future_heavy_adapter | high_dependency | terminal/pdf evidence |
| duckdb | larger analytics/indexing | future_candidate | medium | sqlite3 stdlib |
| sqlite3 stdlib | lightweight local index | stdlib_allowed | low | json files |
