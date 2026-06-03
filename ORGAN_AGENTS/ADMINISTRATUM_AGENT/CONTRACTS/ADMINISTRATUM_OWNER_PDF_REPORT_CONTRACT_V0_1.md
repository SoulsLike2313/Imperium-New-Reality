# ADMINISTRATUM OWNER PDF REPORT CONTRACT V0.1

## Purpose
Define Owner-facing Russian PDF behavior for dossier packages.

## Language policy
- Owner PDF text: Russian allowed.
- Technical keys, paths, command names, statuses: English.
- Encoding: UTF-8 source and safe rendering backend.

## Required sections
- task header
- starting/ending head
- verdict
- short owner summary
- files changed
- commands/tests run
- new commands and flags
- compact output example
- JSON contract evidence
- continuity maturity verdict
- warnings/limitations/unverified
- why-trust
- ready-to-commit status
- next recommended task

## Truth discipline
- PDF must be rendered from canonical report/receipt content.
- PDF must not replace markdown/json artifacts.

## Backend handling
- If backend unavailable: create Russian fallback markdown and set WARN.
- Do not fake PDF generation.
