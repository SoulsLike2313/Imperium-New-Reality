# Evidence Capture Report V0.1

## Implemented in V0.1
- Controlled evidence capture integrated into dossier build flow:
  - `evidence/terminal_captures/dossier_build_terminal_capture.txt`
  - `evidence/logs/dossier_builder.log`
  - `machine/evidence_index.json`
  - `SHA256SUMS.txt` covering captured files
- Evidence index entry kinds supported:
  - `terminal_transcript`
  - `file_hash_manifest`
  - `pdf_page_preview` (when PDF exists)
  - `browser_screenshot_planned` (placeholder when screenshots are not captured)

## Safety constraints
- No desktop screenshot capture performed.
- No browser screenshot capture required.
- No private context content capture; metadata-only policy retained.
- No internet dependency introduced.

## Planned but not implemented in this slice
- Browser screenshot capture command with explicit Owner authorization.
- Rich `.html` or `.svg` capture adapter.
- Playwright-based rendered page captures (non-mandatory and non-core).

## Evidence verdict
- `PASS` for minimal controlled evidence layer.
- `WARN` only if PDF backend is unavailable and fallback markdown is used.

