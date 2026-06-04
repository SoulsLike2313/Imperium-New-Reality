# Officio Owner Language Routing

Owner-facing runtime comments and final Owner comments must be Russian.

Machine artifacts must remain English / UTF-8 / no BOM:

- code;
- schemas;
- JSON receipts;
- canonical markdown contracts;
- filenames;
- report bundle internal machine files.

If a Russian owner-facing summary is produced as a file, it must be explicitly marked as an Officio localization exception and must not be required for machine validation.

If live Owner-facing language drifts to English, record `WARN_RESPONSE_LANGUAGE_DRIFT` in the Servitor control chain receipt. Do not rely on ad-hoc Owner correction as a normal control path.
