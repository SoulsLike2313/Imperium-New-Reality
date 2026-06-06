# ADMINISTRATUM EVIDENCE CAPTURE CONTRACT V0.1

## Purpose
Define safe evidence capture for dossier packages.

## Minimum V0.1 evidence kinds
- terminal_transcript
- rich_render_capture
- pdf_page_preview
- browser_screenshot_planned
- file_hash_manifest

## Rules
- Metadata-first evidence by default.
- No private payload capture.
- No desktop screenshot capture unless Owner-authorized.
- Browser capture is optional and non-blocking in V0.1.

## Required outputs
- `machine/evidence_index.json`
- evidence files under `evidence/` tree
- hashes in `SHA256SUMS.txt`
