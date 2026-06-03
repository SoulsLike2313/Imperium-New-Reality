# Runtime Excluded Output Manifest Report

- Excluded/quarantined runtime outputs now require:
  - `sha256`
  - exclusion `reason`
  - `retention_or_quarantine_policy`
  - `private_or_secret_risk`
  - `owner_visible_summary`
  - `quarantine_path` (for quarantine decision)
- Missing hash/policy metadata triggers mandatory cap:
  - `CAP_RUNTIME_EXCLUDED_OUTPUT_WITHOUT_HASH`
- Template added:
  - `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/TEMPLATES/RUNTIME_EXCLUDED_OUTPUT_MANIFEST_TEMPLATE.json`
- Negative fixture NF23 is detected (`true`).
