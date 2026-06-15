# Officio Owner Language Routing

Owner-facing live comments and final Owner comments must be in Russian.

Machine artifacts remain English, UTF-8, no BOM:

- code
- JSON
- schemas
- receipts
- filenames
- canonical repo documents
- task report bundle machine files

If runtime language drift occurs, record it in `servitor_control_chain_receipt.json` as `WARN_RESPONSE_LANGUAGE_DRIFT`. Do not write Russian text into machine/canonical artifacts unless a later Officio localization layer explicitly allows it.
