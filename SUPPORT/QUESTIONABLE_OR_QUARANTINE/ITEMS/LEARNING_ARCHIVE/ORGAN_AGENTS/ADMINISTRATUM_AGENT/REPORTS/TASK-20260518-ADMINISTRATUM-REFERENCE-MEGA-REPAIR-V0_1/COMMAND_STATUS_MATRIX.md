# Command Status Matrix

| Command | Status | Notes |
|---|---|---|
| `python -m py_compile administratum_agent_runner.py` | PASS | syntax/import check |
| `python -m py_compile administratum_dossier_factory.py` | PASS | syntax/import check |
| `python -m py_compile administratum_v1_core.py` | PASS | syntax/import check |
| `validate-freelance-envelope` valid sample | PASS | valid envelope accepted |
| `validate-freelance-envelope` malformed sample | BLOCKED | malformed envelope blocked |
| `build-freelance-handoff` | PASS | no-PDF handoff package created |
| `schema-regression` | WARN | legacy old PDF dossier detected before fresh build |
| `schema-regression` after fresh dossier | PASS | latest dossier no-PDF validation passed |
| dirty simulation | OWNER_DECISION_REQUIRED | unauthorized dirty path blocked |
| `check-all` | WARN | check_all_report PASS 43/43, command WARN due admitted dirty/internal warnings |
| `recent` | PASS | parsed command/status/warning refs |
| `show-kpd` | WARN | compact scorecard shown, KPD warns on current dirty/warning state |
| `build-dossier` | WARN | new no-PDF dossier built; WARN from admitted dirty/optional legacy reports |
| `verify-dossier --latest` | PASS | `pdf_members: []`, hash OK |
| `verify-dossier` tampered copy | FAIL | hash mismatch detected as expected |
